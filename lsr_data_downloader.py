#!/usr/bin/env python3
"""
LSR-Data Repo Downloader v1.0
==============================
Downloads all files from stevenbrandon88/LSR-Data (GitHub).
This is the curated primary data repo — cleaner filenames than LSR-NCC-Replication.

USAGE:
  python lsr_data_downloader.py --list                   # list all files by category
  python lsr_data_downloader.py --all                    # download everything
  python lsr_data_downloader.py --category ieg           # IEG World Bank files only
  python lsr_data_downloader.py --category adb           # ADB IED files only
  python lsr_data_downloader.py --category aiddata       # AidData / GCDF files
  python lsr_data_downloader.py --category gcf           # GCF ODL files
  python lsr_data_downloader.py --category indices       # HDI, WB FCV strategy
  python lsr_data_downloader.py --category metadata      # metadata / schema files
  python lsr_data_downloader.py --check                  # verify what is downloaded
  python lsr_data_downloader.py --file FILENAME          # download one specific file

OUTPUT:
  Files saved to ./data/<category>/ by default.
  Set env var LSR_DATA_DIR to override base directory.
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from urllib.parse import quote

# ─── Repo config ──────────────────────────────────────────────────────────────
REPO_USER = "stevenbrandon88"
REPO_NAME = "LSR-Data"
BRANCH    = "main"
RAW_BASE  = f"https://raw.githubusercontent.com/{REPO_USER}/{REPO_NAME}/{BRANCH}"

# Output base dir — override with LSR_DATA_DIR env var
BASE = Path(os.environ.get("LSR_DATA_DIR", "./data"))

CATEGORY_LABELS = {
    "ieg":      "IEG World Bank Project Performance Ratings",
    "adb":      "ADB IED Success Rates Database",
    "aiddata":  "AidData / GCDF Chinese Development Finance",
    "gcf":      "GCF ODL Open Data Library Exports",
    "indices":  "Development Indices / Strategies",
    "metadata": "Metadata / Schema Files",
}

# ─── File catalogue ───────────────────────────────────────────────────────────
# Format: (category, remote_filename, local_filename, description)
# remote_filename = exact name in repo (URL-encoded automatically)
# local_filename  = what to save as locally (clean name)

FILES = [

    # ── IEG World Bank ─────────────────────────────────────────────────────────
    ("ieg",
     "IEG_ICRR_PPAR_Ratings_2025-12-15.xlsx",
     "IEG_ICRR_PPAR_Ratings_20251215.xlsx",
     "IEG ICRR+PPAR Ratings Dec 2025 — primary evaluation dataset"),

    ("ieg",
     "ieg_world_bank_project_performance_ratings_01-17-2026.csv",
     "ieg_world_bank_project_performance_ratings_01172026.csv",
     "IEG CSV n=12,328 — used in replication scripts"),

    ("ieg",
     "IEG_CLRV_Ratings_30_06_2025.xlsx",
     "IEG_CLRV_Ratings_30062025.xlsx",
     "IEG Country-Level Results & Values ratings"),

    ("ieg",
     "IEG_ICRR-PPAR_Lessons_2025-09-03.xlsx",
     "IEG_ICRR_PPAR_Lessons_20250903.xlsx",
     "IEG Lessons dataset (separate from Ratings)"),

    ("ieg",
     "IEG_data_for_validator.csv",
     "IEG_data_for_validator.csv",
     "IEG data formatted for validator"),

    ("ieg",
     "IEG_validator_ready.csv",
     "IEG_validator_ready.csv",
     "IEG validator-ready dataset"),

    # ── ADB IED Success Rates ──────────────────────────────────────────────────
    ("adb",
     "aer-2024-success-rates-database.xlsx",
     "aer2024_successratedatabase.xlsx",
     "ADB IED Success Rates Database 2024"),

    ("adb",
     "aer-2024-success-rates-database (2).xlsx",
     "aer2024_successratedatabase_v2.xlsx",
     "ADB IED Success Rates Database 2024 (v2)"),

    ("adb",
     "aer-2023_success-rate-database.xlsx",
     "aer2023_successratedatabase.xlsx",
     "ADB IED Success Rates Database 2023"),

    ("adb",
     "aer-2023_success-rate-database (1).xlsx",
     "aer2023_successratedatabase_v2.xlsx",
     "ADB IED Success Rates Database 2023 (v2)"),

    ("adb",
     "AER-2022-Success-Database (1).xlsx",
     "aer2022_successratedatabase.xlsx",
     "ADB IED Success Rates Database 2022"),

    ("adb",
     "AER-2021-Success-Database (1).xlsx",
     "aer2021_successratedatabase.xlsx",
     "ADB IED Success Rates Database 2021"),

    ("adb",
     "AER-2020-Success-Rates (1).xlsx",
     "aer2020_successratedatabase.xlsx",
     "ADB IED Success Rates Database 2020"),

    ("adb",
     "adb-success-rates-database-2018 (1).xlsx",
     "adb_success_rates_2018.xlsx",
     "ADB IED Success Rates Database 2018 (XLSX)"),

    ("adb",
     "adb-success-rates-database-2018 (1).csv",
     "adb_success_rates_2018.csv",
     "ADB IED Success Rates Database 2018 (CSV)"),

    ("adb",
     "adb-sov-projects-20250109 - Copy.csv",
     "adb_sov_projects_20250109.csv",
     "ADB sovereign projects Jan 2025"),

    # ── AidData / GCDF ─────────────────────────────────────────────────────────
    ("aiddata",
     "AidDatasGlobalChineseDevelopmentFinanceDataset_v2.0.xlsx",
     "AidDatasGlobalChineseDevelopmentFinanceDataset_v2_0.xlsx",
     "AidData Global Chinese Development Finance v2.0 — OR=149.9 cross-institutional"),

    ("aiddata",
     "AidData_TUFF_methodology_2_0.pdf",
     "AidData_TUFF_methodology_2_0.pdf",
     "AidData TUFF Methodology v2.0 (PDF)"),

    ("aiddata",
     "Field Definitions_GCDF 3.0.pdf",
     "Field_Definitions_GCDF_3_0.pdf",
     "GCDF 3.0 Field Definitions (PDF)"),

    ("aiddata",
     "GCDF3.0 ADM Files README.pdf",
     "GCDF3_0_ADM_Files_README.pdf",
     "GCDF 3.0 ADM Files README (PDF)"),

    ("aiddata",
     "GCDF_3.0_ADM1_Locations.csv",
     "GCDF_3_0_ADM1_Locations.csv",
     "GCDF 3.0 ADM1 (province-level) location data"),

    ("aiddata",
     "GCDF_3.0_ADM2_Locations.csv",
     "GCDF_3_0_ADM2_Locations.csv",
     "GCDF 3.0 ADM2 (district-level) location data"),

    # ── GCF ODL ────────────────────────────────────────────────────────────────
    ("gcf",
     "ODL-Export-projects-1769566264768.xlsx",
     "gcf_projects_odl_v1.xlsx",
     "GCF ODL funded projects export (v1)"),

    ("gcf",
     "ODL-Export-projects-1769822251024.xlsx",
     "gcf_projects_odl_v2.xlsx",
     "GCF ODL funded projects export (v2)"),

    ("gcf",
     "ODL-Export-readiness-1769736586645.xlsx",
     "gcf_readiness_odl_v1.xlsx",
     "GCF ODL readiness programme export (v1)"),

    ("gcf",
     "ODL-Export-readiness-1769822228417.xlsx",
     "gcf_readiness_odl_v2.xlsx",
     "GCF ODL readiness programme export (v2)"),

    # ── Development Indices / Strategies ───────────────────────────────────────
    ("indices",
     "human-development-index.csv",
     "human_development_index.csv",
     "UNDP Human Development Index"),

    ("indices",
     "World Bank Group Strategy for Fragility, Conflict, and Violence 2020–2025 (Vol. 1 of 2).xlsx",
     "WB_FCV_Strategy_2020_2025_Vol1.xlsx",
     "World Bank FCV Strategy 2020-2025 (Vol 1)"),

    # ── Metadata ────────────────────────────────────────────────────────────────
    ("metadata",
     "metadata_eds08_ieg_project_performance_ratings_03-11-2026.json",
     "metadata_ieg_project_performance_ratings_20260311.json",
     "IEG dataset metadata / schema (March 2026)"),
]

# ─── Download engine ──────────────────────────────────────────────────────────

def url_for(remote_filename: str) -> str:
    encoded = quote(remote_filename, safe="")
    return f"{RAW_BASE}/{encoded}"


def dest_for(category: str, local_filename: str) -> Path:
    return BASE / category / local_filename


def download_file(url: str, dest: Path) -> str:
    """Returns 'ok', 'exists', '404', or 'failed'."""
    if dest.exists() and dest.stat().st_size > 0:
        return "exists"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(url, timeout=60, stream=True)
        if r.status_code == 404:
            return "404"
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
        size_mb = dest.stat().st_size / 1_048_576
        print(f"    ✓ {size_mb:.1f} MB  →  {dest}")
        return "ok"
    except Exception as e:
        print(f"    ✗ FAILED: {e}")
        return "failed"


def run_download(entries):
    ok = exists = f404 = failed = 0
    for cat, remote, local, desc in entries:
        dest = dest_for(cat, local)
        url  = url_for(remote)
        if dest.exists() and dest.stat().st_size > 0:
            print(f"  [EXISTS] {local}")
            exists += 1
            continue
        print(f"  ↓ {desc}")
        print(f"    {url}")
        result = download_file(url, dest)
        if result == "ok":       ok += 1
        elif result == "exists": exists += 1
        elif result == "404":
            print(f"    ⚠ 404 — not found in repo: {remote}")
            f404 += 1
        else:
            failed += 1
        time.sleep(0.05)
    print(f"\n  Results: {ok} downloaded, {exists} already existed, {f404} not found (404), {failed} failed")
    return ok, exists, f404, failed


# ─── CLI ──────────────────────────────────────────────────────────────────────

def cmd_list(cat_filter=None):
    by_cat = {}
    for cat, remote, local, desc in FILES:
        by_cat.setdefault(cat, []).append((remote, local, desc))

    print()
    print("=" * 70)
    print(f"LSR-DATA REPO — github.com/{REPO_USER}/{REPO_NAME}")
    print("=" * 70)
    cats = [cat_filter] if cat_filter else sorted(by_cat.keys())
    total = 0
    for cat in cats:
        entries = by_cat.get(cat, [])
        if not entries:
            print(f"\n  No files found for category: {cat}")
            continue
        label = CATEGORY_LABELS.get(cat, cat.upper())
        print(f"\n  [{cat.upper()}] — {label} ({len(entries)} files)")
        for remote, local, desc in entries:
            print(f"    {local:<55} {desc[:50]}")
        total += len(entries)
    print(f"\n  TOTAL: {total} files")
    print(f"  REPO:  {RAW_BASE}")
    print()
    print("  COMMANDS:")
    for cat in sorted(by_cat.keys()):
        n = len(by_cat[cat])
        print(f"    python lsr_data_downloader.py --category {cat:<12} # {n} files")
    print(f"    python lsr_data_downloader.py --all                    # everything")
    print(f"    python lsr_data_downloader.py --check                  # verify")
    print()


def cmd_check():
    by_cat = {}
    for cat, remote, local, desc in FILES:
        by_cat.setdefault(cat, []).append((cat, remote, local, desc))

    print("\n  CHECK — scanning downloaded files...")
    total = missing = 0
    for cat in sorted(by_cat.keys()):
        found = 0
        not_found = []
        for c, remote, local, desc in by_cat[cat]:
            dest = dest_for(c, local)
            if dest.exists() and dest.stat().st_size > 0:
                found += 1
            else:
                not_found.append(local)
        label = CATEGORY_LABELS.get(cat, cat.upper())
        total += found + len(not_found)
        missing += len(not_found)
        status = "✓" if not not_found else "✗"
        print(f"  {status} [{cat.upper()}] {found}/{found+len(not_found)} — {label}")
        for fn in not_found:
            print(f"      MISSING: {fn}")
    print(f"\n  TOTAL: {total-missing}/{total} files present ({missing} missing)")
    if missing == 0:
        print("  ✅ All files downloaded.")
    else:
        print("  Run --all to fetch missing files.")


def main():
    parser = argparse.ArgumentParser(
        description=f"Download data from {REPO_USER}/{REPO_NAME}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--list",     action="store_true", help="List all files by category")
    parser.add_argument("--all",      action="store_true", help="Download all files")
    parser.add_argument("--category", type=str,            help="Download specific category")
    parser.add_argument("--file",     type=str,            help="Download one file by local name")
    parser.add_argument("--check",    action="store_true", help="Check what is already downloaded")
    parser.add_argument("--outdir",   type=str,            help="Override output directory")
    args = parser.parse_args()

    global BASE
    if args.outdir:
        BASE = Path(args.outdir)

    if args.list:
        cmd_list(args.category)
        return

    if args.check:
        cmd_check()
        return

    if args.file:
        matches = [e for e in FILES if e[2] == args.file or e[1] == args.file]
        if not matches:
            print(f"  File not found in catalogue: {args.file}")
            sys.exit(1)
        run_download(matches)
        return

    if args.category:
        valid = set(e[0] for e in FILES)
        if args.category not in valid:
            print(f"  Unknown category: {args.category}")
            print(f"  Valid: {', '.join(sorted(valid))}")
            sys.exit(1)
        entries = [e for e in FILES if e[0] == args.category]
        label = CATEGORY_LABELS.get(args.category, args.category.upper())
        print("=" * 60)
        print(f"CATEGORY: {label} ({len(entries)} files)")
        print("=" * 60)
        run_download(entries)
        return

    if args.all:
        cats = sorted(set(e[0] for e in FILES))
        print(f"\nDownloading all {len(FILES)} files across {len(cats)} categories")
        print(f"Output: {BASE.resolve()}")
        total_ok = total_exists = total_404 = total_fail = 0
        for cat in cats:
            entries = [e for e in FILES if e[0] == cat]
            label = CATEGORY_LABELS.get(cat, cat.upper())
            print(f"\n{'='*60}")
            print(f"CATEGORY: {label} ({len(entries)} files)")
            print("="*60)
            ok, ex, f4, fa = run_download(entries)
            total_ok += ok; total_exists += ex; total_404 += f4; total_fail += fa
        print(f"\n{'='*60}")
        print(f"Complete. {total_ok} downloaded, {total_exists} existed, {total_404} not found, {total_fail} failed")
        print("Run --check to verify.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
