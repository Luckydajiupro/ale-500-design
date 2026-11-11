# S1-02B3 research brief (vm_cluster / ts_cluster / edu_cluster)

## 0. Mission

S1-02B3 studies the remaining nine official subdomains of three formal domains
(visual_media #8, transport_safety #10, education_info #11). The deliverable is a
set of candidate *professional workflows* that a domain expert could later review
and an engineer could later run on Linux. This is not S1-02C, not quota work, not
expert recruitment.

The point is professional realism. A candidate must be the kind of multi-step
task a working professional is paid to deliver, with a real input bundle, real
tool and licence dependencies, a concrete artifact, and success criteria a third
party can check. "Use software X" is not a workflow. A tutorial is not a
workflow. A single benchmark operation (reconstruct one mesh, transcribe one
melody) is not a workflow.

Non-negotiables:

- Write only `evidence/s1_02b3_research/<stem>_candidates.csv` and
  `evidence/s1_02b3_research/<stem>.json`. A build helper under
  `.audit/s1-02b3-build/` and a source log under `.audit/` are allowed.
- Never touch the six S1_02B3 final deliverables, `scripts/28-33`, Phase 0,
  S1-01, S1-02A, S1-02B1, S1-02B2, or `S1_02B2_EFFECTIVE_CANDIDATES.csv`.
- No external contact, no emails, no recruitment, no quota numbers.
- Do not copy an official benchmark task. Do not produce near-duplicates of an
  existing A / B1 / B2 candidate (grep the three CSVs to check names and scope).

## 1. Row budget

- 3-5 candidates per subdomain. 3 is the target, 5 is the hard cap.
- Fewer than 3 is allowed only when the evidence genuinely does not support a
  third professional workflow. Then explain it in the JSON `coverage_notes`.
  Never pad, never split one workflow into variants, never rename the same work.
- At least 1 per subdomain. A missing subdomain fails the batch.

## 2. Exact CSV format

UTF-8, one header row, one row per candidate. Use Python's `csv` module
(`csv.writer`) so quoting is correct. No newline inside a cell. The header must
be exactly these 43 columns in this order:

```
subdomain_code,subdomain_business_boundary,subdomain_occupations,candidate_id,workflow_title,occupation_scope,workflow_summary,source_type,evidence_level,source_reference,expert_raw_materials,usage_permissions,task_input,professional_operations,expected_deliverable,success_criteria,verification_approach,platform_dependencies,blocking_risks,expert_capability,cross_domain_overlap,granularity_check,pending_confirmation,data_usage_authorization,privacy_considerations,research_ethics,reproducibility_assessment,evidence_kind,source_category,primary_source_url,primary_claim,software_adaptation,linux_verification_state,expert_pending,engineering_pending,fragment_path,duplicate_status,primary_home,secondary_tag,source_support_mode,evidence_scope,workflow_family_id,process_incident
```

Rules:

- The seven columns `linux_verification_state, expert_pending,
  engineering_pending, fragment_path, duplicate_status, primary_home,
  secondary_tag` must be empty strings. The merge script fills them.
- `candidate_id` = slug + `_wfNN`, NN two digits, unique inside the fragment.
  Slugs: animation_3d=vm_anim, graphic_design=vm_gra, audio_music=vm_aud,
  aviation=ts_avi, maritime_port=ts_mar, fire_safety=ts_fir,
  educational_technology=edu_edt, library_info=edu_lib, translation=edu_trn.
- `subdomain_code`, `subdomain_business_boundary`, `subdomain_occupations`
  repeat the same text on every row of that subdomain.
- `workflow_title` is English so the cross-batch title scan is meaningful. Every
  other column is Chinese unless the value is a code, a standard name, a file
  format, or a URL.

## 3. Enumerations (hard gates, no substitutes)

- `evidence_kind`: industry_standard_complete | tool_existence |
  agent_inferred_combination | expert_pending_proposal
- `evidence_level`: E1 | E3 | E4. **E2 is banned.**
- `source_type`: industry_supported | project_proposal
- `software_adaptation`: native | partial_function_replacement | conditional |
  unverified_or_unavailable | needs_task_redesign
- `source_support_mode`: recorded_full_support | recorded_partial_support |
  verified_support | conditional_support | name_reference_support |
  uncited_support | judgment_support | unspecified_support
- `evidence_scope` statuses: as_recorded | verified_E1 | conditional_E1 |
  name_reference | uncited | expert_judgment | not_specified_by_code
- `workflow_family_id`: one or more `fc_...` codes joined by commas, non-empty.
- `process_incident`: `none` or `inc:<short note>` (no semicolon, <=120 chars).

## 4. Evidence semantics (this is where batches usually break)

`evidence_level` is the strength of the original evidence. `source_support_mode`
is what the cited source actually supports. `software_adaptation` is only the
tool/environment state. These are three different vocabularies. Never put a
tool state into the support field or the reverse.

`evidence_scope` is a semicolon list of `step=status(source)`, for example
`story_breakdown=as_recorded;shot_animation=conditional_E1(ISO 17100:2015 3.1);render_qc=expert_judgment`.
Step names are the snake_case names of the `professional_operations` steps.

Binding rules the checker enforces:

1. `recorded_full_support` means only "the original record claimed full support".
   Its scope may contain nothing but `as_recorded`. It never means verified.
2. A `verified_E1` block requires `verified_support`, and `verified_support`
   needs at least one `verified_E1` block and no `conditional_E1`.
3. A `conditional_E1` block requires `conditional_support`, and
   `conditional_support` needs at least one `conditional_E1` block and no
   `verified_E1`.
4. `recorded_partial_support` must contain no `verified_E1` and no
   `conditional_E1` blocks.
5. Weak modes are exclusive: `name_reference_support` needs a `name_reference`
   block; `uncited_support` needs `uncited`; `judgment_support` needs
   `expert_judgment`; `unspecified_support` needs `not_specified_by_code`. A
   weak-mode scope may contain only `as_recorded` plus its own token.
6. `E4` if and only if `evidence_kind=expert_pending_proposal`, and E4 requires
   `source_type=project_proposal`. E1 never pairs with `project_proposal`.
7. `industry_standard_complete` cannot rest on `source_category` vendor_doc,
   vendor_blog, or government_tool_page.
8. Only claim `verified_E1` or `conditional_E1` when you actually opened the
   clause/page and the claim is stated there. A paywalled landing page supports
   `name_reference`, not `conditional_E1`.

Decision table (use it, do not invent other combinations):

| Situation | level | kind | source_type | mode | scope shape | category |
|---|---|---|---|---|---|---|
| One authoritative standard/regulation prescribes the workflow's duties end to end, and you read the clauses | E1 | industry_standard_complete | industry_supported | conditional_support | step=conditional_E1(doc clause) for clause-backed steps; rest as_recorded | professional_standard / regulatory_document |
| A standard covers the core steps but not the artifact-level method, or you read only part | E3 | industry_standard_complete | industry_supported | conditional_support | clause-backed steps conditional_E1; method steps as_recorded | professional_standard / regulatory_document |
| You combine several authoritative industry sources into one workflow | E3 | agent_inferred_combination | industry_supported | recorded_partial_support | step=as_recorded mostly; tool facts name_reference | professional_standard / industry_report / professional_body_factsheet |
| The workflow is evidenced mainly by vendor tool documentation that describes the pipeline | E3 | tool_existence | industry_supported | name_reference_support | step=name_reference(vendor doc); rest as_recorded | vendor_doc |
| No standard or tool doc covers it; you propose the workflow for expert review | E4 | expert_pending_proposal | project_proposal | judgment_support or unspecified_support | step=expert_judgment or not_specified_by_code | other |

Notes:

- `industry_standard_complete` does not mean "the whole workflow is verified".
  It means an official standard is the primary evidence that the workflow is a
  real professional task. Level and scope still tell the honest story.
- Academic papers support method choices, not professional acceptance. Cite them
  as `source_category=academic_paper` with E3 and `recorded_partial_support`, or
  use them as a secondary reference and keep the standard as primary.
- One row has one `primary_source_url`. Put secondary sources in
  `source_reference`.

## 5. Column content bar

Each column must carry real content. Empty filler ("N/A", "none", "待定") fails
the required-field gate and, more importantly, fails review.

- `subdomain_business_boundary`: what the subdomain covers as professional work,
  its boundary against the neighbouring subdomains and against adjacent domains,
  and who signs off on the deliverable. 2-4 sentences.
- `subdomain_occupations`: 4-8 real job titles, Chinese with English in
  parentheses, e.g. 动画导演 (animation director).
- `workflow_title`: English, specific, 6-14 words. Name the artifact and the
  professional context, e.g. "Animated Short Film Production Pipeline to
  Broadcast Master".
- `occupation_scope`: which roles execute which part, and the division of
  responsibility (who approves).
- `workflow_summary`: 2-4 sentences, end to end, input to delivered artifact.
- `source_type`, `evidence_level`: from the table above.
- `source_reference`: author/body + document number + clause or section + year,
  plus one secondary source. Example: `ICAO Annex 6 Part I 4.3 (2022);
  FAA AC 120-92B (2015)`. Never just a URL here.
- `expert_raw_materials`: the actual inputs a professional receives: scripts,
  storyboards, EDL/XML, CAD/BIM models, drawings, weather/NOTAM packs, MARC
  records, source manuscripts, brand briefs, audio stems, etc.
- `usage_permissions`: the rights basis for every input class (licence,
  contract, public domain, consent, NDA) and what must be cleared before use.
  Name the risky asset classes explicitly (fonts, stock footage, music, 3D
  scans, third-party models, student records).
- `task_input`: the concrete bundle for one run, with formats and sizes.
- `professional_operations`: 6-10 numbered steps. Each step is a professional
  action with its method and instrument, not a UI click path. Include the review
  or approval gates.
- `expected_deliverable`: named artifacts with formats and versions (e.g.
  `PDF/X-4 + packaged fonts + colour proof`, `IMF/ProRes master + QC report`).
- `success_criteria`: objectively checkable. Numeric tolerances, standard
  clauses, acceptance checklists, diff thresholds. No "looks good".
- `verification_approach`: how a third party would verify: re-run, measure,
  compare against the standard's checklist, inspect metadata, independent
  review.
- `platform_dependencies`: OS, applications, plugins, GPU, RAM/CPU, render time,
  licences, network/services.
- `blocking_risks`: which step is blocked on Windows-only software, GUI-only
  operation, GPU, dongle/licence server, proprietary format, or cloud service.
  Say which step and why. If nothing blocks, say so and name the residual risk.
- `expert_capability`: years/roles/certifications and the judgement a non-expert
  cannot supply.
- `cross_domain_overlap`: name the concrete existing candidate or official task
  that is adjacent, e.g. `eng_urban_wf02 (GIS suitability)`, and state the
  difference in one clause. `none identified` only after grepping.
- `granularity_check`: why this is a complete professional workflow, not a tool
  tutorial and not a single benchmark operation.
- `pending_confirmation`: what an expert must still confirm. Always non-empty.
- `data_usage_authorization`: the legal basis for the data used, per class.
- `privacy_considerations`: personal data, student records, passenger/crew data,
  health data, voice/biometric data, and the minimisation rule.
- `research_ethics`: professional responsibility and the limit of the agent's
  role. For safety-critical work state explicitly that the agent prepares
  analysis and the accountable professional signs the determination.
- `reproducibility_assessment`: can the run be repeated from the inputs? What
  blocks it (licences, non-determinism, hardware, proprietary assets)?
- `evidence_kind`, `source_category`, `primary_source_url`, `primary_claim`:
  the URL must be the canonical page you actually fetched; the claim must be
  what that page says, in one or two sentences, with the clause if available.
- `software_adaptation`: native means the pipeline runs on Linux with
  open-source or licensed Linux tools. partial_function_replacement means an
  open-source tool covers part of a proprietary step. conditional means it runs
  only under a condition (Windows GUI, container, registration). 
  unverified_or_unavailable means no verified Linux path. needs_task_redesign
  means the workflow must be reshaped to be runnable.
- `source_support_mode`, `evidence_scope`: per section 4.
- `workflow_family_id`: 2-4 `fc_` codes that place the workflow in a task family,
  e.g. `fc_media_production,fc_render_pipeline`.
- `process_incident`: `none` unless a real research incident happened. Do not
  invent one.

## 6. Domain mandates

visual_media: the workflow must be a complete production process (3D, animation,
video, audio, graphic design). Cover asset rights (stock, fonts, music, models,
scans), Windows-only or GUI-only dependencies, GPU and render time, licence
servers, and whether the final artifact is editable, reproducible, and
objectively acceptable. Do not treat "using Blender" or "using Photoshop" as a
task type.

transport_safety: keep aviation, port, public transport, and fire/safety
operations inside their professional boundary. Cover the operational plan, risk
analysis, simulation result, and safety report, and the professional
accountability for each. Name the regulation or industry standard and the
authorisation needed for real operational data. Flag Windows-only professional
software, GIS, simulators, and proprietary systems. The agent never makes the
real safety decision; it prepares the analysis for a named accountable role.

education_info: cover edtech, curriculum/instructional design, library and
information science, and translation/localisation. Cover copyright of
textbooks, bibliographic records, course materials, and language resources;
student data, learning records, and privacy; whether learning outcomes and
translation quality are objectively verifiable; and whether multilingual or
format-conversion work is a real professional workflow.

## 7. Seed archetypes (pick 3-5 best-supported; substitution allowed only with equal depth)

animation_3d:
1. Animated short film production to a broadcast/festival master (script and
   storyboard, animatic, asset build, layout, animation, lighting/render,
   compositing, grade, delivery QC).
2. Game-ready character asset pipeline (sculpt, retopo, UV, bake, texture, rig,
   LOD, engine import validation).
3. Architectural or product visualisation still set (CAD/BIM ingest, scene
   assembly, materials and lighting, path-traced render, post).
4. Interactive WebGL 3D product configurator (glTF optimisation, Draco/KTX2,
   viewer integration, performance and accessibility budget).
5. Virtual production previz shot package (USD scene, tracking data, LED volume
   prelight).

graphic_design:
1. Brand identity system and guidelines (audit, logo system, type and colour,
   applications, guidelines PDF).
2. Print packaging artwork to PDF/X with dieline, spot colours, barcode
   verification (GS1).
3. Book or magazine editorial layout and prepress to PDF/X-4 plus accessible
   EPUB 3.
4. Accessible brand and document system remediation (WCAG 2.2, PDF/UA).
5. Exhibition or wayfinding signage system (ISO 3864, ISO 21542, ADA).

audio_music:
1. Music mix and master to a streaming/broadcast loudness spec (ITU-R BS.1770,
   EBU R128).
2. Film/TV post: dialogue edit, sound design, 5.1 mix to a broadcast spec.
3. Audiobook production to ACX/Audible technical spec plus chapter QC.
4. Podcast series post-production to a published loudness and metadata spec.
5. Audio restoration and archival transfer (IASA TC-03/TC-04).

aviation:
1. Flight plan and dispatch release package (weather, NOTAM, performance, fuel,
   route, alternate, release authority).
2. SMS hazard identification and risk assessment for a new route or procedure
   (ICAO Doc 9859 risk matrix, mitigation, safety case).
3. Airport airside capacity or stand allocation study (ICAO ADRM, fast-time
   simulation).
4. UAS BVLOS operation risk assessment (JARUS SORA).
5. Occurrence investigation analysis package (ICAO Annex 13) with the
   accountable investigator signing the finding.

maritime_port:
1. Port call and vessel turnaround plan (berth window, pilotage, tugs, cargo
   sequence; IMO FAL).
2. Container stowage and lashing plan verification (IMO CSS Code).
3. Dangerous goods segregation and documentation check (IMDG Code).
4. VTS or channel capacity simulation study (IALA, PIANC).
5. Port safety risk assessment and emergency response plan (ISO 31000, PIANC).

fire_safety:
1. Building fire protection and life safety design review (NFPA 101 egress,
   NFPA 13 sprinklers).
2. Performance-based fire engineering with evacuation simulation (NFPA 101
   Chapter 5, FDS/PyroSim).
3. Fire investigation origin and cause report (NFPA 921).
4. Pre-incident plan for a high-hazard occupancy (NFPA 1620).
5. Industrial flammable liquids fire risk assessment (NFPA 30).

educational_technology:
1. Blended course instructional design package (needs analysis, objectives,
   assessment blueprint, activities, LMS build, QA rubric).
2. SCORM/xAPI courseware packaging and conformance test.
3. Digital course accessibility remediation (WCAG 2.2 AA, Section 508).
4. Learning analytics dashboard specification with FERPA/GDPR data governance.
5. Virtual lab or simulation design for a STEM course.

library_info:
1. Original cataloging to RDA and MARC 21 with authority control (LC-PCC).
2. Digitisation and metadata package for a special collection (FADGI, Dublin
   Core, METS/MODS, IIIF).
3. Collection deselection and weeding analysis (CREW/MUSTIE).
4. Systematic review search strategy and PRISMA 2020 reporting.
5. Digital preservation ingest to OAIS (ISO 14721) with PREMIS.

translation:
1. Technical translation with terminology management to ISO 17100 (TEP
   workflow, TBX).
2. Software UI localisation via XLIFF 2.x with linguistic QA (MQM).
3. Subtitling and audiovisual translation to a published spec (Netflix TTSG or
   EBU-TT).
4. Machine translation post-editing per ISO 18587 with quality estimation.
5. Certified/legal translation workflow (sworn translator, ISO 17100).

Official benchmark tasks already in these subdomains (do not duplicate; they are
single reconstruction/reproduction operations, not full workflows):
`visual_media/atlas_outpost_graybox_navigation`,
`visual_media/blender_character_reconstruction_from_multiview_01`,
`visual_media/butterfly_flap_animation`, `visual_media/chroma_key_from_reference`,
`visual_media/compress_3dgs_scene_ply`, `visual_media/high_to_low_modeling`,
`visual_media/human_mesh_animation_reproduction`,
`visual_media/mota_flash_game_reproduction` (as mota_reproduction),
`visual_media/music_transcription`, `visual_media/object_generation`,
`visual_media/project_migration` (Ardour), `visual_media/scene_restoration`,
`visual_media/skeletal_animation_reproduction`, `visual_media/uv_reproduction`,
`visual_media/video_storyboard_001`,
`engineering/robotics_blender_tabletop_reconstruction`,
`other/mota_exploration`, `business_finance/saas_onepager_brand_refresh_instance_1`,
`education_info/marc_remediation_folio_overlay`,
`education_info/yi_manuscript_translation_1`,
`transport_safety/fds_single_compartment_detector_reconstruction`.

## 8. Source verification protocol

1. Use the web search tool to locate a canonical source. Prefer standards bodies,
   regulators, professional associations, peer-reviewed journals, government
   agencies, and official tool documentation for tool facts.
2. Fetch the exact page before citing it. Record the final URL, HTTP status, page
   title, and the sentence that supports the claim in
   `.audit/s1-02b3-sources-<stem>.md`. One line per source.
3. If a fetch fails or the page does not support the claim, replace the source.
   Never cite an unverified URL. Never cite a search result page.
4. Paywalled standards: cite the official landing/abstract page and use
   `name_reference`, or find a free official equivalent (regulator AC, guidance
   note). Do not claim clause-level support you did not read.
5. Do not use content farms, SEO listicles, or AI-generated summaries as primary
   evidence.
6. If the web tool is unavailable, stop and report `WEB_UNAVAILABLE` without
   writing files.

## 9. Build and self-check loop

Write the CSV with a Python builder that holds the rows as dicts and calls
`csv.DictWriter`. Then run the per-stem gate (the frozen script has no stem
argument, so call its function directly):

```
python3 - <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("frag", "scripts/30_check_fragment_b3.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
stem = "vm_cluster"  # your stem
text = open(f"evidence/s1_02b3_research/{stem}_candidates.csv", encoding="utf-8").read()
sys.exit(1 if m.check_fragment_text(text, stem, m.FRAG_DIR) else 0)
PY
```

Exit 0 is required. If it fails, fix the content. Never weaken the contract and
never edit the script.

JSON sidecar `<stem>.json`:

```
{"subdomains": [
  {"subdomain_code": "animation_3d", "candidate_count": 3,
   "coverage_notes": "why this many rows; what evidence is thin"},
  {"subdomain_code": "graphic_design", "candidate_count": 3, "coverage_notes": "..."},
  {"subdomain_code": "audio_music", "candidate_count": 3, "coverage_notes": "..."}
]}
```

The code set must equal your cluster's three subdomains. `candidate_count` must
equal the CSV row count. `coverage_notes` must be non-empty for every subdomain.

## 10. Report back

Return a compact report: rows per subdomain, level/kind/mode/adaptation
distribution, the source list with fetch status, seed substitutions and why, and
every unresolved uncertainty. Do not claim a source works unless you fetched it.