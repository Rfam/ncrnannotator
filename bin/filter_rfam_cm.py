#!/usr/bin/env python3
"""
filter_rfam_cm.py — filter Rfam.cm to keep only models whose accession is in
an accession list file.

Logic ported from ensembl-anno (ensembl_anno.py, run_cmsearch_regions, lines 836-850).

Usage:
    filter_rfam_cm.py --rfam_cm Rfam.cm --accessions accessions.txt \
                      --output rfam_filtered.cm
"""

import argparse
import re
import sys


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rfam_cm", required=True,
                        help="Path to full Rfam.cm covariance model file")
    parser.add_argument("--accessions", required=True,
                        help="Path to text file with one RF##### accession per line")
    parser.add_argument("--output", default="rfam_filtered.cm",
                        help="Output path for filtered .cm file (default: rfam_filtered.cm)")
    return parser.parse_args()


def load_accessions(accessions_file):
    """Read accession list, ignoring comment lines starting with '#'."""
    accessions = set()
    with open(accessions_file) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            accessions.add(line)
    return accessions


def filter_rfam_cm(rfam_cm_path, accessions, output_path):
    """Split Rfam.cm on '//' records and write only matching models."""
    rf_accession_re = re.compile(r"\bRF\d{5}\b")

    with open(rfam_cm_path) as fh:
        content = fh.read()

    # Each CM record ends with '//' followed by a newline
    records = content.split("//\n")

    kept = 0
    skipped = 0
    with open(output_path, "w") as out:
        for record in records:
            record = record.strip()
            if not record:
                continue
            match = rf_accession_re.search(record)
            if match and match.group(0) in accessions:
                out.write(record + "\n//\n")
                kept += 1
            else:
                skipped += 1

    print(f"filter_rfam_cm: kept {kept} models, skipped {skipped} models",
          file=sys.stderr)
    if kept == 0:
        print("WARNING: no models were kept — check that accessions match the CM file",
              file=sys.stderr)


def main():
    args = parse_args()
    accessions = load_accessions(args.accessions)
    print(f"filter_rfam_cm: loaded {len(accessions)} accessions", file=sys.stderr)
    filter_rfam_cm(args.rfam_cm, accessions, args.output)


if __name__ == "__main__":
    main()
