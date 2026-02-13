LSR-NCC-Replication
Law of Symbiotic Resilience (LSR) & Node Cascading Collapse (NCC) Framework
Replication Data, Code, and Verification
Show Image
Show Image
Author: Steven Brandon
Institution: Queensland University of Technology
Contact: steven.brandon@connect.qut.edu.au
SSRN Author ID: 7801909

Overview
This repository contains the complete datasets and replication code for the Law of Symbiotic Resilience research programme. The LSR demonstrates that systems designed for mutual benefit succeed at 92.2% while systems designed for extraction succeed at 29.9% — an odds ratio of 27.8 (95% CI: 23.7–32.6) — tested across 12,328 World Bank projects, 187 countries, 12 sectors, 7 regions, and 4 decades with zero exceptions.
Quick Start
bash# Clone the repository
git clone https://github.com/stevenbrandon88/LSR-NCC-Replication.git
cd LSR-NCC-Replication

# Run the replication script (Python 3.8+, no dependencies required)
python paper1_replication_v3.py
The script auto-detects the IEG dataset file. No pip install required — it uses only Python standard library.
Primary Dataset
FieldValueFileieg_world_bank_project_performance_ratings_01-17-2026.csvSourceWorld Bank Independent Evaluation Group (IEG)Downloadieg.worldbankgroup.org/dataExtraction DateJanuary 15, 2026Records12,328Countries187Year Range1956–2023 (approval fiscal year)MD55a13fbabd3f9e26698cb591aba560793
Replication Script
paper1_replication_v3.py
The replication script independently computes every IEG-derived statistic and verifies it against the published claims. It outputs PASS/FAIL for each check.
python paper1_replication_v3.py                        # auto-detect data file
python paper1_replication_v3.py path/to/ieg_data.csv   # explicit path
Expected Output (Summary)
  HIGH QE (S/HS):  3,735 / 4,049 = 92.2%
  LOW QE  (U/HU):    457 / 1,526 = 29.9%
  Total n:          5,575
  Gap:              62.3 percentage points
  Odds Ratio:       27.8 (95% CI: 23.7–32.6)
  
  Checks passed: 18/18
  ✅ ALL CLAIMS VERIFIED

⚠️ Critical Methodology Notes
These filtering rules are essential for replication. Incorrect filtering produces different (lower) numbers.
1. Excluding "Not Rated" Records
The IEG dataset contains records with Quality at Entry = "Not Rated" (3,607 records) and Outcome = "Not Rated" (151 records). These must be excluded from the relevant analyses:
python# CORRECT: Exclude "Not Rated" from BOTH QE and Outcome
has_qe = [r for r in rows 
          if r['Quality at Entry'].strip() not in ('', 'Not Rated')
          and r['Outcome'].strip() not in ('', 'Not Rated')]
Why: A project with QE = "Not Rated" was never assessed for design quality. Including it in a QE-stratified analysis is methodologically invalid. Similarly, a project with Outcome = "Not Rated" has no success/failure determination.
FilterRecordsEffectAll records12,328—Exclude Outcome = "Not Rated"12,177Denominator for overall success rateExclude QE = "Not Rated"8,570Available for QE analysisBoth excluded8,570Correct QE analysis baseStrict QE (S/HS vs U/HU only)5,575Primary comparison group
If you skip this filter, you will get n=5,662 and OR=24.6 instead of n=5,575 and OR=27.8. The paper's numbers use the correct filter.
2. Success Definition
Success is defined as Outcome ∈ {Moderately Satisfactory, Satisfactory, Highly Satisfactory}. This is the standard IEG binarisation used across World Bank evaluation literature.
3. Strict QE Comparison
The primary analysis compares only S/HS (Satisfactory + Highly Satisfactory) against U/HU (Unsatisfactory + Highly Unsatisfactory). The "Moderately" categories (MS, MU) are excluded to create maximally clean comparison groups.
4. SIDS Country Name Matching
The World Bank dataset uses both abbreviated and formal constitutional country names interchangeably. The SIDS matching list must include all variants:
WB Short NameWB Formal NameProjectsJamaicaJamaica92HaitiRepublic of Haiti72Papua New GuineaThe Independent State of Papua New Guinea58Dominican RepublicDominican Republic57MauritiusRepublic of Mauritius48GuyanaCo-operative Republic of Guyana41Guinea-BissauRepublic of Guinea-Bissau40Cabo VerdeRepublic of Cabo Verde39SamoaSamoa30ComorosUnion of the Comoros30Timor-LesteDemocratic Republic of Timor-Leste28Trinidad and TobagoRepublic of Trinidad and Tobago21Solomon IslandsSolomon Islands21MaldivesRepublic of Maldives19TongaKingdom of Tonga19
If you use only the short names, you will get n≈285 instead of n=761. The complete matching list is documented in the replication script.
5. Overall Success Rate Denominator

73.4% = 8,937 / 12,177 (rated outcomes only, excluding "Not Rated")
72.5% = 8,937 / 12,328 (all records)

The paper uses 73.4% (rated denominator), which is the standard IEG approach.

Repository Structure
LSR-NCC-Replication/
├── paper1_replication_v3.py          # Primary replication script
├── README.md                         # This file
│
├── ieg_world_bank_project_performance_ratings_01-17-2026.csv   # Primary IEG dataset
│
├── Data by Domain/
│   ├── id_econ_01/                   # Economic indicators
│   ├── id_ecos_01/                   # Ecological indicators  
│   ├── id_food_01/                   # Food security (FAOSTAT)
│   ├── id_gove_01/                   # Governance (V-Dem, WGI)
│   ├── id_heal_01/                   # Health indicators
│   ├── id_infr_01/                   # Infrastructure
│   └── id_soci_01/                   # Social indicators
│
├── Supporting Datasets/
│   ├── aer-2024-success-rates-database.xlsx          # ADB IED (independent replication)
│   ├── CrisisConsequencesData_NavigatingPolycrisis_2023.03.csv  # 169 crises
│   ├── MASTER_Seshat_Test_Register.csv               # Seshat Axial Age
│   ├── adb-sov-projects-*.csv                        # ADB sovereign projects
│   ├── OECD_CRS_*.csv                                # OECD aid data
│   └── LSR_AI_Governance_Dataset.xlsx                 # AI governance extension
│
├── External Sources/
│   ├── AidDatas_Global_Chinese_Development_Finance_Dataset_*/  # AidData v2.0/v3.0
│   ├── FAOSTAT_*/                                     # FAO statistics
│   └── WEOAPR2025/                                    # IMF World Economic Outlook
│
└── Indices/
    ├── hdi/                          # Human Development Index
    ├── gdp/                          # GDP data
    ├── pop/                          # Population data
    ├── vulnerability/                # Vulnerability indices
    └── readiness/                    # Readiness indices
Supporting Datasets
DatasetSourcenUse in LSR ProgrammeWB IEG (primary)World Bank IEG12,328 projectsPrimary empirical validationWGI 2024Kaufmann & Kraay205 countriesCountry-level Φ validationCrisis ConsequencesNavigating Polycrisis 2023169 crisesHistorical cascade analysisSeshat Axial AgeTurchin et al. 2018428 observations10,000-year institutional patternsADB IED 2024Asian Development Bank1,084 projectsIndependent replicationAidData China v2.0William & Mary 202113,427 projectsBRI context analysisV-Dem v15Varieties of Democracy19,678 rowsDemocratic governanceFragile States IndexFund for Peace178 countriesState fragilityACLEDArmed Conflict Location & EventOngoingConflict eventsFAOSTATFAOMultiple seriesFood security indicatorsIMF WEOIMFGlobalMacroeconomic projections
Key Results
ClaimDatasetnResultPrimary ORWB IEG Jan 20265,575OR = 27.8 (CI: 23.7–32.6)Dose-responseWB IEG Jan 20269,431Inflection Φ = 0.431Sector universalityWB IEG Jan 202612 sectorsAll OR > 1 (17.7–63.6)Regional universalityWB IEG Jan 20267+ regionsAll OR > 1 (15.3–37.8)Temporal trendWB IEG Jan 20265 decades3.1× → 531.9× (strengthening)Country Φ thresholdWGI 2024205 countries42/42 ≥0.70 = High IncomeEnvironmental ceilingPolycrisis 2023169 crises0/9 env-only ≥ severity 7ADB replicationADB IED 20241,084OR = 30.3Seshat prosocialAxial Age428 obsρ = 0.788, p < 10⁻⁹²
Data Integrity
All primary dataset files have MD5 hashes recorded. To verify:
bashmd5sum ieg_world_bank_project_performance_ratings_01-17-2026.csv
# Expected: 5a13fbabd3f9e26698cb591aba560793
Citation
bibtex@article{brandon2026lsr,
  title={The Law of Symbiotic Resilience: A Universal Framework for Development System Design},
  author={Brandon, Steven},
  journal={SSRN Working Paper},
  year={2026},
  institution={Queensland University of Technology},
  note={SSRN Author ID: 7801909}
}
License
This repository is licensed under CC BY 4.0. You are free to share and adapt the materials with appropriate attribution.
Contact

Email: steven.brandon@connect.qut.edu.au
SSRN: Author Page
Issues: Please open a GitHub issue for replication questions
