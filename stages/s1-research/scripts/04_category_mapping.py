#!/usr/bin/env python3
"""Generate S1_01_CATEGORY_MAPPING.csv — two-layer official taxonomy mapping.

Layer 1 "complete official classification" = 55 subdomains from the paper's
Figure 2 (evidence/official_taxonomy_55.tsv), 13 named industry clusters + the
"Other" catch-all. Layer 2 "active-task observed classification" = the 49 of
those 55 that have >=1 active task in the published set, flagged via
`coverage_status` (active_observed vs uncovered_official).

computing_math A/B is NOT adjudicated. Three separate machine-readable columns
record plan A (whole-domain exclusion), plan B (per-subdomain), and disputes.
math_ops_research is conditional-keep under B; quantum stays disputed;
other/sports is a catch-all and NOT an auto-approved non-CS quota category.
"""
import csv, json, collections

BASE = "/Users/mac/Workspaces/ale-研究设计"
PUB = set(json.load(open(f"{BASE}/agents-last-exam/tasks/published_tasks.json"))['published'].keys())

# complete official taxonomy (55 rows) from Figure 2
official = list(csv.DictReader(open("evidence/official_taxonomy_55.tsv"), delimiter="\t"))

# official_domain_name -> task_card domain_code
DOMAIN_CODE = {
    "Engineering & Architecture": "engineering",
    "Physical Sciences": "physical_sciences",
    "Life Sciences": "life_sciences",
    "Health & Medicine": "health_medicine",
    "Psychology & Neuroscience": "psychology_neuro",
    "Business & Finance": "business_finance",
    "Legal": "legal",
    "Visual & Media Arts": "visual_media",
    "Computing, Data & Mathematical Sciences": "computing_math",
    "Transport & Safety": "transport_safety",
    "Education & Information": "education_info",
    "Agriculture & Environment": "agriculture_env",
    "Social Sciences": "social_sciences",
    "Other": "other",
}

cards = list(csv.DictReader(open("evidence/taxonomy_card_rows.tsv"), delimiter="\t"))
active = [r for r in cards if r["task_id"] in PUB]

tax_count = collections.Counter((r["dom_code"], r["sub_code"]) for r in active)
dom_tax_count = collections.Counter(r["dom_code"] for r in active)
dom_dir_count = collections.Counter(r["category"] for r in active)

# cross-domain reclassification (category != domain_code), by real task_id
reclassified = []
for r in cards:
    if r["taxonomy_missing"] == "True":
        continue
    if r["category"] != r["dom_code"]:
        reclassified.append((r["task_id"], r["category"], r["dom_code"], r["sub_code"]))

reclass_in = collections.defaultdict(list)
reclass_out = collections.defaultdict(list)
for tid, cat, dom, sub in reclassified:
    reclass_in[(dom, sub)].append(f"{cat}->{dom}/{sub}")
    reclass_out[cat].append(f"{tid}->{dom}/{sub}")

# plan A / plan B / dispute for computing_math subdomains (NOT adjudicated)
CS_SUBDOMAINS = {"software_eng", "data_analytics", "ai_cs_research",
                 "cybersecurity", "infra_cloud"}
COMPUTING_AB = {
    "software_eng":   ("excluded", "excluded_cs_subdomain", ""),
    "data_analytics": ("excluded", "excluded_cs_subdomain", ""),
    "ai_cs_research": ("excluded", "excluded_cs_subdomain", ""),
    "math_ops_research": ("excluded", "conditional_keep_non_cs_math_or", ""),
    "cybersecurity":  ("excluded", "excluded_cs_subdomain", ""),
    "infra_cloud":    ("excluded", "excluded_cs_subdomain", ""),
    "quantum":        ("excluded", "dispute_unresolved", "quantum_straddles_physics_and_cs"),
}

DISPUTE = {
    ("agriculture_env", "env_water"): "No task in agriculture_env directory (2 retired: crop_rotation_d02, ndvi_zonal_statistics_d02). Only active member is reclassified-in physical_sciences/glm_lake_calibration (prev: physical_sciences/earth_atmo).",
    ("business_finance", "accounting"): "None.",
    ("business_finance", "actuarial_risk"): "None.",
    ("business_finance", "compliance"): "reclassified-in legal/agora_governance_classify_instance_1 (prev: legal/legal_research).",
    ("business_finance", "enterprise_analytics"): "None.",
    ("business_finance", "hr_pm"): "None.",
    ("business_finance", "quant_finance"): "None.",
    ("business_finance", "sales_marketing"): "reclassified-out business_finance/saas_onepager_brand_refresh_instance_1 -> visual_media/graphic_design (prev: sales_marketing).",
    ("business_finance", "supply_chain"): "None.",
    ("computing_math", "software_eng"): "reclassified-out computing_math/go_game_reconstruction_1 -> other/sports (prev: software_eng).",
    ("computing_math", "data_analytics"): "None.",
    ("computing_math", "ai_cs_research"): "None.",
    ("computing_math", "math_ops_research"): "None.",
    ("computing_math", "cybersecurity"): "None.",
    ("computing_math", "infra_cloud"): "None.",
    ("computing_math", "quantum"): "Quantum computing straddles physics and CS; B-candidate boundary is unadjudicated this round.",
    ("education_info", "library_info"): "None.",
    ("education_info", "translation"): "None.",
    ("engineering", "aerospace_mech"): "None.",
    ("engineering", "civil_geo"): "None.",
    ("engineering", "electronics"): "None.",
    ("engineering", "energy_power"): "None.",
    ("engineering", "manufacturing"): "None.",
    ("engineering", "robotics"): "reclassified-out engineering/robotics_blender_tabletop_reconstruction -> visual_media/animation_3d (prev: robotics).",
    ("engineering", "semiconductor"): "None.",
    ("engineering", "urban_planning"): "reclassified-in transport_safety/abm_hangzhou_metro (prev: transport_safety/aviation, an uncovered official leaf).",
    ("health_medicine", "clinical_diagnostics"): "None.",
    ("health_medicine", "therapeutic_oncology"): "None.",
    ("health_medicine", "clinical_informatics"): "reclassified-out health_medicine/causal_ihdp_ite_estimation_6a_v1 -> social_sciences/economics (prev: clinical_informatics).",
    ("health_medicine", "public_health"): "reclassified-out health_medicine/ltmle_targeted_bootstrap_simulation_study -> social_sciences/economics (prev: public_health).",
    ("health_medicine", "clinical_trials"): "None.",
    ("legal", "litigation"): "reclassified-in business_finance/legal_ma_consistency_audit_01 (prev: business_finance/compliance).",
    ("legal", "legal_research"): "reclassified-out legal/agora_governance_classify_instance_1 -> business_finance/compliance (prev: legal_research).",
    ("life_sciences", "biomolecular"): "reclassified-in physical_sciences/lenacapavir_sar_table2_extraction (prev: physical_sciences/chemistry_materials).",
    ("life_sciences", "genomics"): "None.",
    ("life_sciences", "cell_imaging"): "None.",
    ("life_sciences", "systems_microbial"): "reclassified-in physical_sciences/gillespie_gene_regulatory_network (prev: physical_sciences/chemistry_materials).",
    ("other", "sports"): "other is the formal catch-all bucket, NOT an auto-approved non-CS quota category. 2 directory tasks, but membership shifts: other/mota_exploration reclassified-out -> visual_media/animation_3d; computing_math/go_game_reconstruction_1 reclassified-in (prev: computing_math/software_eng). Net: 2 active by taxonomy.",
    ("physical_sciences", "physics"): "None.",
    ("physical_sciences", "chemistry_materials"): "reclassified-out physical_sciences/gillespie_gene_regulatory_network -> life_sciences/systems_microbial; physical_sciences/lenacapavir_sar_table2_extraction -> life_sciences/biomolecular (both prev: chemistry_materials).",
    ("physical_sciences", "astronomy"): "None.",
    ("physical_sciences", "earth_atmo"): "reclassified-out physical_sciences/glm_lake_calibration -> agriculture_env/env_water (prev: earth_atmo).",
    ("psychology_neuro", "comp_neuro"): "reclassified-out psychology_neuro/reddit_ai_post_codebook_boolean_coding -> social_sciences/economics (prev: comp_neuro).",
    ("psychology_neuro", "exp_psychology"): "None.",
    ("social_sciences", "economics"): "reclassified-in 3: health_medicine/causal_ihdp_ite_estimation_6a_v1, health_medicine/ltmle_targeted_bootstrap_simulation_study, psychology_neuro/reddit_ai_post_codebook_boolean_coding. social_sciences directory has only 1 task (transport_safety/abm_hangzhou_metro is reclassified-out to engineering).",
    ("transport_safety", "fire_safety"): "reclassified-out transport_safety/abm_hangzhou_metro -> engineering/urban_planning (prev: transport_safety/aviation).",
    ("visual_media", "animation_3d"): "reclassified-in 2: engineering/robotics_blender_tabletop_reconstruction, other/mota_exploration.",
    ("visual_media", "graphic_design"): "reclassified-in business_finance/saas_onepager_brand_refresh_instance_1 (prev: business_finance/sales_marketing).",
    ("visual_media", "audio_music"): "None.",
    # uncovered official subdomains (no active task)
    ("engineering", "chemical_process"): "Uncovered official subdomain (no active task in the published set).",
    ("engineering", "mining_petroleum"): "Uncovered official subdomain (no active task in the published set).",
    ("transport_safety", "aviation"): "Uncovered official subdomain; confirmed name via classifier.previous of transport_safety/abm_hangzhou_metro (which was reclassified out to engineering/urban_planning).",
    ("transport_safety", "maritime_port"): "Uncovered official subdomain (no active task in the published set).",
    ("education_info", "educational_technology"): "Uncovered official subdomain (no active task in the published set).",
    ("agriculture_env", "precision_agriculture"): "Uncovered official subdomain (no active task in the published set).",
}

cols = ["domain_id", "domain_code", "official_domain_name", "subdomain_id",
        "subdomain_code", "subdomain_name", "id_source", "coverage_status",
        "active_taxonomy_count", "domain_dir_count", "domain_tax_count",
        "reclassified_in", "reclassified_out", "mapping_dispute",
        "ab_A_status", "ab_B_status", "ab_dispute", "exclusion_status",
        "evidence_location"]

rows = []
for o in official:
    official_name = o["official_domain_name"]
    dom = DOMAIN_CODE[official_name]
    sub = o["subdomain_code"]
    sid = o["subdomain_id"]
    name = o["subdomain_name"]
    id_source = o["id_source"]
    observed = o["observed"] == "yes"
    coverage = "active_observed" if observed else "uncovered_official"
    atc = tax_count.get((dom, sub), 0) if observed else 0
    ddc = dom_dir_count.get(dom, 0)
    dtc = dom_tax_count.get(dom, 0)
    rin = ";".join(reclass_in.get((dom, sub), [])) or ""
    rout = ";".join(reclass_out.get(dom, [])) or ""
    dispute = DISPUTE.get((dom, sub), "None.")
    if dom == "computing_math":
        a_status, b_status, ab_dispute = COMPUTING_AB.get(
            sub, ("excluded", "excluded_cs_subdomain", ""))
        excl = "excluded_awaiting_AB"
    elif dom == "other":
        a_status = b_status = ab_dispute = ""
        excl = "catch_all_not_auto_approved"
    else:
        a_status = b_status = ab_dispute = ""
        excl = "candidate_non_cs"
    if observed:
        ev = (f"agents-last-exam/tasks/{dom}/*/task_card.json (taxonomy field); "
              "classifier.previous for reclassification; Figure 2 (official_taxonomy_55.tsv)")
    else:
        ev = ("official_taxonomy_55.tsv (paper Figure 2); no task_card.json "
              "(uncovered). ID source: " + id_source)
    rows.append([o["domain_id"], dom, official_name, sid, sub, name, id_source,
                 coverage, atc, ddc, dtc, rin, rout, dispute,
                 a_status, b_status, ab_dispute, excl, ev])

rows.sort(key=lambda r: (r[0], r[3]))

with open("S1_01_CATEGORY_MAPPING.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    w.writerows(rows)
print(f"wrote {len(rows)} subdomain rows -> S1_01_CATEGORY_MAPPING.csv")
print("sum active_taxonomy_count =", sum(r[8] for r in rows))
print("active_observed rows =", sum(1 for r in rows if r[7] == "active_observed"))
print("uncovered_official rows =", sum(1 for r in rows if r[7] == "uncovered_official"))
print("\nreclassified (13):")
for tid, cat, dom, sub in reclassified:
    print(f"  {cat}/{tid.split('/')[-1]} -> {dom}/{sub}")
