#!/usr/bin/env python3
"""
LSR Paper 1 - Full Replication & Verification Script
=====================================================
Author: Steven Brandon
Institution: Queensland University of Technology
Contact: steven.brandon@connect.qut.edu.au
SSRN Author ID: 7801909
Date: February 2026

This script computes ALL key statistics from the IEG dataset
and reports the TRUE values for the master document and papers.

Usage:
    python paper1_full_replication.py

Required file:
    ieg_world_bank_project_performance_ratings_01-17-2026.csv
    (Place in same directory or specify path)
"""

import csv
import hashlib
import os
import sys
import math
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

IEG_FILE = "ieg_world_bank_project_performance_ratings_01-17-2026.csv"
EXPECTED_MD5 = "5a13fbabd3f9e26698cb591aba560793"

SIDS_COUNTRIES = [
    'Antigua and Barbuda', 'Bahamas, The', 'Barbados', 'Belize', 'Cabo Verde',
    'Comoros', 'Cuba', 'Dominica', 'Dominican Republic', 'Fiji',
    'Grenada', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Jamaica',
    'Kiribati', 'Maldives', 'Marshall Islands', 'Mauritius',
    'Micronesia, Fed. Sts.', 'Nauru', 'Palau', 'Papua New Guinea',
    'St. Kitts and Nevis', 'St. Lucia', 'St. Vincent and the Grenadines',
    'Samoa', 'São Tomé and Príncipe', 'Sao Tome and Principe',
    'Seychelles', 'Singapore', 'Solomon Islands', 'Suriname',
    'Timor-Leste', 'Tonga', 'Trinidad and Tobago', 'Tuvalu', 'Vanuatu',
    # Common alternate spellings in WB data
    'Cape Verde', 'Saint Kitts and Nevis', 'Saint Lucia',
    'Saint Vincent and the Grenadines', 'Federated States of Micronesia',
]

PACIFIC_COUNTRIES = [
    'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia, Fed. Sts.',
    'Nauru', 'Palau', 'Papua New Guinea', 'Samoa', 'Solomon Islands',
    'Timor-Leste', 'Tonga', 'Tuvalu', 'Vanuatu',
    'Federated States of Micronesia',
]

# Rating classifications
SAT_RATINGS = {'Highly Satisfactory', 'Satisfactory'}
UNSAT_RATINGS = {'Highly Unsatisfactory', 'Unsatisfactory'}
BROAD_SAT = {'Highly Satisfactory', 'Satisfactory', 'Moderately Satisfactory'}
BROAD_UNSAT = {'Highly Unsatisfactory', 'Unsatisfactory', 'Moderately Unsatisfactory'}

# M&E quality levels
ME_HIGH = {'High'}
ME_SUBSTANTIAL = {'Substantial'}
ME_MODEST = {'Modest'}
ME_NEGLIGIBLE = {'Negligible'}

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def md5_file(path):
    """Compute MD5 hash of a file."""
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def odds_ratio(a, b, c, d):
    """
    Compute odds ratio and 95% CI from 2x2 table.
    a = success in group 1 (symbiotic success)
    b = fail in group 1 (symbiotic fail)  
    c = success in group 2 (extractive success)
    d = fail in group 2 (extractive fail)
    OR = (a*d) / (b*c)
    """
    if b == 0 or c == 0:
        return float('inf'), float('inf'), float('inf')
    OR = (a * d) / (b * c)
    # Woolf's method for log-OR CI
    se_ln = math.sqrt(1/a + 1/b + 1/c + 1/d) if min(a,b,c,d) > 0 else float('inf')
    ln_or = math.log(OR)
    ci_lo = math.exp(ln_or - 1.96 * se_ln)
    ci_hi = math.exp(ln_or + 1.96 * se_ln)
    return OR, ci_lo, ci_hi

def pct(num, denom):
    """Safe percentage."""
    return (num / denom * 100) if denom > 0 else 0.0

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_result(label, value, note=""):
    note_str = f"  ({note})" if note else ""
    print(f"  {label:<45} {value}{note_str}")

# ═══════════════════════════════════════════════════════════════
# MAIN ANALYSIS
# ═══════════════════════════════════════════════════════════════

def main():
    # Find the data file
    paths_to_try = [
        IEG_FILE,
        os.path.join(os.path.dirname(__file__), IEG_FILE),
        f"/mnt/user-data/uploads/{IEG_FILE}",
        f"data/{IEG_FILE}",
    ]
    
    data_path = None
    for p in paths_to_try:
        if os.path.exists(p):
            data_path = p
            break
    
    if not data_path:
        print(f"ERROR: Cannot find {IEG_FILE}")
        print(f"Tried: {paths_to_try}")
        sys.exit(1)
    
    # ── Step 1: Verify dataset integrity ──
    print_section("STEP 1: DATASET VERIFICATION")
    
    file_md5 = md5_file(data_path)
    md5_match = file_md5 == EXPECTED_MD5
    print_result("File", data_path)
    print_result("MD5 (computed)", file_md5)
    print_result("MD5 (expected)", EXPECTED_MD5)
    print_result("MD5 MATCH", "✅ YES" if md5_match else "❌ NO")
    
    # ── Step 2: Load data ──
    print_section("STEP 2: DATA LOADING")
    
    rows = []
    with open(data_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    total = len(rows)
    print_result("Total records loaded", f"{total:,}")
    
    # ── Step 3: Examine column values ──
    print_section("STEP 3: COLUMN VALUE DISTRIBUTIONS")
    
    # Outcome ratings
    outcome_counts = defaultdict(int)
    for r in rows:
        val = r.get('Outcome', '').strip()
        if val:
            outcome_counts[val] += 1
    
    print("\n  OUTCOME RATINGS:")
    for rating in sorted(outcome_counts.keys()):
        print(f"    {rating:<30} {outcome_counts[rating]:>5}")
    
    # QE ratings
    qe_counts = defaultdict(int)
    for r in rows:
        val = r.get('Quality at Entry', '').strip()
        if val:
            qe_counts[val] += 1
    
    print("\n  QUALITY AT ENTRY RATINGS:")
    for rating in sorted(qe_counts.keys()):
        print(f"    {rating:<30} {qe_counts[rating]:>5}")
    
    # QoS ratings
    qs_counts = defaultdict(int)
    for r in rows:
        val = r.get('Quality of Supervision', '').strip()
        if val:
            qs_counts[val] += 1
    
    print("\n  QUALITY OF SUPERVISION RATINGS:")
    for rating in sorted(qs_counts.keys()):
        print(f"    {rating:<30} {qs_counts[rating]:>5}")
    
    # M&E ratings
    me_counts = defaultdict(int)
    for r in rows:
        val = r.get('M&E Quality', '').strip()
        if val:
            me_counts[val] += 1
    
    print("\n  M&E QUALITY RATINGS:")
    for rating in sorted(me_counts.keys()):
        print(f"    {rating:<30} {me_counts[rating]:>5}")
    
    # Eval types
    eval_counts = defaultdict(int)
    for r in rows:
        val = r.get('Evaluation Type', '').strip()
        if val:
            eval_counts[val] += 1
    
    print("\n  EVALUATION TYPES:")
    for etype in sorted(eval_counts.keys()):
        print(f"    {etype:<30} {eval_counts[etype]:>5}")
    
    # ── Step 4: Core statistics ──
    print_section("STEP 4: CORE STATISTICS")
    
    # 4a: Overall success rate (Outcome = any satisfactory variant)
    has_outcome = [r for r in rows if r.get('Outcome', '').strip()]
    sat = [r for r in has_outcome if r['Outcome'].strip() in BROAD_SAT]
    unsat = [r for r in has_outcome if r['Outcome'].strip() in BROAD_UNSAT]
    rated = sat + unsat  # Only projects with clear sat/unsat
    
    n_rated = len(has_outcome)
    n_sat = len(sat)
    n_unsat_broad = len(unsat)
    
    print(f"\n  Projects with Outcome rating:    {n_rated:>6}")
    print(f"  Satisfactory (MS+S+HS):          {n_sat:>6} ({pct(n_sat, n_rated):.1f}%)")
    print(f"  Unsatisfactory (MU+U+HU):        {n_unsat_broad:>6} ({pct(n_unsat_broad, n_rated):.1f}%)")
    print(f"  Other/Missing:                   {total - n_rated:>6}")
    
    # Break down sat/unsat
    n_hs = sum(1 for r in has_outcome if r['Outcome'].strip() == 'Highly Satisfactory')
    n_s = sum(1 for r in has_outcome if r['Outcome'].strip() == 'Satisfactory')
    n_ms = sum(1 for r in has_outcome if r['Outcome'].strip() == 'Moderately Satisfactory')
    n_mu = sum(1 for r in has_outcome if r['Outcome'].strip() == 'Moderately Unsatisfactory')
    n_u = sum(1 for r in has_outcome if r['Outcome'].strip() == 'Unsatisfactory')
    n_hu = sum(1 for r in has_outcome if r['Outcome'].strip() == 'Highly Unsatisfactory')
    
    print(f"\n  Breakdown:")
    print(f"    Highly Satisfactory:           {n_hs:>6}")
    print(f"    Satisfactory:                  {n_s:>6}")
    print(f"    Moderately Satisfactory:       {n_ms:>6}")
    print(f"    Moderately Unsatisfactory:     {n_mu:>6}")
    print(f"    Unsatisfactory:                {n_u:>6}")
    print(f"    Highly Unsatisfactory:         {n_hu:>6}")
    print(f"    TOTAL rated:                   {n_hs+n_s+n_ms+n_mu+n_u+n_hu:>6}")
    
    # ── Step 5: QE Analysis (Strict - S/HS vs U/HU) ──
    print_section("STEP 5: QUALITY AT ENTRY - STRICT ANALYSIS")
    
    has_qe_outcome = [r for r in rows 
                      if r.get('Quality at Entry', '').strip() 
                      and r.get('Outcome', '').strip()]
    
    # Strict QE: only S/HS vs U/HU
    qe_high = [r for r in has_qe_outcome if r['Quality at Entry'].strip() in SAT_RATINGS]
    qe_low = [r for r in has_qe_outcome if r['Quality at Entry'].strip() in UNSAT_RATINGS]
    
    qe_high_sat = sum(1 for r in qe_high if r['Outcome'].strip() in BROAD_SAT)
    qe_high_unsat = len(qe_high) - qe_high_sat
    qe_low_sat = sum(1 for r in qe_low if r['Outcome'].strip() in BROAD_SAT)
    qe_low_unsat = len(qe_low) - qe_low_sat
    
    qe_high_rate = pct(qe_high_sat, len(qe_high))
    qe_low_rate = pct(qe_low_sat, len(qe_low))
    qe_gap = qe_high_rate - qe_low_rate
    
    OR_qe, ci_lo_qe, ci_hi_qe = odds_ratio(qe_high_sat, qe_high_unsat, qe_low_sat, qe_low_unsat)
    
    print(f"\n  HIGH QE (S/HS):")
    print(f"    n = {len(qe_high):,}")
    print(f"    Success: {qe_high_sat:,} / {len(qe_high):,} = {qe_high_rate:.1f}%")
    print(f"\n  LOW QE (U/HU):")
    print(f"    n = {len(qe_low):,}")
    print(f"    Success: {qe_low_sat:,} / {len(qe_low):,} = {qe_low_rate:.1f}%")
    print(f"\n  STRICT QE TOTAL n = {len(qe_high) + len(qe_low):,}")
    print(f"  GAP: {qe_gap:.1f} percentage points")
    print(f"  OR = {OR_qe:.1f} (95% CI: {ci_lo_qe:.1f} – {ci_hi_qe:.1f})")
    
    # ── Step 5b: QE Broad (MS+ vs MU-) ──
    print_section("STEP 5b: QUALITY AT ENTRY - BROAD ANALYSIS")
    
    qe_broad_high = [r for r in has_qe_outcome if r['Quality at Entry'].strip() in BROAD_SAT]
    qe_broad_low = [r for r in has_qe_outcome if r['Quality at Entry'].strip() in BROAD_UNSAT]
    
    qe_bh_sat = sum(1 for r in qe_broad_high if r['Outcome'].strip() in BROAD_SAT)
    qe_bh_unsat = len(qe_broad_high) - qe_bh_sat
    qe_bl_sat = sum(1 for r in qe_broad_low if r['Outcome'].strip() in BROAD_SAT)
    qe_bl_unsat = len(qe_broad_low) - qe_bl_sat
    
    qe_bh_rate = pct(qe_bh_sat, len(qe_broad_high))
    qe_bl_rate = pct(qe_bl_sat, len(qe_broad_low))
    
    OR_qe_b, ci_lo_b, ci_hi_b = odds_ratio(qe_bh_sat, qe_bh_unsat, qe_bl_sat, qe_bl_unsat)
    
    print(f"\n  HIGH QE Broad (MS/S/HS): n={len(qe_broad_high):,}, Success={qe_bh_rate:.1f}%")
    print(f"  LOW QE Broad (MU/U/HU):  n={len(qe_broad_low):,}, Success={qe_bl_rate:.1f}%")
    print(f"  OR = {OR_qe_b:.1f} (95% CI: {ci_lo_b:.1f} – {ci_hi_b:.1f})")
    
    # ── Step 6: QoS Analysis ──
    print_section("STEP 6: QUALITY OF SUPERVISION - STRICT ANALYSIS")
    
    has_qs_outcome = [r for r in rows 
                      if r.get('Quality of Supervision', '').strip()
                      and r.get('Outcome', '').strip()]
    
    qs_high = [r for r in has_qs_outcome if r['Quality of Supervision'].strip() in SAT_RATINGS]
    qs_low = [r for r in has_qs_outcome if r['Quality of Supervision'].strip() in UNSAT_RATINGS]
    
    qs_high_sat = sum(1 for r in qs_high if r['Outcome'].strip() in BROAD_SAT)
    qs_high_unsat = len(qs_high) - qs_high_sat
    qs_low_sat = sum(1 for r in qs_low if r['Outcome'].strip() in BROAD_SAT)
    qs_low_unsat = len(qs_low) - qs_low_sat
    
    qs_high_rate = pct(qs_high_sat, len(qs_high))
    qs_low_rate = pct(qs_low_sat, len(qs_low))
    
    OR_qs, ci_lo_qs, ci_hi_qs = odds_ratio(qs_high_sat, qs_high_unsat, qs_low_sat, qs_low_unsat)
    
    print(f"\n  HIGH QoS (S/HS): n={len(qs_high):,}, Success={qs_high_rate:.1f}%")
    print(f"  LOW QoS (U/HU):  n={len(qs_low):,}, Success={qs_low_rate:.1f}%")
    print(f"  STRICT QoS TOTAL n = {len(qs_high) + len(qs_low):,}")
    print(f"  OR = {OR_qs:.1f} (95% CI: {ci_lo_qs:.1f} – {ci_hi_qs:.1f})")
    
    # ── Step 7: M&E Analysis ──
    print_section("STEP 7: M&E QUALITY ANALYSIS")
    
    has_me_outcome = [r for r in rows
                      if r.get('M&E Quality', '').strip()
                      and r.get('Outcome', '').strip()]
    
    for me_level in ['High', 'Substantial', 'Modest', 'Negligible']:
        me_group = [r for r in has_me_outcome if r['M&E Quality'].strip() == me_level]
        me_sat = sum(1 for r in me_group if r['Outcome'].strip() in BROAD_SAT)
        me_rate = pct(me_sat, len(me_group))
        print(f"  M&E {me_level:<15} n={len(me_group):>5}, Success={me_sat:>5}/{len(me_group):>5} = {me_rate:.1f}%")
    
    # ── Step 8: Certification Analysis (QE HIGH + QoS HIGH) ──
    print_section("STEP 8: CERTIFICATION (QE=S/HS AND QoS=S/HS)")
    
    has_all = [r for r in rows
               if r.get('Quality at Entry', '').strip()
               and r.get('Quality of Supervision', '').strip()
               and r.get('Outcome', '').strip()]
    
    certify = [r for r in has_all 
               if r['Quality at Entry'].strip() in SAT_RATINGS 
               and r['Quality of Supervision'].strip() in SAT_RATINGS]
    reject = [r for r in has_all
              if r['Quality at Entry'].strip() in UNSAT_RATINGS
              and r['Quality of Supervision'].strip() in UNSAT_RATINGS]
    
    cert_sat = sum(1 for r in certify if r['Outcome'].strip() in BROAD_SAT)
    cert_rate = pct(cert_sat, len(certify))
    rej_sat = sum(1 for r in reject if r['Outcome'].strip() in BROAD_SAT)
    rej_rate = pct(rej_sat, len(reject))
    
    print(f"\n  CERTIFY (QE=S/HS & QoS=S/HS): n={len(certify):,}, Success={cert_sat}/{len(certify)} = {cert_rate:.1f}%")
    print(f"  REJECT  (QE=U/HU & QoS=U/HU): n={len(reject):,}, Success={rej_sat}/{len(reject)} = {rej_rate:.1f}%")
    print(f"  GAP: {cert_rate - rej_rate:.1f} pp")
    
    if len(certify) > 0 and len(reject) > 0:
        cert_unsat = len(certify) - cert_sat
        rej_unsat = len(reject) - rej_sat
        OR_cert, ci_lo_c, ci_hi_c = odds_ratio(cert_sat, cert_unsat, rej_sat, rej_unsat)
        print(f"  OR = {OR_cert:.1f} (95% CI: {ci_lo_c:.1f} – {ci_hi_c:.1f})")
    
    # ── Step 9: SIDS Analysis ──
    print_section("STEP 9: SIDS ANALYSIS")
    
    sids_projects = [r for r in has_outcome if r.get('Country / Economy', '').strip() in SIDS_COUNTRIES]
    sids_sat = sum(1 for r in sids_projects if r['Outcome'].strip() in BROAD_SAT)
    sids_rate = pct(sids_sat, len(sids_projects))
    
    pacific_projects = [r for r in has_outcome if r.get('Country / Economy', '').strip() in PACIFIC_COUNTRIES]
    pac_sat = sum(1 for r in pacific_projects if r['Outcome'].strip() in BROAD_SAT)
    pac_rate = pct(pac_sat, len(pacific_projects))
    
    print(f"\n  ALL SIDS: n={len(sids_projects):,}, Success={sids_sat}/{len(sids_projects)} = {sids_rate:.1f}%")
    print(f"  PACIFIC:  n={len(pacific_projects):,}, Success={pac_sat}/{len(pacific_projects)} = {pac_rate:.1f}%")
    
    # SIDS QE strict
    sids_qe = [r for r in sids_projects if r.get('Quality at Entry', '').strip()]
    sids_qe_high = [r for r in sids_qe if r['Quality at Entry'].strip() in SAT_RATINGS]
    sids_qe_low = [r for r in sids_qe if r['Quality at Entry'].strip() in UNSAT_RATINGS]
    
    if sids_qe_high and sids_qe_low:
        sh_sat = sum(1 for r in sids_qe_high if r['Outcome'].strip() in BROAD_SAT)
        sh_rate = pct(sh_sat, len(sids_qe_high))
        sl_sat = sum(1 for r in sids_qe_low if r['Outcome'].strip() in BROAD_SAT)
        sl_rate = pct(sl_sat, len(sids_qe_low))
        
        OR_sids, _, _ = odds_ratio(sh_sat, len(sids_qe_high)-sh_sat, sl_sat, len(sids_qe_low)-sl_sat)
        print(f"\n  SIDS QE HIGH: n={len(sids_qe_high)}, Success={sh_rate:.1f}%")
        print(f"  SIDS QE LOW:  n={len(sids_qe_low)}, Success={sl_rate:.1f}%")
        print(f"  SIDS OR = {OR_sids:.1f}")
    
    # Pacific QE strict
    pac_qe = [r for r in pacific_projects if r.get('Quality at Entry', '').strip()]
    pac_qe_high = [r for r in pac_qe if r['Quality at Entry'].strip() in SAT_RATINGS]
    pac_qe_low = [r for r in pac_qe if r['Quality at Entry'].strip() in UNSAT_RATINGS]
    
    if pac_qe_high and pac_qe_low:
        ph_sat = sum(1 for r in pac_qe_high if r['Outcome'].strip() in BROAD_SAT)
        ph_rate = pct(ph_sat, len(pac_qe_high))
        pl_sat = sum(1 for r in pac_qe_low if r['Outcome'].strip() in BROAD_SAT)
        pl_rate = pct(pl_sat, len(pac_qe_low))
        
        OR_pac, _, _ = odds_ratio(ph_sat, len(pac_qe_high)-ph_sat, pl_sat, len(pac_qe_low)-pl_sat)
        print(f"\n  PACIFIC QE HIGH: n={len(pac_qe_high)}, Success={ph_rate:.1f}%")
        print(f"  PACIFIC QE LOW:  n={len(pac_qe_low)}, Success={pl_rate:.1f}%")
        print(f"  PACIFIC OR = {OR_pac:.1f}")
    
    # ── Step 10: Sector Analysis ──
    print_section("STEP 10: SECTOR ANALYSIS (STRICT QE)")
    
    sectors = defaultdict(lambda: {'high_sat': 0, 'high_total': 0, 'low_sat': 0, 'low_total': 0})
    
    for r in has_qe_outcome:
        qe = r['Quality at Entry'].strip()
        sector = r.get('Global Practice', '').strip() or r.get('Practice Group', '').strip()
        if not sector:
            continue
        outcome_sat = r['Outcome'].strip() in BROAD_SAT
        
        if qe in SAT_RATINGS:
            sectors[sector]['high_total'] += 1
            if outcome_sat:
                sectors[sector]['high_sat'] += 1
        elif qe in UNSAT_RATINGS:
            sectors[sector]['low_total'] += 1
            if outcome_sat:
                sectors[sector]['low_sat'] += 1
    
    print(f"\n  {'Sector':<40} {'n':>5} {'HIGH%':>7} {'LOW%':>7} {'OR':>8}")
    print(f"  {'-'*40} {'---':>5} {'-----':>7} {'-----':>7} {'------':>8}")
    
    for sector in sorted(sectors.keys()):
        s = sectors[sector]
        n = s['high_total'] + s['low_total']
        if n < 20:  # Skip tiny sectors
            continue
        h_rate = pct(s['high_sat'], s['high_total'])
        l_rate = pct(s['low_sat'], s['low_total'])
        
        h_fail = s['high_total'] - s['high_sat']
        l_fail = s['low_total'] - s['low_sat']
        
        if h_fail > 0 and s['low_sat'] > 0:
            OR_s, _, _ = odds_ratio(s['high_sat'], h_fail, s['low_sat'], l_fail)
            or_str = f"{OR_s:.1f}"
        else:
            or_str = "∞"
        
        print(f"  {sector:<40} {n:>5} {h_rate:>6.1f}% {l_rate:>6.1f}% {or_str:>8}")
    
    # ── Step 11: Region Analysis ──
    print_section("STEP 11: REGION ANALYSIS (STRICT QE)")
    
    regions = defaultdict(lambda: {'high_sat': 0, 'high_total': 0, 'low_sat': 0, 'low_total': 0})
    
    for r in has_qe_outcome:
        qe = r['Quality at Entry'].strip()
        region = r.get('WB Region', '').strip()
        if not region:
            continue
        outcome_sat = r['Outcome'].strip() in BROAD_SAT
        
        if qe in SAT_RATINGS:
            regions[region]['high_total'] += 1
            if outcome_sat:
                regions[region]['high_sat'] += 1
        elif qe in UNSAT_RATINGS:
            regions[region]['low_total'] += 1
            if outcome_sat:
                regions[region]['low_sat'] += 1
    
    print(f"\n  {'Region':<40} {'n':>5} {'HIGH%':>7} {'LOW%':>7} {'OR':>8}")
    print(f"  {'-'*40} {'---':>5} {'-----':>7} {'-----':>7} {'------':>8}")
    
    for region in sorted(regions.keys()):
        s = regions[region]
        n = s['high_total'] + s['low_total']
        if n < 10:
            continue
        h_rate = pct(s['high_sat'], s['high_total'])
        l_rate = pct(s['low_sat'], s['low_total'])
        
        h_fail = s['high_total'] - s['high_sat']
        l_fail = s['low_total'] - s['low_sat']
        
        if h_fail > 0 and s['low_sat'] > 0:
            OR_r, _, _ = odds_ratio(s['high_sat'], h_fail, s['low_sat'], l_fail)
            or_str = f"{OR_r:.1f}"
        else:
            or_str = "∞"
        
        print(f"  {region:<40} {n:>5} {h_rate:>6.1f}% {l_rate:>6.1f}% {or_str:>8}")
    
    # ── Step 12: Decade Analysis ──
    print_section("STEP 12: DECADE ANALYSIS (STRICT QE)")
    
    decades = defaultdict(lambda: {'high_sat': 0, 'high_total': 0, 'low_sat': 0, 'low_total': 0})
    
    for r in has_qe_outcome:
        qe = r['Quality at Entry'].strip()
        try:
            fy = int(r.get('Approval FY', 0))
        except (ValueError, TypeError):
            continue
        decade = (fy // 10) * 10
        if decade < 1970:
            continue
        outcome_sat = r['Outcome'].strip() in BROAD_SAT
        
        if qe in SAT_RATINGS:
            decades[decade]['high_total'] += 1
            if outcome_sat:
                decades[decade]['high_sat'] += 1
        elif qe in UNSAT_RATINGS:
            decades[decade]['low_total'] += 1
            if outcome_sat:
                decades[decade]['low_sat'] += 1
    
    print(f"\n  {'Decade':<15} {'n':>5} {'HIGH%':>7} {'LOW%':>7} {'OR':>8}")
    print(f"  {'-'*15} {'---':>5} {'-----':>7} {'-----':>7} {'------':>8}")
    
    for decade in sorted(decades.keys()):
        s = decades[decade]
        n = s['high_total'] + s['low_total']
        if n < 10:
            continue
        h_rate = pct(s['high_sat'], s['high_total'])
        l_rate = pct(s['low_sat'], s['low_total'])
        
        h_fail = s['high_total'] - s['high_sat']
        l_fail = s['low_total'] - s['low_sat']
        
        if h_fail > 0 and s['low_sat'] > 0:
            OR_d, _, _ = odds_ratio(s['high_sat'], h_fail, s['low_sat'], l_fail)
            or_str = f"{OR_d:.1f}"
        else:
            or_str = "∞"
        
        print(f"  {str(decade)+'s':<15} {n:>5} {h_rate:>6.1f}% {l_rate:>6.1f}% {or_str:>8}")
    
    # ── Step 13: Income/FCS Analysis ──
    print_section("STEP 13: INCOME GROUP & FCS ANALYSIS (STRICT QE)")
    
    for group_col, group_name in [('Country / Economy Lending Group', 'Lending Group'),
                                    ('Country / Economy FCS Status', 'FCS Status')]:
        groups = defaultdict(lambda: {'high_sat': 0, 'high_total': 0, 'low_sat': 0, 'low_total': 0})
        
        for r in has_qe_outcome:
            qe = r['Quality at Entry'].strip()
            grp = r.get(group_col, '').strip()
            if not grp:
                continue
            outcome_sat = r['Outcome'].strip() in BROAD_SAT
            
            if qe in SAT_RATINGS:
                groups[grp]['high_total'] += 1
                if outcome_sat:
                    groups[grp]['high_sat'] += 1
            elif qe in UNSAT_RATINGS:
                groups[grp]['low_total'] += 1
                if outcome_sat:
                    groups[grp]['low_sat'] += 1
        
        print(f"\n  {group_name}:")
        for grp in sorted(groups.keys()):
            s = groups[grp]
            n = s['high_total'] + s['low_total']
            if n < 5:
                continue
            h_rate = pct(s['high_sat'], s['high_total'])
            l_rate = pct(s['low_sat'], s['low_total'])
            h_fail = s['high_total'] - s['high_sat']
            l_fail = s['low_total'] - s['low_sat']
            if h_fail > 0 and s['low_sat'] > 0:
                OR_g, _, _ = odds_ratio(s['high_sat'], h_fail, s['low_sat'], l_fail)
                or_str = f"{OR_g:.1f}"
            else:
                or_str = "∞"
            print(f"    {grp:<35} n={n:>5}, HIGH={h_rate:.1f}%, LOW={l_rate:.1f}%, OR={or_str}")
    
    # ── Step 14: QAE + M&E Combined Score ──
    print_section("STEP 14: QAE + M&E COMBINED SCORE (TIER 1)")
    
    qae_map = {
        'Highly Satisfactory': 5, 'Satisfactory': 4, 'Moderately Satisfactory': 3,
        'Moderately Unsatisfactory': 2, 'Unsatisfactory': 1, 'Highly Unsatisfactory': 1
    }
    me_map = {
        'High': 5, 'Substantial': 4, 'Modest': 3, 'Modest ': 3,
        'Negligible': 2, 'Not Applicable': 1
    }
    
    has_both = [r for r in rows
                if r.get('Quality at Entry', '').strip() in qae_map
                and r.get('M&E Quality', '').strip() in me_map
                and r.get('Outcome', '').strip()]
    
    score_bins = defaultdict(lambda: {'sat': 0, 'total': 0})
    for r in has_both:
        qae_score = qae_map[r['Quality at Entry'].strip()]
        me_score = me_map[r['M&E Quality'].strip()]
        combined = qae_score + me_score
        outcome_sat = r['Outcome'].strip() in BROAD_SAT
        score_bins[combined]['total'] += 1
        if outcome_sat:
            score_bins[combined]['sat'] += 1
    
    print(f"\n  {'Score':<8} {'n':>6} {'Success':>8} {'Rate':>8}")
    print(f"  {'-'*8} {'---':>6} {'-------':>8} {'----':>8}")
    total_tier1 = 0
    for score in sorted(score_bins.keys()):
        s = score_bins[score]
        rate = pct(s['sat'], s['total'])
        print(f"  {score:<8} {s['total']:>6} {s['sat']:>8} {rate:>7.1f}%")
        total_tier1 += s['total']
    print(f"  {'TOTAL':<8} {total_tier1:>6}")
    
    # ── SUMMARY ──
    print_section("SUMMARY: CORRECTED CANONICAL NUMBERS")
    
    print(f"""
  ┌──────────────────────────────────────────────────────────────┐
  │ THESE ARE THE TRUE NUMBERS FROM THE IEG DATASET             │
  │ MD5: {file_md5}                     │
  │ All numbers below are computed, not assumed.                 │
  └──────────────────────────────────────────────────────────────┘
  
  Total IEG projects:          {total:>8,}
  Projects with Outcome:       {n_rated:>8,}
  Overall success rate:        {pct(n_sat, n_rated):>7.1f}%
  
  QE STRICT (S/HS vs U/HU):
    n =                        {len(qe_high) + len(qe_low):>8,}
    HIGH QE success:           {qe_high_rate:>7.1f}%  (n={len(qe_high):,})
    LOW QE success:            {qe_low_rate:>7.1f}%  (n={len(qe_low):,})
    GAP:                       {qe_gap:>7.1f} pp
    OR:                        {OR_qe:>7.1f}  (CI: {ci_lo_qe:.1f}–{ci_hi_qe:.1f})
  
  QoS STRICT (S/HS vs U/HU):
    HIGH QoS success:          {qs_high_rate:>7.1f}%  (n={len(qs_high):,})
    LOW QoS success:           {qs_low_rate:>7.1f}%  (n={len(qs_low):,})
  
  CERTIFICATION (QE=S/HS & QoS=S/HS):
    CERTIFY success:           {cert_rate:>7.1f}%  (n={len(certify):,})
    REJECT success:            {rej_rate:>7.1f}%  (n={len(reject):,})
  
  SIDS: n={len(sids_projects):,}, success={sids_rate:.1f}%
  PACIFIC: n={len(pacific_projects):,}, success={pac_rate:.1f}%
""")
    
    print("  SCRIPT COMPLETE. Use these numbers in all papers and documents.")
    print(f"  {'='*60}")


if __name__ == '__main__':
    main()
