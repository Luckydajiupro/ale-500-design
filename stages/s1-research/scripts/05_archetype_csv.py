#!/usr/bin/env python3
"""Generate S1_01_TASK_ARCHETYPE_EVIDENCE.csv — candidate professional task archetypes.

Rows = 49 active-observed subdomains. Software/verifier/OS/example-tasks are aggregated
from evidence/task_archetype_rows.tsv (active tasks only). verifier_impl_class is the
R1 verifier implementation class (E2, review-pending). verification_method is INFERRED
from that class (E3 research hypothesis, not independently confirmed). workflow/input/
deliverable/expertise/unconfirmed are hand-authored archetype summaries grounded in the
task-card `summary` fields (NOT verbatim copies of taskPrompt/reference/scoring content).
professional_workflow, expertise_clues and verification_method are research hypotheses,
not domain-expert-confirmed facts (see research_hypothesis_fields column).
"""
import csv, json, collections

BASE = "/Users/mac/Workspaces/ale-研究设计"
PUB = set(json.load(open(f"{BASE}/agents-last-exam/tasks/published_tasks.json"))['published'].keys())
rows = [r for r in csv.DictReader(open("evidence/task_archetype_rows.tsv"), delimiter="\t")
        if r["task_id"] in PUB and r["domain_code"] != "UNKNOWN"]

g = collections.defaultdict(list)
for r in rows:
    g[(r["domain_code"], r["subdomain_code"])].append(r)

sub_meta = {(r["domain_code"], r["subdomain_code"]): r
            for r in csv.DictReader(open("evidence/taxonomy_subdomains.tsv"), delimiter="\t")}

# hand-authored archetype annotations: (workflow, raw_input, deliverable, expertise, unconfirmed)
A = {
    ("agriculture_env", "env_water"): (
        "Calibrate a staged physical model by editing a small config surface so simulation output matches target observations.",
        "Staged GLM lake-model namelist/config plus calibration target observation data.",
        "Edited namelist + simulation run matching calibration target.",
        "Limnology/hydrology; GLM (General Lake Model) configuration and lake water-quality/thermal calibration.",
        "Only 1 active member (reclassified-in). 2 retired tasks (crop_rotation_d02, ndvi_zonal_statistics_d02) imply a broader agriculture+environment scope currently absent from active set."),
    ("business_finance", "accounting"): (
        "Parse financial filings (SEC 10-K / annual reports) into normalized structured records and extract defined fields.",
        "Filing corpora (PDF/HTML financial reports), extraction schemas.",
        "Normalized financial JSON/CSV records with extracted line items and personnel/disclosure fields.",
        "Accounting standards (US GAAP/SEC forms, China A-share disclosure); financial statement structure; document extraction.",
        "None."),
    ("business_finance", "actuarial_risk"): (
        "Classify operational-risk loss events against a regulatory taxonomy (Basel categories, business lines).",
        "Loss-event tables (Chinese operational-risk events).",
        "Classification results file mapping events to Basel categories.",
        "Basel II/III operational risk; actuarial loss-event classification; Chinese banking regulation.",
        "None."),
    ("business_finance", "compliance"): (
        "Audit artifacts against a published policy or answer regulatory reporting questions from closed-book domain knowledge.",
        "Real policy/artifact corpora (GPT Actions, Chinese regulatory filings, AI-governance documents).",
        "Compliance audit findings / classified documents / reporting answers.",
        "Regulatory compliance (OpenAI policy, China SSE reporting, AI-governance legislation).",
        "None."),
    ("business_finance", "enterprise_analytics"): (
        "Redesign a business workflow in BPMN or build an analytics workbook/dashboard from staged enterprise data.",
        "Staged enterprise datasets + BPMN/analytics tool config; live data services.",
        "BPMN workflow definitions; equity-research workbook; BI dashboards.",
        "Business process modeling (Flowable BPMN); equity research; BI (Metabase).",
        "Some tasks require staged-local live services (Flowable/Metabase)."),
    ("business_finance", "hr_pm"): (
        "Triage support conversations and produce a deterministic structured outcome.",
        "Staged HR/IT support conversation transcripts.",
        "Deterministic results file.",
        "HR/IT support operations; deterministic classification.",
        "None."),
    ("business_finance", "quant_finance"): (
        "Implement a tiered quantitative pricing benchmark (Black-Scholes + extensions).",
        "Pricing specification and market parameters.",
        "Pricing solver output file.",
        "Quantitative finance; option pricing; Monte Carlo/numerical methods.",
        "None."),
    ("business_finance", "sales_marketing"): (
        "Design/analyze marketing experiments (A/B test) and segment customers from transactional data.",
        "Transactional/experiment data.",
        "Analysis results + segmentation cohort output.",
        "Marketing analytics; experiment design; causal inference; segmentation.",
        "None."),
    ("business_finance", "supply_chain"): (
        "Execute a full ERP supply-chain workflow (purchase, landed cost, subcontracting) in Odoo.",
        "Odoo instance + staged product/partner data.",
        "Completed ERP transactions/records.",
        "ERP operations (Odoo); supply-chain and inventory accounting.",
        "Windows + staged-local Odoo/PostgreSQL service."),
    ("computing_math", "software_eng"): (
        "Write or repair deterministic software (C++ test generator; ranking-service node rebuild) to exact spec.",
        "Problem spec / staged codebase.",
        "Compiled program / rebuilt service artifact passing tests.",
        "Software engineering; C++; algorithms; distributed service internals.",
        "A/B candidate: CS subdomain (excluded under both A and B)."),
    ("computing_math", "data_analytics"): (
        "Build data pipelines/warehouses or analyze incident/causal/recommender datasets.",
        "Staged tabular/incident/synthetic datasets.",
        "SQLite warehouse + sidecars; root-cause reports; recommender models.",
        "Data engineering; SQL; causal inference; recommender systems.",
        "A/B candidate: CS subdomain (excluded under both A and B)."),
    ("computing_math", "ai_cs_research"): (
        "Reproduce ML research results or repair/infer model pipeline internals (DiT sampling, checkpoint layout, paper tables).",
        "Staged model code, checkpoints, paper specifications.",
        "Repaired pipeline / inferred layout / reproduced results table.",
        "ML research engineering; diffusion models; distributed training checkpoints; paper reproduction.",
        "A/B candidate: CS subdomain (excluded under both A and B)."),
    ("computing_math", "math_ops_research"): (
        "Implement a mathematical solver/estimator benchmark (game-theory CFR, particle filter).",
        "Mathematical problem specification.",
        "Solver output JSON.",
        "Operations research; game theory; state estimation; numerical optimization.",
        "A/B candidate: KEEP under B (non-CS math/OR)."),
    ("computing_math", "cybersecurity"): (
        "Reverse-engineer malware/keys or triage packet captures with Ghidra/Wireshark.",
        "Bundled binaries, packet captures, crackme targets.",
        "Recovered config/key; triage report; patched binary.",
        "Reverse engineering; malware analysis; network forensics.",
        "A/B candidate: CS subdomain (excluded under both A and B). All Windows."),
    ("computing_math", "infra_cloud"): (
        "Migrate apps to Kubernetes or analyze cloud billing/security posture.",
        "Docker Compose app / AWS billing screenshots / K8s manifests.",
        "Production-grade K8s manifests/Helm; cost/security analysis.",
        "Cloud infrastructure; Kubernetes; Terraform; cost optimization.",
        "A/B candidate: CS subdomain (excluded under both A and B)."),
    ("computing_math", "quantum"): (
        "Reproduce quantum error-correction circuit simulation failure-rate data.",
        "Staged construction notes + simulation grid.",
        "Simulated failure-rate data files.",
        "Quantum error correction; quantum circuit simulation (Stim).",
        "A/B candidate: CS subdomain (excluded under both A and B). DISPUTE: quantum straddles physics and CS."),
    ("education_info", "library_info"): (
        "Remediate legacy library metadata (MARC) and apply cataloging rules via a starter project.",
        "Legacy MARC batches.",
        "Remediated catalog records.",
        "Library/information science; MARC cataloging.",
        "None."),
    ("education_info", "translation"): (
        "Transcribe/translate a classical manuscript glyph (Yi phonetic gloss).",
        "Manuscript image.",
        "Glyph identification/translation output.",
        "Classical Chinese/Yi philology; paleography.",
        "Windows (image viewer)."),
    ("engineering", "aerospace_mech"): (
        "Compute a multi-stage orbital transfer (LEO to GEO).",
        "Orbital mechanics specification.",
        "Transfer trajectory/orbital data.",
        "Orbital mechanics; astrodynamics.",
        "None."),
    ("engineering", "civil_geo"): (
        "Build CAD/BIM geometry or run civil/geotech simulations from disclosed sources.",
        "2D drawings, survey/source data, excavation specs.",
        "Blender/FreeCAD models; road alignment; pit-excavation elevation comparisons.",
        "Civil/structural engineering; CAD (Blender/FreeCAD); geotech (Kratos).",
        "3 active + 1 extra (2d_drawings_to_3d_bridge_model). Some are v1.1 open-source conversions."),
    ("engineering", "electronics"): (
        "Design/simulate/repair electronic circuits (LTspice, KiCad PCB layout).",
        "Circuit schematics/specifications, KiCad projects.",
        "Simulation results; repaired KiCad project; routed PCB.",
        "Electronics; analog circuit design; PCB layout (KiCad); SPICE (LTspice).",
        "All Windows."),
    ("engineering", "energy_power"): (
        "Model building-energy control (MPC cooling) or reconstruct feeder reliability topology.",
        "Building/feeder datasets and specifications.",
        "MPC control plans; feeder topology/reliability model.",
        "Building energy simulation (EnergyPlus); power systems; MPC/optimization (cvxpy).",
        "None."),
    ("engineering", "manufacturing"): (
        "Design safe machining toolpaths (roughing/finishing) in FreeCAD CAM.",
        "Workpiece geometry.",
        "CAM toolpath definitions.",
        "CNC machining; CAM (FreeCAD CAM, LinuxCNC).",
        "None."),
    ("engineering", "robotics"): (
        "Produce deterministic robot locomotion/whole-body-control policies and rollouts.",
        "Robot model + training/rollout environments.",
        "Trained policy; rollout trajectories.",
        "Robotics; reinforcement learning (Isaac Lab/MuJoCo); whole-body control.",
        "GPU tasks (Isaac Sim). 1 reclassified-out (robotics_blender -> visual_media)."),
    ("engineering", "semiconductor"): (
        "Tune/verify chip design flows (Chisel/OpenROAD/Yosys) to pinned toolchain.",
        "Hardware design (Chisel Scala), OpenROAD configs.",
        "Tuned EDA flow config; verified netlist/reports.",
        "Digital design; RTL (Chisel); EDA (OpenROAD/Yosys); semiconductor physical design.",
        "None."),
    ("engineering", "urban_planning"): (
        "Calibrate transport microsimulation (SUMO) or simulate transit passenger trips.",
        "SUMO model packages; AFC demand data; network files.",
        "Calibrated simulation; passenger-trip outputs.",
        "Transport modeling (SUMO); urban planning; travel-demand analysis.",
        "abm_hangzhou_metro reclassified-in from transport_safety (prev: aviation)."),
    ("health_medicine", "clinical_diagnostics"): (
        "Reconstruct/analyze medical imaging (CT, WSI, X-ray) and adjudicate reader annotations.",
        "DICOM/whole-slide images, phantom scans, annotation pairs.",
        "Reconstructed images; radiomics features; adjudicated annotations.",
        "Medical imaging; radiology; radiomics (PyRadiomics); CT reconstruction; WSI (OpenSlide).",
        "Largest asset profile (12.08 GiB nsclc_radiomics). Some Windows (DICOM viewer)."),
    ("health_medicine", "therapeutic_oncology"): (
        "Reproduce radiotherapy plans / ECG benchmark slices / glucose control.",
        "DICOM/ECG/physiology data, plan specifications.",
        "IMRT plan; ECG classification; glucose-control output.",
        "Medical physics (matRad); oncology; ECG; diabetes modeling (SimGlucose).",
        "Contains variant tasks (ptbxl_1386/2263)."),
    ("health_medicine", "clinical_informatics"): (
        "Query synthetic EHR tables (MIMIC-IV style) to identify defined patient cohorts.",
        "Synthetic EHR tables.",
        "Cohort identification results.",
        "Clinical informatics; EHR data; SQL; ICU cohort definition.",
        "1 reclassified-out (causal_ihdp -> social_sciences)."),
    ("health_medicine", "public_health"): (
        "Forecast disease incidence or rebuild epidemiological cohorts from public registries.",
        "Archived surveillance data, public registry (TCGA/NHANES).",
        "Forecast files; survival/sensitivity cohort analyses.",
        "Epidemiology; public health; survival analysis (R); FluSight-style forecasting.",
        "Some online-required (GDC). 1 reclassified-out (ltmle -> social_sciences)."),
    ("health_medicine", "clinical_trials"): (
        "Map CRF/define.xml to SDTM or produce a statistical analysis plan for a Phase III trial.",
        "CRF + define.xml; trial protocol.",
        "Field-mapping CSV; statistical analysis plan package.",
        "Clinical trial operations; SDTM/CDISC mapping; biostatistics (gsDesign/rpact).",
        "None."),
    ("legal", "litigation"): (
        "Review regulatory filings about a transaction and produce a consistency/correctness analysis.",
        "Chinese regulatory filings (share-transfer).",
        "Consistency audit output.",
        "Litigation support; Chinese corporate/securities regulation.",
        "reclassified-in from business_finance."),
    ("legal", "legal_research"): (
        "Compute arbitration institution fees/remuneration per a published schedule.",
        "Fee schedule + case parameters.",
        "Fee calculation output.",
        "Doctrinal legal research; arbitration fee rules (BAC).",
        "1 reclassified-out (agora_governance -> business_finance)."),
    ("life_sciences", "biomolecular"): (
        "Run biomolecular simulation/docking/ensemble-scoring workflows (Amber) and rank results.",
        "PDB structures, docking poses, ensemble models.",
        "Amber workflow bundle; ranked scores; docking evaluations.",
        "Structural biology; molecular dynamics (Amber); docking; IDP scoring.",
        "Reference-only Amber/SLURM/CUDA environment; some Windows."),
    ("life_sciences", "genomics"): (
        "Run variant-calling/differential-expression workflows on real genome/transcriptome data.",
        "FASTQ/reads, expression matrices, clinical annotations.",
        "Variant calls; differential-expression results; genome-browser SVG.",
        "Genomics; NGS variant calling; RNA-seq differential expression.",
        "None."),
    ("life_sciences", "cell_imaging"): (
        "Segment/track cells and run imaging-analysis pipelines (CellProfiler/Cellpose/Scanpy).",
        "Fluorescence microscopy images, MERFISH fields, HDF5/AnnData.",
        "Segmentation/tracking results; quantification tables.",
        "Cell biology; image analysis (CellProfiler/Cellpose); spatial transcriptomics (Squidpy).",
        "None."),
    ("life_sciences", "systems_microbial"): (
        "Implement stochastic simulation (Gillespie/tau-leaping) for a gene regulatory network.",
        "Reaction network specification.",
        "Simulation implementation + trajectories.",
        "Systems biology; stochastic simulation; gene regulatory networks.",
        "reclassified-in from physical_sciences."),
    ("other", "sports"): (
        "Reconstruct a sports record (Go game / aerobics routine) and score it against rules.",
        "Board image/moves, video, rulebook.",
        "Reconstructed game/score sheet.",
        "Go game analysis (Sabaki/sgfmill); sports judging (FIG aerobics).",
        "other is a catch-all domain; membership shifted (mota_exploration out, go_game in)."),
    ("physical_sciences", "physics"): (
        "Compute condensed-matter/lattice properties via exact diagonalization or dynamical matrix.",
        "Hamiltonian/lattice specification.",
        "Eigenvalues/dynamical matrix/phonon output.",
        "Condensed-matter physics; exact diagonalization; lattice dynamics.",
        "None."),
    ("physical_sciences", "chemistry_materials"): (
        "Compute electronic structure (GW band gaps) or reconstruct/extract molecular structures.",
        "Crystal/molecule inputs, paper tables, structure images.",
        "Band-gap data; molecule files (SDF/SMILES); extracted tables.",
        "Computational chemistry (Quantum ESPRESSO, BerkeleyGW); cheminformatics (RDKit, Ketcher).",
        "2 reclassified-out to life_sciences; 3 Windows (Ketcher)."),
    ("physical_sciences", "astronomy"): (
        "Implement an astronomical imaging reduction workflow (HST ACS/WFC).",
        "Synthetic HST imaging data.",
        "Reduced science images/photometry.",
        "Astronomy; image reduction (Astropy, Photutils).",
        "None."),
    ("physical_sciences", "earth_atmo"): (
        "Build a climate-emulation pipeline from CMIP6-derived data.",
        "CMIP6-derived Zarr store.",
        "Emulator model + predictions.",
        "Climate science; earth-system emulation (xarray, PyTorch).",
        "1 reclassified-out (glm_lake -> agriculture_env)."),
    ("psychology_neuro", "comp_neuro"): (
        "Complete sparse whole-brain neuron trajectories in HDF5 recording.",
        "Staged HDF5 neural recording.",
        "Completed trajectories.",
        "Computational neuroscience; neural data (HDF5); trajectory completion.",
        "1 reclassified-out (reddit_ai_post -> social_sciences)."),
    ("psychology_neuro", "exp_psychology"): (
        "Resample an ROI mask onto a statistical-map grid for neuroimaging alignment.",
        "ROI mask + statistical map.",
        "Resampled mask file.",
        "Neuroimaging; fMRI data processing.",
        "None."),
    ("social_sciences", "economics"): (
        "Run econometric/causal-inference pipelines (IHDP/LMTP) or code survey annotations.",
        "Semi-synthetic benchmark data; codebooks; survey texts.",
        "Inference script; simulation pipeline; coded annotations.",
        "Econometrics; causal inference (SuperLearner, lmtp); survey coding.",
        "3 reclassified-in from health/psych; only 1 task in its own directory."),
    ("transport_safety", "fire_safety"): (
        "Reconstruct a fire/smoke simulation (FDS) CLI for a single-compartment scenario.",
        "FDS input deck / scenario spec.",
        "FDS/Smokeview simulation output.",
        "Fire safety engineering; CFD (FDS).",
        "abm_hangzhou_metro reclassified-out to engineering/urban_planning; transport_safety also has an unobserved 'aviation' leaf (from reclassification history)."),
    ("visual_media", "animation_3d"): (
        "Build/repair 3D scenes, models, or engine ports (Blender/Godot/Gaussian Splatting) with GPU.",
        "Floor plans, source scenes, graybox assets, Flash/motion data.",
        "Blender/Godot scenes; exported models/level blockouts.",
        "3D modeling (Blender); game engine (Godot); motion/asset capture; Gaussian Splatting.",
        "Largest Windows+GPU concentration; 4 extra unreleased cards; 2 reclassified-in."),
    ("visual_media", "graphic_design"): (
        "Rebuild a flattened one-pager as an editable single-slide deck.",
        "Flattened one-pager image.",
        "Editable PPTX.",
        "Graphic design; presentation editing (LibreOffice Impress).",
        "reclassified-in from business_finance."),
    ("visual_media", "audio_music"): (
        "Transcribe a score, replace instruments in a project, or produce a continuity log.",
        "Recorded orchestration, source project files, film.",
        "Native MuseScore score; Ardour project; DOCX continuity log.",
        "Music transcription (MuseScore); audio post-production (Ardour); film continuity.",
        "v1.1 open-source conversions (MuseScore, Ardour)."),
}

cols = ["domain_code", "subdomain_code", "subdomain_name", "example_task_ids",
        "professional_workflow", "raw_input_type", "expected_deliverable",
        "verifier_impl_class", "verification_method", "software_environment",
        "runtime_environment", "expertise_clues", "research_hypothesis_fields",
        "evidence_location", "unconfirmed_items"]

# verifier implementation class -> inferred verification method (E3, not confirmed)
VERIFIER_METHOD = {
    "scorer": "score-based output comparison",
    "checker": "assertion/check-based validation",
    "hook-evaluator": "runtime hook evaluation",
    "evaluator": "evaluator-based assessment",
    "script": "script-based validation",
}

HYPOTHESIS_FIELDS = "professional_workflow;expertise_clues;verification_method"

out = []
for (dom, sub), rs in sorted(g.items()):
    meta = sub_meta[(dom, sub)]
    name = meta["subdomain_name"]
    tids = sorted(r["task_id"] for r in rs)
    sw = sorted({x for r in rs for x in r["software"].split(";") if x})
    ver = collections.Counter(r["r1_verifier_type"] for r in rs if r["r1_verifier_type"])
    impl = ",".join(f"{k}={v}" for k, v in sorted(ver.items())) or "UNKNOWN"
    method = ";".join(sorted({VERIFIER_METHOD[v] for v in ver if v in VERIFIER_METHOD})) or "UNKNOWN"
    osc = []
    linux = sum(1 for r in rs if r["r1_os_linux"] == "yes")
    win = sum(1 for r in rs if r["r1_os_windows"] == "yes")
    mt = sorted({r["vm_machineType"] for r in rs if r["vm_machineType"] != "UNKNOWN"})
    ext = sorted({r["r1_external_service"] for r in rs if r["r1_external_service"] and r["r1_external_service"] != "none"})
    rt = f"vm={','.join(mt) or 'UNKNOWN'}; linux={linux}; windows={win}"
    if ext:
        rt += f"; external_service={','.join(ext)}"
    wf, inp, dlv, exp, unc = A[(dom, sub)]
    ev = f"agents-last-exam/tasks/{dom}/*/task_card.json; R1 04_task_inventory.csv"
    out.append([dom, sub, name, ";".join(tids), wf, inp, dlv,
                impl, method, ";".join(sw) or "UNKNOWN", rt, exp,
                HYPOTHESIS_FIELDS, ev, unc])

with open("S1_01_TASK_ARCHETYPE_EVIDENCE.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    w.writerows(out)
print(f"wrote {len(out)} archetype rows -> S1_01_TASK_ARCHETYPE_EVIDENCE.csv")
print("total example tasks:", sum(len(r[3].split(';')) for r in out if r[3]))
