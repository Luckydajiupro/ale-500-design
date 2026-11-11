#!/usr/bin/env python3
"""Build S1-02A revision artifacts from the original CSV + revision judgment.

Generates:
- S1_02A_SOURCE_CLAIM_MAP.csv  (external source -> specific claim -> what it proves)
- S1_02A_DUPLICATE_ATTRIBUTION.csv  (the 3 duplicate-pair verdicts)

The judgment below is the S1-02A revision round's re-classification of the 51
candidates produced in the first batch. It does NOT overwrite the original
S1_02A_WORKFLOW_CANDIDATES.csv; it adds a revision layer.

evidence_kind (4-way, per review task 1):
  industry_standard_complete  - a non-vendor source directly documents the full
                                input -> operations -> product -> success workflow
  tool_existence              - the source proves a tool exists / has features,
                                but does NOT document the complete workflow
  agent_inferred_combination  - no single source documents the workflow; the LLM
                                combined tool/step knowledge into a workflow
  expert_pending_proposal     - no source; LLM hypothesis needing expert confirmation

source_category (what the source actually is):
  government / government_tool_page / academic / professional_society /
  vendor_doc / vendor_blog / industry_media / search_snippet / citation_only / none

software_adaptation (5-way, per review task 4) for the primary dependency:
  native / conditional / partial_function_replacement / needs_task_redesign /
  unverified_or_unavailable
"""
import csv, json

WC = list(csv.DictReader(open("S1_02A_WORKFLOW_CANDIDATES.csv", encoding="utf-8")))
BY_ID = {r["candidate_id"]: r for r in WC}

# --- revision judgment: per candidate_id -----------------------------------
# key order matters for readability; fields optional except evidence_kind.
REV = {
    # aerospace_mech
    "eng_aerospace_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="government",
        adaptation="native",
        note="NASA technical report + TFAWS paper document the sizing workflow; E3 (not full-read this round)."),
    "eng_aerospace_wf02": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        note="ASEE industry-perspective paper documents the FEA margin workflow; E3."),
    "eng_aerospace_wf03": dict(
        evidence_kind="expert_pending_proposal",
        source_category="none",
        adaptation="partial_function_replacement",
        note="E4: no source this round; GD&T stack-up inferred from standard practice; MUST be expert-confirmed (ASME Y14.5)."),
    # electronics
    "eng_electronics_wf01": dict(
        evidence_kind="tool_existence",
        source_category="vendor_doc",
        adaptation="partial_function_replacement",
        note="Altium Designer documentation proves the tool's high-speed features, NOT that the SI workflow is industry-standard. Downgraded from industry_supported."),
    "eng_electronics_wf02": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="unverified_or_unavailable",
        note="ETH VLSI exercise documents the scan+ATPG workflow, but it is IC-level: MIS-ATTRIBUTED to electronics/PCB; it belongs to semiconductor. Platform claim 'OpenROAD ... ATPG' is WRONG: OpenROAD has scan insertion but no production ATPG. See duplicate attribution."),
    "eng_electronics_wf03": dict(
        evidence_kind="agent_inferred_combination",
        source_category="vendor_doc",
        adaptation="native",
        note="passive-components.eu snippet covers only inductor selection; the full DC-DC spec-to-verified-design workflow is inferred, not directly sourced."),
    # civil_geo
    "eng_civilgeo_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="government",
        adaptation="native",
        note="National Academies chapter documents acquisition-to-DEM lifecycle; E1."),
    "eng_civilgeo_wf02": dict(
        evidence_kind="tool_existence",
        source_category="government_tool_page",
        adaptation="conditional",
        note="HEC-RAS software page proves the tool; the floodplain workflow is standard but the source is a tool page. Windows GUI is official; Linux is third-party Docker/Apptainer compute engine only. Duplicate of ag_envwater_wf03."),
    "eng_civilgeo_wf03": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        note="Zenodo paper documents EPANET distribution modeling; E3. Duplicate of ag_envwater_wf04."),
    "eng_civilgeo_wf04": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="partial_function_replacement",
        note="ETABS paper documents building analysis; ETABS/SAP2000 are Windows proprietary; open alternatives (OpenSees) cover the solver, not the full modeling UI."),
    # chemical_process
    "eng_chemproc_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        note="DWSIM distillation tutorial read in full; E1. DWSIM is a free native-Linux alternative to Aspen."),
    "eng_chemproc_wf02": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        note="HAZOP source read in full; E1."),
    "eng_chemproc_wf03": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="partial_function_replacement",
        evidence_level_override="E1",
        source_type_override="industry_supported",
        source_url_override="https://eng.libretexts.org/Bookshelves/Chemical_Engineering/Foundations_of_Chemical_and_Biological_Engineering_I_(Verret_Qiao_Barghout)/01%3A_Introduction_to_Chemical_Processes_and_Process_Diagrams",
        note="E1 UPGRADED (subagent 17b3ac80): UBC/BCcampus OER textbook (LibreTexts, CC BY-NC-SA) documents the complete PFD->P&ID workflow in §1.5-1.8; §1.8 'Building a PFD' is a literal written-description->diagram exercise. Aspen/HYSYS are Windows proprietary; DWSIM is a partial substitute."),
    # manufacturing
    "eng_manufacturing_wf01": dict(
        evidence_kind="tool_existence",
        source_category="vendor_blog",
        adaptation="partial_function_replacement",
        note="3d-scantech.com vendor blog proves scanning tools; the scan-to-decision workflow is industry practice but the source is vendor marketing. Downgraded from industry_supported."),
    "eng_manufacturing_wf02": dict(
        evidence_kind="tool_existence",
        source_category="vendor_blog",
        adaptation="partial_function_replacement",
        note="Flowfuse blog (an IIoT vendor, not an SPC vendor) covers SPC-chart automation; proves the technique exists, not a full industry workflow. Downgraded. Minitab is Windows desktop + Web App, not Linux-native."),
    "eng_manufacturing_wf03": dict(
        evidence_kind="industry_standard_complete",
        source_category="search_snippet",
        adaptation="native",
        note="Cp/Cpk + tolerance stack-up is unambiguous industry standard; source is a ScienceDirect abstract (E3)."),
    # energy_power
    "eng_energypower_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="search_snippet",
        adaptation="native",
        note="Load-flow/DER workflow is standard; source is a ScienceDirect snippet (E3)."),
    "eng_energypower_wf02": dict(
        evidence_kind="industry_standard_complete",
        source_category="search_snippet",
        adaptation="native",
        note="SAIDI/SAIFI reliability is standard (IEEE 1366); source is a ScienceDirect snippet (E3)."),
    "eng_energypower_wf03": dict(
        evidence_kind="expert_pending_proposal",
        source_category="none",
        adaptation="native",
        note="E4: no direct M&V source this round; MUST be expert-confirmed and grounded in ASHRAE Guideline 14."),
    "eng_energypower_wf04": dict(
        evidence_kind="industry_standard_complete",
        source_category="search_snippet",
        adaptation="native",
        note="MSR fuel-cycle/thermal-hydraulics is standard; source is an NSTL abstract (E3)."),
    # mining_petroleum (all E3)
    "eng_mining_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="vendor_doc",
        adaptation="native",
        evidence_level_override="E1",
        source_url_override="https://manual.whitson.com/modules/well-performance/decline-curve-analysis/index.html",
        note="E1 UPGRADED (subagent 85b6043b): whitson+ user manual read in full documents the complete Arps DCA workflow (input params -> b/qi/Di theory -> autofit -> EUR export to ARIES/PHDwin). Arps DCA is the textbook industry standard; source is a vendor manual (vendor_doc) but the method is standard and the workflow fully documented."),
    "eng_mining_wf02": dict(
        evidence_kind="industry_standard_complete",
        source_category="vendor_doc",
        adaptation="partial_function_replacement",
        evidence_level_override="E1",
        source_url_override="https://manual.whitson.com/modules/well-performance/analytical_rta/index.html",
        note="E1 UPGRADED (subagent 85b6043b): whitson+ 'Classical RTA' manual read in full documents material-balance-time -> Bourdet derivative -> flow-regime ID -> parameter estimation -> forecast. KAPPA is Windows proprietary; Python is a partial substitute."),
    "eng_mining_wf03": dict(
        evidence_kind="industry_standard_complete",
        source_category="vendor_doc",
        adaptation="partial_function_replacement",
        evidence_level_override="E1",
        source_url_override="http://filesnj.carlsonsw.com/mirror/manuals/Carlson_2007/online/source/Geology/Block_Model/Optimized_Pit_Design/Optimized_Pit_Design.html",
        note="E1 UPGRADED (subagent 85b6043b): Carlson Software 'Optimized Pit Design' manual read in full documents the complete Lerchs-Grossmann algorithm (13 steps) + cyclic production scheduling from a block model. LG is the textbook industry standard."),
    "eng_mining_wf04": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="partial_function_replacement",
        evidence_level_override="E1",
        source_url_override="https://geoengineer.org/education/slope-stability/slope-stability-the-bishop-method-of-slices",
        note="E1 UPGRADED (subagent 85b6043b): GeoEngineer.org 'Bishop Method of Slices' read in full documents the limit-equilibrium method-of-slices FoS workflow. NOTE: source covers Bishop specifically; Morgenstern-Price (the generalized sibling in the candidate title) is NOT covered by name — M-P needs separate E1 evidence."),
    "eng_mining_wf05": dict(
        evidence_kind="industry_standard_complete",
        source_category="government",
        adaptation="partial_function_replacement",
        evidence_level_override="E1",
        source_url_override="https://geocom.geonardo.com/assets/elearning/2.47.Session-IV-JDVW_hydraulicfraccing.pdf",
        note="E1 UPGRADED (subagent 85b6043b): BRGM/GFZ 'EGS Technology: hydraulic fraccing' 73-page national-geoscience training deck read in full documents frac geometry -> proppant placement -> productivity design workflow."),
    # semiconductor
    "eng_semiconductor_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="search_snippet",
        adaptation="native",
        note="STA/signoff is standard; source is an ACM snippet (E3). OpenSTA/Magic are native-Linux partial substitutes for PrimeTime."),
    "eng_semiconductor_wf02": dict(
        evidence_kind="industry_standard_complete",
        source_category="search_snippet",
        adaptation="partial_function_replacement",
        note="Logic synthesis is standard; source is an ebook record (E3), not read content. Yosys is a partial substitute for Design Compiler."),
    "eng_semiconductor_wf03": dict(
        evidence_kind="expert_pending_proposal",
        source_category="none",
        adaptation="unverified_or_unavailable",
        note="E4: no source; DFT/ATPG inferred. Open-source ATPG is NOT a verified full commercial equivalent. Duplicate of eng_electronics_wf02."),
    # urban_planning
    "eng_urban_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="search_snippet",
        adaptation="native",
        note="Signal timing/optimization is standard; source is a TRB + ScienceDirect snippet (E3). SUMO is native Linux."),
    "eng_urban_wf02": dict(
        evidence_kind="agent_inferred_combination",
        source_category="citation_only",
        adaptation="native",
        note="Source is only a Google Scholar citation (no content read); the specific multi-criteria suitability workflow is inferred, not directly sourced."),
    "eng_urban_wf03": dict(
        evidence_kind="expert_pending_proposal",
        source_category="none",
        adaptation="native",
        note="E4: no source; four-step demand model inferred; MUST be expert-confirmed."),
    # robotics
    "eng_robotics_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        note="Arxiv full text (LimX) read this round; research-grade (not yet industry-standard) but complete train-to-evaluate workflow. GPU/CUDA required."),
    "eng_robotics_wf02": dict(
        evidence_kind="tool_existence",
        source_category="vendor_doc",
        adaptation="native",
        note="MoveIt Task Constructor tutorial (GitHub fetch failed, E3) proves the tool's pick-and-place capability; the multi-stage workflow is tool-documented, not independently sourced."),
    "eng_robotics_wf03": dict(
        evidence_kind="industry_standard_complete",
        source_category="search_snippet",
        adaptation="native",
        note="Grasp synthesis is standard research; source is an IEEE snippet (E3)."),
    # env_water
    "ag_envwater_wf01": dict(
        evidence_kind="tool_existence",
        source_category="government_tool_page",
        adaptation="native",
        note="EPA SWMM page documents the tool (authoritative); the build-calibrate-design workflow is standard but not step-documented on that page. SWMM engine is native Linux."),
    "ag_envwater_wf02": dict(
        evidence_kind="tool_existence",
        source_category="government_tool_page",
        adaptation="native",
        note="USGS MODFLOW 6 page documents the tool; the conceptual-to-calibrated workflow is standard but the source is a tool page."),
    "ag_envwater_wf03": dict(
        evidence_kind="tool_existence",
        source_category="government_tool_page",
        adaptation="conditional",
        note="HEC-RAS/HEC-HMS manual documents the tools (Windows-centric); Linux is third-party Docker/Apptainer compute engine only. Duplicate of eng_civilgeo_wf02."),
    "ag_envwater_wf04": dict(
        evidence_kind="tool_existence",
        source_category="government_tool_page",
        adaptation="native",
        note="EPA EPANET page documents the tool; the workflow is standard but the source is a tool page. EPANET engine + wntr/epyt are native Linux. Duplicate of eng_civilgeo_wf03."),
    # precision_agriculture
    "ag_precision_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        evidence_level_override="E1",
        source_url_override="https://adamchukpa.mcgill.ca/manifold/lesson_3.html",
        note="E1 UPGRADED (subagent 32bf7819): McGill Manifold Lesson 3 read in full + Cornell Fact Sheet #107 + Nebraska EC2005 document the complete yield-log clean -> delay-adjust -> filter -> interpolate -> classify -> map workflow."),
    "ag_precision_wf02": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        evidence_level_override="E1",
        source_url_override="https://pmc.ncbi.nlm.nih.gov/articles/PMC8779988/",
        note="E1 UPGRADED (subagent 32bf7819): Javadi/Guerrero/Mouazen Sensors 2022 (doi 10.3390/s22020645, open access) read in full; documents the CaSP pipeline (normalize -> feature-select -> k-means -> DBSCAN smoothing) with quantitative success indices (VRI/DBI/Silhouette)."),
    "ag_precision_wf03": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="conditional",
        evidence_level_override="E1",
        source_url_override="https://adamchukpa.mcgill.ca/manifold/lesson_5.html",
        note="E1 UPGRADED (subagent 32bf7819): McGill Manifold Lesson 5 + Adamchuk ArcGIS Pro tutorial read in full; documents rate-rule -> prescription map -> controller-ready file (shapefile OR proprietary binary). Controller compatibility is conditional (proprietary binary possible)."),
    "ag_precision_wf04": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="conditional",
        evidence_level_override="E1",
        source_url_override="https://www.genomes2fields.org/docs/publications/csc2.20857.pdf",
        note="E1 UPGRADED (subagent 32bf7819): Win et al. Crop Science 2023 (doi 10.1002/csc2.20857, CC-BY) read in full; documents APSIM setup -> sensitivity -> stepwise calibration -> NRMSE/R2 validation -> GxE scenario. APSIM needs registration (conditional)."),
    "ag_precision_wf05": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        note="Virginia Tech extension read this round; E1."),
    # litigation
    "legal_litigation_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="professional_society",
        adaptation="partial_function_replacement",
        note="EDRM model is the industry-standard lifecycle; UK gov PDF is a second source (E3, EDRM page truncated). Relativity/Everlaw are proprietary; Python pipeline is a partial substitute."),
    "legal_litigation_wf02": dict(
        evidence_kind="tool_existence",
        source_category="vendor_doc",
        adaptation="partial_function_replacement",
        note="Everlaw support doc proves the tool's privilege-log feature; the workflow is tool-documented, not independently sourced. Downgraded from industry_supported."),
    "legal_litigation_wf03": dict(
        evidence_kind="tool_existence",
        source_category="vendor_doc",
        adaptation="partial_function_replacement",
        note="Lighthouse + Everlaw vendor blogs/docs prove TAR tooling; the workflow is tool-documented. Downgraded from industry_supported."),
    "legal_litigation_wf04": dict(
        evidence_kind="industry_standard_complete",
        source_category="professional_society",
        adaptation="native",
        note="ABA witness-preparation article documents the pre-trial work product; E3 (truncated). Output is partly subjective (expert grading for substance)."),
    # legal_research
    "legal_research_wf01": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="native",
        note="IRAC memo drafting is standard legal writing; UT Austin + Clio sources (E3, partial fetch). Substance needs expert grading."),
    "legal_research_wf02": dict(
        evidence_kind="industry_standard_complete",
        source_category="government",
        adaptation="native",
        note="LOC legislative-history guide read in full; E1."),
    "legal_research_wf03": dict(
        evidence_kind="industry_standard_complete",
        source_category="government",
        adaptation="native",
        note="Statutory-interpretation canons are standard; LOC guide + BASL handbook (E3); canon list partly E4 pending expert confirm."),
    "legal_research_wf04": dict(
        evidence_kind="industry_standard_complete",
        source_category="academic",
        adaptation="partial_function_replacement",
        note="Shepard's/KeyCite citator is standard; UC Law + UW sources (E3). CourtListener is a partial public-graph substitute, not a full citator."),
}

# --- duplicate-pair verdicts (review task 2) --------------------------------
DUP = [
    dict(
        pair="HEC-RAS floodplain (civil_geo vs env_water)",
        candidates="eng_civilgeo_wf02 vs ag_envwater_wf03",
        substantively_duplicate="YES",
        primary_home="env_water (ag_envwater_wf03)",
        primary_reason="Full hydrologic-hydraulic floodplain modeling (HEC-HMS rainfall-runoff + HEC-RAS routing + delineation) is a water-resources management function; env_water's candidate is the broader, complete lifecycle.",
        secondary_tag="civil_geo (eng_civilgeo_wf02) -> retag as 'hydraulic design for civil infrastructure (bridge/culvert/levee sizing, scour, backwater)'",
        difference_basis="Input: design discharge vs basin rainfall-runoff. Operations: HEC-RAS only vs HEC-HMS+HEC-RAS. Product: structure hydraulic parameter vs flood-extent map. Success: structure capacity vs map accuracy.",
        pending="Expert confirms the civil-infrastructure vs water-management boundary; confirm both stay as distinct workflows (not merged).",
    ),
    dict(
        pair="EPANET distribution (civil_geo vs env_water)",
        candidates="eng_civilgeo_wf03 vs ag_envwater_wf04",
        substantively_duplicate="YES",
        primary_home="env_water (ag_envwater_wf04)",
        primary_reason="Water-distribution network modeling/calibration is a water-utility management function; env_water has the stronger source (E1 EPA page).",
        secondary_tag="civil_geo (eng_civilgeo_wf03) -> retag as 'distribution-network DESIGN for new development (pipe sizing)'",
        difference_basis="Weak: design-context (new-network sizing) vs operations-context (existing-network calibration). Both are EPANET hydraulic modeling. This pair is the NEAREST to a true merge.",
        pending="HIGH: near-duplicate. Expert decides merge (single home env_water + civil_geo secondary tag) vs keep-split on the design/operation distinction.",
    ),
    dict(
        pair="DFT scan/ATPG (electronics vs semiconductor)",
        candidates="eng_electronics_wf02 vs eng_semiconductor_wf03",
        substantively_duplicate="YES",
        primary_home="semiconductor (eng_semiconductor_wf03)",
        primary_reason="Scan insertion + ATPG is IC/chip-level design activity; it belongs to the semiconductor domain, not electronics/PCB.",
        secondary_tag="electronics (eng_electronics_wf02) -> RE-ATTRIBUTE to semiconductor, or reframe as board-level boundary-scan (IEEE 1149.1 JTAG), which is the distinct electronics-domain testability workflow",
        difference_basis="Chip testability (scan/ATPG, IC-level) vs board testability (JTAG boundary-scan, PCB-level). eng_electronics_wf02 as currently framed (scan/ATPG) is mis-attributed to electronics.",
        pending="Expert confirms the electronics/semiconductor testability split. eng_electronics_wf02 also has a WRONG platform claim: 'OpenROAD ... ATPG' — OpenROAD has scan insertion, not production ATPG.",
    ),
]

# --- software-environment corrections (review task 3) -----------------------
SOFTWARE_ENV_CORRECTIONS = [
    dict(
        tool="HEC-RAS",
        original_claim="Windows (primary) or Linux via Wine / 'run headlessly (HEC-RAS CLI)'",
        corrected="Official HEC-RAS is Windows (Intel PC) GUI + 64-bit compute engine only. There is NO official native Linux build. Headless/Linux is third-party: Docker (rascommander/hec-ras-linux-unsteady_6.6) and Apptainer/Slurm run the 2D unsteady compute engine without the Windows GUI.",
        adaptation="conditional",
        affected="eng_civilgeo_wf02, ag_envwater_wf03",
    ),
    dict(
        tool="Minitab",
        original_claim="Minitab (proprietary)",
        corrected="Minitab Statistical Software is a Windows desktop app AND has a Web App (browser). It is NOT Linux-native. Open-source Python/R cover the statistics (partial), not Minitab's exact workflow.",
        adaptation="partial_function_replacement",
        affected="eng_manufacturing_wf02",
    ),
    dict(
        tool="OpenROAD DFT / open-source ATPG",
        original_claim="OpenROAD or Synopsys TestMAX (eng_electronics_wf02) treats OpenROAD as an ATPG path",
        corrected="OpenROAD has a src/dft scan-insertion flow but NO production automatic-test-pattern-generation (ATPG). DFT/ATPG is 'the crucial gap in open-source chip design' (WIOWIZ). Open-source ATPG (TestVector/Atalanta/Quaigh) is not a verified full commercial TetraMAX/TestMAX equivalent.",
        adaptation="unverified_or_unavailable",
        affected="eng_electronics_wf02, eng_semiconductor_wf03",
    ),
    dict(
        tool="EPANET vs HEC-RAS",
        original_claim="both treated as 'hydraulic modeling' and implicitly substitutable",
        corrected="EPANET models pressurized water-distribution networks (demand-driven node/pump/tank); HEC-RAS models open-channel river/flood hydraulics (gravity-driven). Different physics, NOT mutually substitutable.",
        adaptation="n/a",
        affected="eng_civilgeo_wf02/wf03, ag_envwater_wf03/wf04",
    ),
]

# --- emit SOURCE_CLAIM_MAP --------------------------------------------------
def first_url(s):
    if not s:
        return ""
    return s.split(";")[0].split(" and ")[0].strip()

SC = []
for r in WC:
    cid = r["candidate_id"]
    j = REV.get(cid, {})
    SC.append(dict(
        candidate_id=cid,
        subdomain_code=r["subdomain_code"],
        workflow_title=r["workflow_title"],
        source_url=first_url(j.get("source_url_override", r["source_reference"])),
        source_category=j.get("source_category", ""),
        evidence_kind=j.get("evidence_kind", ""),
        evidence_level=j.get("evidence_level_override", r["evidence_level"]),
        source_type=j.get("source_type_override", r["source_type"]),
        software_adaptation=j.get("adaptation", ""),
        correction_note=j.get("note", ""),
    ))

# validation: every candidate classified
missing = [r["candidate_id"] for r in WC if r["candidate_id"] not in REV]
if missing:
    raise SystemExit(f"UNCLASSIFIED candidates: {missing}")

with open("S1_02A_SOURCE_CLAIM_MAP.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(SC[0].keys()))
    w.writeheader()
    w.writerows(SC)

with open("S1_02A_DUPLICATE_ATTRIBUTION.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(DUP[0].keys()))
    w.writeheader()
    w.writerows(DUP)

from collections import Counter
ek = Counter(s["evidence_kind"] for s in SC)
sc = Counter(s["source_category"] for s in SC)
sa = Counter(s["software_adaptation"] for s in SC)
print(f"SOURCE_CLAIM_MAP rows={len(SC)}")
print(f"evidence_kind={dict(ek)}")
print(f"source_category={dict(sc)}")
print(f"software_adaptation={dict(sa)}")
print("DUPLICATE_ATTRIBUTION rows=3")
