#!/usr/bin/env python3
"""Independent verifier for SigningLab forecast commitments.

Standard library only. No network. No dependencies. Python 3.8+.

    python verify.py            # run every check
    python verify.py files      # file hashes match manifest.json
    python verify.py chain      # batches form an unbroken chain
    python verify.py union      # counts and union hash match the cumulative manifest
    python verify.py sample --beacon <block_hash>
                                # reproduce which commitments a beacon selects
    python verify.py reveal --reveals <csv> [--beacon <block_hash>]
                                # recompute sha256 of revealed payload+salt

Exit code 0 means every requested check passed.
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FAIL = []


def ok(msg):
    print("  OK    " + msg)


def bad(msg):
    print("  FAIL  " + msg)
    FAIL.append(msg)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def manifest():
    return load("manifest.json")


def cumulative():
    return load(manifest()["cumulative_manifest"])


def check_files():
    print("files: every published artifact hashes to the value recorded in manifest.json")
    for entry in manifest()["files"]:
        path = ROOT / entry["path"]
        if not path.exists():
            bad("%s is missing" % entry["path"])
            continue
        got = sha256_file(path)
        if got == entry["sha256"]:
            ok("%s  %s" % (entry["sha256"][:16] + "...", entry["path"]))
        else:
            bad("%s: expected %s, got %s" % (entry["path"], entry["sha256"], got))


def check_chain():
    print("chain: each batch names its predecessor by hash, so no batch can be swapped later")
    batches = cumulative()["batches"]
    prev = None
    for b in batches:
        path = ROOT / b["file"]
        got = sha256_file(path)
        if got != b["sha256"]:
            bad("batch %s: file hash %s does not match manifest %s" % (b["batch_id"], got, b["sha256"]))
        if prev is None:
            if b.get("prev_sha256"):
                bad("batch %s is the first batch but declares a predecessor" % b["batch_id"])
            else:
                ok("batch %s is the chain root (%d commitments)" % (b["batch_id"], b["n_commitments"]))
        else:
            if b.get("prev_sha256") == prev["sha256"]:
                ok("batch %s links to batch %s (%d commitments)" % (b["batch_id"], prev["batch_id"], b["n_commitments"]))
            else:
                bad("batch %s declares prev_sha256 %s but batch %s hashes to %s"
                    % (b["batch_id"], b.get("prev_sha256"), prev["batch_id"], prev["sha256"]))
        prev = b


def union_hashes():
    hashes = []
    for b in cumulative()["batches"]:
        hashes.extend(h.lower() for h in load(b["file"])["commitments"])
    return hashes


def check_union():
    print("union: the sampling universe is exactly the published batches, with nothing added or dropped")
    cum = cumulative()
    hashes = union_hashes()
    uniq = sorted(set(hashes))
    if len(hashes) == cum["n_commitments_total"]:
        ok("%d commitments across %d batches" % (len(hashes), cum["n_batches"]))
    else:
        bad("counted %d commitments, manifest declares %d" % (len(hashes), cum["n_commitments_total"]))
    if len(uniq) == cum["n_commitments_unique"]:
        ok("%d unique commitments (no batch overlap)" % len(uniq))
    else:
        bad("counted %d unique commitments, manifest declares %d" % (len(uniq), cum["n_commitments_unique"]))
    got = hashlib.sha256(("".join(u + "\n" for u in uniq)).encode("utf-8")).hexdigest()
    if got == cum["union_sha256"]:
        ok("union hash %s" % got)
    else:
        bad("union hash: expected %s, got %s" % (cum["union_sha256"], got))


def select(beacon, uniq, k=None):
    scored = sorted((hashlib.sha256(("SL-SAMPLE-v1|%s|%s" % (beacon, h)).encode("utf-8")).hexdigest(), h)
                    for h in uniq)
    if k is None:
        k = min(100, len(uniq))
    return [h for _, h in scored[:k]]


def check_sample(beacon):
    print("sample: the beacon alone decides which commitments get revealed")
    uniq = sorted(set(union_hashes()))
    chosen = select(beacon, uniq)
    ok("beacon %s selects %d of %d commitments" % (beacon, len(chosen), len(uniq)))
    for h in chosen:
        print("        " + h)


PAYLOAD_COLS = ["league", "season", "player_key", "club_key", "verdict", "generation"]


def payload_of(row):
    """A revealed row carries either the payload string or its six fields."""
    if row.get("payload"):
        return row["payload"]
    missing = [c for c in PAYLOAD_COLS if not row.get(c)]
    if missing:
        return None
    return "|".join(row[c] for c in PAYLOAD_COLS)


def recompute(row):
    payload = payload_of(row)
    if payload is None:
        return None
    salt = row.get("salt") or row.get("salt_hex") or ""
    return hashlib.sha256((payload + "|" + salt).encode("utf-8")).hexdigest()


def check_reveal(reveals, beacon):
    print("reveal: each revealed payload and salt rebuilds its published commitment hash")
    uniq = set(union_hashes())
    with open(reveals, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        bad("%s has no rows" % reveals)
        return
    if payload_of(rows[0]) is None:
        bad("%s needs a 'payload' column, or the columns %s"
            % (reveals, ", ".join(PAYLOAD_COLS)))
        return
    recomputed = []
    for i, r in enumerate(rows, 1):
        got = recompute(r)
        recomputed.append(got)
        label = (payload_of(r) or "").split("|")
        label = label[2] if len(label) > 2 else "row %d" % i
        declared = (r.get("commitment") or "").lower()
        if declared and got != declared:
            bad("row %d: recomputed %s, row declares %s" % (i, got, declared))
        elif got not in uniq:
            bad("row %d: recomputed %s is not among the published commitments" % (i, got))
        else:
            ok("row %d  %s  %s" % (i, got[:16] + "...", label))
    if beacon:
        expected = set(select(beacon, sorted(uniq), k=len(rows)))
        if set(recomputed) == expected:
            ok("the revealed set is exactly what beacon %s selects" % beacon)
        else:
            bad("revealed set does not match the beacon selection (%d unexpected, %d missing)"
                % (len(set(recomputed) - expected), len(expected - set(recomputed))))


def main():
    ap = argparse.ArgumentParser(description="Verify SigningLab forecast commitments.")
    ap.add_argument("check", nargs="?", default="all",
                    choices=["all", "files", "chain", "union", "sample", "reveal"])
    ap.add_argument("--beacon", help="Bitcoin block hash used as the public beacon")
    ap.add_argument("--reveals", help="CSV of revealed entries")
    args = ap.parse_args()

    if args.check in ("all", "files"):
        check_files()
    if args.check in ("all", "chain"):
        check_chain()
    if args.check in ("all", "union"):
        check_union()
    if args.check == "sample":
        if not args.beacon:
            ap.error("sample needs --beacon")
        check_sample(args.beacon)
    if args.check == "reveal":
        if not args.reveals:
            ap.error("reveal needs --reveals")
        check_reveal(args.reveals, args.beacon)

    print()
    if FAIL:
        print("%d check(s) FAILED" % len(FAIL))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
