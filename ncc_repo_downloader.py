#!/usr/bin/env python3
"""
NCC Repo Downloader v1.0
=========================
Downloads all datasets from stevenbrandon88/LSR-NCC-Replication (GitHub).
Much faster and more reliable than hitting original data portals.

USAGE:
  python ncc_repo_downloader.py --list              # list all files by category
  python ncc_repo_downloader.py --all               # download everything
  python ncc_repo_downloader.py --category ieg      # download IEG files only
  python ncc_repo_downloader.py --category adb      # download ADB files only
  python ncc_repo_downloader.py --category aiddata  # download AidData files
  python ncc_repo_downloader.py --category gcf      # download GCF files
  python ncc_repo_downloader.py --category imf      # download IMF files
  python ncc_repo_downloader.py --category oecd     # download OECD files
  python ncc_repo_downloader.py --category vdem     # download V-Dem files
  python ncc_repo_downloader.py --category fsi      # download FSI/conflict files
  python ncc_repo_downloader.py --category fao      # download FAOSTAT files
  python ncc_repo_downloader.py --category seshat   # download Seshat/historical
  python ncc_repo_downloader.py --category scripts  # download Python scripts
  python ncc_repo_downloader.py --check             # check what's already downloaded
  python ncc_repo_downloader.py --file FILENAME     # download one specific file

OUTPUT:
  Files saved to ./data/<category>/ by default.
  Set env var NCC_DATA_DIR to override.
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from urllib.parse import quote

# ─── Repo config ──────────────────────────────────────────────────────────────
REPO_USER   = "stevenbrandon88"
REPO_NAME   = "LSR-NCC-Replication"
BRANCH      = "main"
RAW_BASE    = f"https://raw.githubusercontent.com/{REPO_USER}/{REPO_NAME}/{BRANCH}"
GITHUB_BASE = f"https://github.com/{REPO_USER}/{REPO_NAME}/raw/refs/heads/{BRANCH}"

# Output base dir — override with NCC_DATA_DIR env var
BASE = Path(os.environ.get("NCC_DATA_DIR", "./data"))

# ─── File catalogue ───────────────────────────────────────────────────────────
# Format: (category, local_subdir, remote_filename, local_filename, description)
FILES = [

    # ── IEG World Bank Ratings ─────────────────────────────────────────────────
    ("ieg", "ieg", "IEG_ICRR_PPAR_Ratings_2025-12-15.xlsx",
        "IEG_ICRR_PPAR_Ratings_20251215.xlsx",
        "IEG ICRR+PPAR Ratings Dec 2025 — primary evaluation dataset"),

    ("ieg", "ieg", "ieg_world_bank_project_performance_ratings_01-17-2026.csv",
        "ieg_world_bank_project_performance_ratings_01172026.csv",
        "IEG CSV n=12,328 — used in replication scripts"),

    ("ieg", "ieg", "IEG_CLRV_Ratings_30_06_2025.xlsx",
        "IEG_CLRV_Ratings_30062025.xlsx",
        "IEG Country-Level Results & Values ratings"),

    ("ieg", "ieg", "IEG_ICRR-PPAR_Lessons_2025-09-03.xlsx",
        "IEG_ICRR_PPAR_Lessons_20250903.xlsx",
        "IEG Lessons dataset (separate from Ratings)"),

    ("ieg", "ieg", "IEG_data_for_validator.csv",
        "IEG_data_for_validator.csv",
        "IEG data formatted for validator"),

    ("ieg", "ieg", "IEG_validator_ready.csv",
        "IEG_validator_ready.csv",
        "IEG validator-ready dataset"),

    ("ieg", "ieg", "forest_plot_data.csv",
        "forest_plot_data.csv",
        "Forest plot data for IEG meta-analysis"),

    # ── ADB Success Rates ──────────────────────────────────────────────────────
    ("adb", "adb", "aer-2024-success-rates-database.xlsx",
        "aer2024_successratedatabase.xlsx",
        "ADB IED Success Rates Database 2024"),

    ("adb", "adb", "ce_aer-2024_SOV_Success_Rate_Database.xlsx",
        "ce_aer2024_sov_success_rate_database.xlsx",
        "ADB sovereign-only success rates 2024"),

    ("adb", "adb", "aer-2023_success-rate-database.xlsx",
        "aer2023_successratedatabase.xlsx",
        "ADB IED Success Rates Database 2023"),

    ("adb", "adb", "AER-2022-Success-Database.xlsx",
        "aer2022_successratedatabase.xlsx",
        "ADB IED Success Rates Database 2022"),

    ("adb", "adb", "AER-2021-Success-Database.xlsx",
        "aer2021_successratedatabase.xlsx",
        "ADB IED Success Rates Database 2021"),

    ("adb", "adb", "AER-2020-Success-Rates.xlsx",
        "aer2020_successratedatabase.xlsx",
        "ADB IED Success Rates Database 2020"),

    ("adb", "adb", "adb-success-rates-database-2018.xlsx",
        "adb_success_rates_2018.xlsx",
        "ADB IED Success Rates Database 2018"),

    ("adb", "adb", "adb-sov-projects-20250109.csv",
        "adb_sov_projects_20250109.csv",
        "ADB sovereign projects Jan 2025"),

    # ── AidData Chinese Development Finance ───────────────────────────────────
    ("aiddata", "aiddata", "AidDatasGlobalChineseDevelopmentFinanceDataset_v2.0.xlsx",
        "AidDatasGlobalChineseDevelopmentFinanceDataset_v2_0.xlsx",
        "AidData Global Chinese Development Finance v2.0 — OR=149.9 in cross-institutional"),

    ("aiddata", "aiddata", "AidDatasGlobalChineseDevelopmentFinanceDataset_v3.0.xlsx",
        "AidDatasGlobalChineseDevelopmentFinanceDataset_v3_0.xlsx",
        "AidData Global Chinese Development Finance v3.0 — latest version"),

    # ── GCF Open Data Library ─────────────────────────────────────────────────
    ("gcf", "gcf", "ODL-Export-projects-1769566264768.xlsx",
        "gcf_projects_odl_v1.xlsx",
        "GCF ODL funded projects export"),

    ("gcf", "gcf", "ODL-Export-projects-1769822251024.xlsx",
        "gcf_projects_odl_v2.xlsx",
        "GCF ODL funded projects export v2"),

    ("gcf", "gcf", "ODL-Export-readiness-1769822228417.xlsx",
        "gcf_readiness_odl.xlsx",
        "GCF ODL readiness programme export"),

    # ── IMF Datasets ───────────────────────────────────────────────────────────
    ("imf", "imf", "dataset_2026-02-13T05_46_56.200222172Z_DEFAULT_INTEGRATION_IMF.STA_MFS_MA_10.0.1.csv",
        "imf_mfs_ma_20260213.csv",
        "IMF Monetary and Financial Statistics — Monthly"),

    ("imf", "imf", "imf-weo-main.zip",
        "imf_weo_main.zip",
        "IMF World Economic Outlook dataset (zipped)"),

    ("imf", "imf", "weoapr2025-sdmxdata.zip",
        "imf_weo_apr2025_sdmx.zip",
        "IMF WEO April 2025 SDMX data"),

    ("imf", "imf", "food_price_indices_data_jan3.xlsx",
        "imf_food_price_indices.xlsx",
        "IMF food price indices"),

    # ── OECD Datasets ──────────────────────────────────────────────────────────
    ("oecd", "oecd", "OECD.ELS.SAE,DSD_POPULATION@DF_POP_HIST,,filtered,2026-02-02 07-39-42.xlsx",
        "oecd_population_hist_20260202.xlsx",
        "OECD Historical Population (ELS.SAE DSD_POPULATION@DF_POP_HIST)"),

    ("oecd", "oecd", "OECD.ELS.SPD,DSD_SOCX_AGG@DF_SOCX_AGG,1.0+.A..PT_B1GQ.ES10._T._T..csv",
        "oecd_socx_pct_gdp.csv",
        "OECD Social Expenditure % GDP (SOCX aggregated)"),

    ("oecd", "oecd", "OECD.DCD.FSD_DSD_CRS@DF_CRS_1_5.csv",
        "oecd_dac_crs.csv",
        "OECD DAC Creditor Reporting System — all aid flows"),

    # ── WGI / Governance ──────────────────────────────────────────────────────
    ("wgi", "wgi", "wgidataset_with_sourcedata-2025.xlsx",
        "wgi_dataset_with_sourcedata_2025.xlsx",
        "World Governance Indicators 2025 with source data"),

    # ── V-Dem Democracy ───────────────────────────────────────────────────────
    ("vdem", "vdem", "V-Dem-CY-FullOthers-v15_csv (1).zip",
        "vdem_v15_full.zip",
        "V-Dem Country-Year Full Dataset v15"),

    ("vdem", "vdem", "vdem_trimmed.csv",
        "vdem_trimmed.csv",
        "V-Dem trimmed working dataset"),

    # ── FSI / Conflict / Fragility ────────────────────────────────────────────
    ("fsi", "fsi", "FSI-2023-DOWNLOAD.xlsx",
        "fsi_2023.xlsx",
        "Fragile States Index 2023 (Fund for Peace)"),

    ("fsi", "fsi", "fsi-2022-download.xlsx",
        "fsi_2022.xlsx",
        "Fragile States Index 2022"),

    ("fsi", "fsi", "fsi-2021.xlsx",
        "fsi_2021.xlsx",
        "Fragile States Index 2021"),

    ("fsi", "fsi", "ACLED_Conflict_Index_2025.xlsx",
        "acled_conflict_index_2025.xlsx",
        "ACLED Armed Conflict Location & Event Index 2025"),

    ("fsi", "fsi", "CrisisConsequencesData_NavigatingPolycrisis_2023.03.csv",
        "crisis_consequences_polycrisis_2023.csv",
        "Crisis Consequences Data — Navigating Polycrisis 2023 (169 crises)"),

    ("fsi", "fsi", "IDA20 Special Theme _ Fragility, Conflict and Violence.xlsx",
        "ida20_fcv_special_theme.xlsx",
        "WB IDA20 Special Theme — Fragility Conflict Violence"),

    ("fsi", "fsi", "covid-fci-data.xlsx",
        "covid_fci_data.xlsx",
        "COVID Fragile/Conflict/Impacted country data"),

    # ── FAO Food & Agriculture ─────────────────────────────────────────────────
    # Note: FAOSTAT_A-S_E and FAOSTAT_T-Z_E are folders — handled via folder download below
    # Individual files within those folders need separate entries if needed

    # ── Historical / Seshat ────────────────────────────────────────────────────
    ("seshat", "seshat", "MASTER_Seshat_Test_Register.csv",
        "seshat_test_register.csv",
        "Seshat Axial Age test register — 428 observations, 10,000-year institutional patterns"),

    ("seshat", "seshat", "axial_dataset.05.2018.csv",
        "axial_dataset_2018.csv",
        "Seshat axial dataset May 2018"),

    ("seshat", "seshat", "agri_dataset.07.2020.csv",
        "agri_dataset_2020.csv",
        "Agricultural dataset July 2020"),

    ("seshat", "seshat", "mr_dataset.04.2021.csv",
        "mr_dataset_2021.csv",
        "Moralising religions dataset April 2021"),

    ("seshat", "seshat", "sc_dataset.12.2017.xlsx",
        "sc_dataset_2017.xlsx",
        "Social complexity dataset Dec 2017"),

    ("seshat", "seshat", "social_complexity_data_20260213_053931.csv",
        "social_complexity_2026.csv",
        "Social complexity data Feb 2026"),

    ("seshat", "seshat", "cliopatria.ipynb",
        "cliopatria.ipynb",
        "Cliopatria analysis notebook"),

    # ── HDI / GDP / Population indices ────────────────────────────────────────
    ("indices", "indices", "human-development-index.csv",
        "human_development_index.csv",
        "UNDP Human Development Index"),

    ("indices", "indices", "global-living-planet-index.csv",
        "global_living_planet_index.csv",
        "WWF Global Living Planet Index"),

    # ── LSR-specific datasets ──────────────────────────────────────────────────
    ("lsr", "lsr", "LSR_AI_Governance_Dataset.xlsx",
        "lsr_ai_governance_dataset.xlsx",
        "LSR AI Governance Dataset — extension analysis"),

    ("lsr", "lsr", "chart.csv",
        "chart.csv",
        "Chart data"),

    # ── Scripts ────────────────────────────────────────────────────────────────
    ("scripts", "scripts", "paper1_replication_v3.py",
        "paper1_replication_v3.py",
        "Primary replication script — auto-verifies OR=27.8"),

    ("scripts", "scripts", "convert_data.py",
        "convert_data.py",
        "Data conversion utilities"),

    ("scripts", "scripts", "map_functions.py",
        "map_functions.py",
        "Map/visualisation functions"),

]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_dirs():
    subdirs = set(f[1] for f in FILES)
    for s in subdirs:
        (BASE / s).mkdir(parents=True, exist_ok=True)
    (BASE / "logs").mkdir(exist_ok=True)


def raw_url(remote_filename):
    """Build raw GitHub URL for a file, handling spaces and special chars."""
    encoded = quote(remote_filename)
    return f"{RAW_BASE}/{encoded}"


def download_file(remote_filename, local_path, desc=""):
    local_path = Path(local_path)
    if local_path.exists():
        size_mb = local_path.stat().st_size / 1024 / 1024
        print(f"  [EXISTS] {local_path.name} ({size_mb:.1f} MB)")
        return True

    url = raw_url(remote_filename)
    print(f"  ↓ {desc or local_path.name}")
    print(f"    {url}")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (NCC-Research/Brandon2026)"}
        r = requests.get(url, stream=True, timeout=120, headers=headers)

        if r.status_code == 404:
            # Try alternate URL format
            alt_url = f"{GITHUB_BASE}/{quote(remote_filename)}"
            r = requests.get(alt_url, stream=True, timeout=120, headers=headers)

        r.raise_for_status()

        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r    {pct:.0f}% ({downloaded/1024/1024:.1f} MB)", end="", flush=True)

        size_mb = downloaded / 1024 / 1024
        print(f"\r    ✓ {size_mb:.1f} MB saved to {local_path}        ")
        return True

    except requests.HTTPError as e:
        print(f"\n    ✗ HTTP {e.response.status_code} — file may not exist at this path")
        return False
    except Exception as e:
        print(f"\n    ✗ Error: {e}")
        return False


def get_files_by_category(category):
    return [(cat, subdir, remote, local, desc)
            for cat, subdir, remote, local, desc in FILES
            if cat == category]


def download_category(category):
    items = get_files_by_category(category)
    if not items:
        print(f"Unknown category: {category}")
        print(f"Available: {sorted(set(f[0] for f in FILES))}")
        return
    print(f"\n{'='*60}")
    print(f"CATEGORY: {category.upper()} ({len(items)} files)")
    print(f"{'='*60}")
    ok = fail = skip = 0
    for cat, subdir, remote, local, desc in items:
        dest = BASE / subdir / local
        if dest.exists():
            skip += 1
            print(f"  [EXISTS] {local}")
            continue
        if download_file(remote, dest, desc):
            ok += 1
        else:
            fail += 1
        time.sleep(0.3)
    print(f"\n  Results: {ok} downloaded, {skip} already existed, {fail} failed")


def download_all():
    categories = sorted(set(f[0] for f in FILES))
    total = len(FILES)
    print(f"\nDownloading all {total} files across {len(categories)} categories")
    print(f"Output: {BASE.resolve()}\n")
    for cat in categories:
        download_category(cat)
    print(f"\n{'='*60}")
    print(f"Complete. Run --check to verify.")


def download_one(filename):
    """Download a single file by its local or remote name."""
    matches = [f for f in FILES
               if f[2].lower() == filename.lower() or f[3].lower() == filename.lower()]
    if not matches:
        print(f"File not found in catalogue: {filename}")
        print("Use --list to see all available files.")
        return
    for cat, subdir, remote, local, desc in matches:
        dest = BASE / subdir / local
        download_file(remote, dest, desc)


def check_existing():
    print(f"\n{'='*60}")
    print(f"FILE STATUS — {BASE.resolve()}")
    print(f"{'='*60}")
    by_cat = {}
    for cat, subdir, remote, local, desc in FILES:
        dest = BASE / subdir / local
        exists = dest.exists()
        size = dest.stat().st_size / 1024 / 1024 if exists else 0
        by_cat.setdefault(cat, []).append((local, exists, size, desc))

    total_found = 0
    total_size = 0
    for cat in sorted(by_cat):
        items = by_cat[cat]
        found = sum(1 for _, e, _, _ in items if e)
        print(f"\n  {cat.upper()} ({found}/{len(items)})")
        for local, exists, size, desc in items:
            if exists:
                print(f"    ✓ {local:55s} {size:6.1f} MB")
                total_found += 1
                total_size += size
            else:
                print(f"    ✗ {local}")

    print(f"\n  TOTAL: {total_found}/{len(FILES)} files present")
    print(f"  SIZE:  {total_size:.1f} MB ({total_size/1024:.2f} GB)")
    missing = [f[3] for f in FILES if not (BASE / f[1] / f[3]).exists()]
    if missing:
        print(f"\n  TO DOWNLOAD MISSING:")
        print(f"    python ncc_repo_downloader.py --all")


def list_files():
    print(f"\n{'='*70}")
    print(f"NCC REPO FILES — github.com/{REPO_USER}/{REPO_NAME}")
    print(f"{'='*70}")
    by_cat = {}
    for cat, subdir, remote, local, desc in FILES:
        by_cat.setdefault(cat, []).append((remote, local, desc))

    for cat in sorted(by_cat):
        items = by_cat[cat]
        print(f"\n  [{cat.upper()}] — {len(items)} files")
        for remote, local, desc in items:
            print(f"    {local:55s} {desc}")

    print(f"\n  TOTAL: {len(FILES)} files")
    print(f"  REPO:  {RAW_BASE}")
    print(f"\n  COMMANDS:")
    cats = sorted(set(f[0] for f in FILES))
    for cat in cats:
        n = len(get_files_by_category(cat))
        print(f"    python ncc_repo_downloader.py --category {cat:12s} # {n} files")
    print(f"    python ncc_repo_downloader.py --all                    # everything")
    print(f"    python ncc_repo_downloader.py --check                  # verify")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Download all NCC research data from stevenbrandon88/LSR-NCC-Replication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--list",     action="store_true", help="List all files by category")
    parser.add_argument("--all",      action="store_true", help="Download everything")
    parser.add_argument("--check",    action="store_true", help="Check existing files")
    parser.add_argument("--category", type=str,            help="Download one category")
    parser.add_argument("--file",     type=str,            help="Download one file by name")
    parser.add_argument("--outdir",   type=str,            help="Output directory (default: ./data)")
    args = parser.parse_args()

    global BASE
    if args.outdir:
        BASE = Path(args.outdir)

    make_dirs()

    if args.list:
        list_files()
    elif args.check:
        check_existing()
    elif args.all:
        download_all()
    elif args.category:
        download_category(args.category)
    elif args.file:
        download_one(args.file)
    else:
        list_files()
        print("\nRun with --all to download everything.")


if __name__ == "__main__":
    main()
