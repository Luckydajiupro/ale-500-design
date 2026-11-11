# 01_agents-last-exam: read-only audit of the old ALE engine

Snapshot: /Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/inputs-readonly/01_agents-last-exam
Upstream: https://github.com/rdi-berkeley/agents-last-exam.git
Branch: main. HEAD 2e91edd3cd26baa35a38127c90c8e5241dfbe62f.
Tags: v1, runtime-qe-bgw-6.7.0-4.0.
Audited read-only, 2026-11-08. All paths below are repo-relative to the snapshot root.
Evidence tags: [doc] official doc text, [code] source or config, [inference] my reasoning, [unknown] open question.

## 1. Identity

- Project name. "Agents' Last Exam" (ALE). README.md:2-5 shows the title. [doc]
- Purpose. "Challenge and measure AI agents on economically valuable, real-world tasks." README.md:8. [doc]
- Owner. Led by UC Berkeley RDI and RDI Foundation. README.md:17-18. [doc]
- What the repo is. Official public repository of the ALE benchmark. It holds two things. The run framework under ale_run/ and the task source plus graders under tasks/. README.md, AGENTS.md layout diagram. [doc][inference]
- Relation to the rdi-berkeley artificial-life exam. This repo IS the public artifact of the ALE program. Agents solve real GUI and CLI workflows inside Windows or Linux VMs, graded against hidden references. README.md "How ALE Works" section. [doc][inference]
- Version. pyproject.toml sets name "agent-last-exam", version 0.1.0, requires-python ">=3.12,<3.14". [code]
- Releases. v1 tag points to commit d9abc0734b56ea34116c5bfcbdd0b808269ab9e2. docs/releases/v1.md. v1.1 is the current run target. docs/releases/v1.1.md. [doc][code]
- Runtime tag. runtime-qe-bgw-6.7.0-4.0 names the preinstalled package env/packages-linux/qe-bgw-6.7.0-4.0. [code][inference]
- Paper. arXiv:2606.05405. README.md:11. Websites agents-last-exam.org and agenthle.org. [doc]
- License. Software Apache-2.0 (LICENSE), data CC-BY-4.0 (LICENSE-DATA). Badges at README.md:14-15. [code][doc]
- Dependencies. openenv-core==0.3.0, cua-bench==0.2.7, pydantic, httpx, anyio, huggingface-hub. pyproject.toml. [code]
- History. 602 commits. First real skeleton at 7cbb636 "Initial commit: ale orchestration framework (v0.1.0)". [code]

## 2. Layout

Top level. ale_run/, tasks/, configs/, selected_tasks/, docs/, env/, scripts/, secret/, tests/, releases/, assets/, README.md, LICENSE, LICENSE-DATA, AGENTS.md, pyproject.toml, uv.lock, .gitmodules, example_exp.yaml. [code]

Sizes. Total 1.5 GB, .git 1.1 GB, ale_run 326 MB, tasks 64 MB, assets 18 MB, tests 3.3 MB, env 1.9 MB. [code]

File counts. 28273 files excluding .git. tasks/ has 621 files. Repo-wide extension census. ts 15886, py 2344, rs 2228, md 2000, json 1141. The huge ts/rs counts come from vendored agent submodules. [code][inference]

Key directories.

- ale_run/. The framework. Entry point ale_run/cli.py, prog name "ale". python -m ale_run. [code]
- ale_run/agents/. 23 agent adapters. Five carry git submodules under <name>/upstream, all CUA-verse forks on branch agenthle. gemini_cli, grok_cli, openclaw_cli, hermes, codex. .gitmodules. [code]
- ale_run/base_interface/. Contracts between framework and tasks. task_data.py defines TaskDataSpec, trajectory.py the log schema, plus loader and driver in ale_run/tasks/. [code]
- ale_run/environments/. Provider modules under providers/ (aliyun, aws, docker, gcloud, qemu, static), VM image registry under images/, task data backends under task_data/ (gsbucket, s3bucket, ossbucket, baked_in_sandbox, local_host, huggingface). [code]
- ale_run/executors/. In-guest and docker runners, entry scripts, secrets sidecar. [code]
- tasks/. All task code, one folder per domain, one folder per task. This is where task data lives in git. [code]
- configs/. Reusable experiment parts. agents/ has 23 agent presets, environments/ has provider yamls. [code]
- selected_tasks/. Curated task lists as txt files. [code]
- docs/. HTML manual under docs/ale-docs-site/pages/ plus release notes under docs/releases/. [code]
- env/. Host and guest dependency manifests. install scripts, verify scripts, packages-linux/, packages-win/. [code]
- releases/v1.1/assets.json. Pinned manifest of v1.1 lists, HF repos, images and data with SHA256 hashes. [code]

Where task data really lives. Task code and graders are in git. Runtime inputs and hidden references ship outside git, either baked into VM images or pulled from gs:// or Hugging Face archives. The fetch tool is scripts/fetch_task_data.sh. [code][inference]

## 3. Old task format

One task instance is a folder tasks/<domain>/<task>/ with two required files. [doc]

- main.py. Python module with three entry hooks. load, start, evaluate. [code]
- task_card.json. Metadata card. [code]

The authoring guide states it plainly. "A task is a two-file package" and "input/reference/output surface in ~250 lines". docs/ale-docs-site/pages/add-task.html. [doc]

No readme.md. There are zero readme.md files inside task folders, zero compose.yaml, zero _meta dirs. find confirmed. The main.py docstring is the closest thing to a task readme. [code]

Quoted example header, tasks/demo/hello/main.py. [code]

```text
"""Demo task: ``demo/hello`` (Linux) — a GUI-centric end-to-end demo.

This is the canonical "does the whole stack work" task. Unlike a trivial
file-write, it forces the agent to drive a real desktop GUI:
```

The em dash here is verbatim repo content inside a fenced quote. [code]

Files scored per task, required and optional. [code][doc]

- main.py required. [code]
- task_card.json required. [code]
- scripts/ common. Holds grader scripts, usually verify_*.py copied into the VM at eval time. [code]
- report_judge.py optional. LLM report grading, e.g. tasks/business_finance/digital_marketing_ab_test_analysis_1/report_judge.py. [code]
- task_spec.md optional. Short spec, e.g. tasks/visual_media/butterfly_flap_animation/task_spec.md. [code]
- assets/ optional. Embedded non-code files. [code]

main.py anatomy. [code]

- Imports cua_bench as cb with a local fallback stub when cua_bench is missing. [code]
- Dataclass Config(LinuxTaskConfig) for Linux tasks, Config(GeneralTaskConfig) for Windows tasks. Constants DOMAIN_NAME, TASK_NAME, VARIANT_NAME. [code]
- @cb.tasks_config(split="train") wraps load(). It returns a list of cb.Task objects. Each Task carries description, metadata and a computer dict. computer.setup_config.os_type is "linux" or "windows". [code]
- @cb.setup_task wraps start(task_cfg, session). It stages the workspace and never touches hidden references. [doc][code]
- @cb.evaluate_task wraps evaluate(task_cfg, session). It returns list[float], usually one score in 0..1. Missing output returns 0.0 and never raises. [doc][code]

Config classes. GeneralTaskConfig lives in tasks/common_config.py. REMOTE_ROOT_DIR defaults to E:\agenthle. OS_TYPE defaults to "windows". LinuxTaskConfig lives in tasks/linux_runtime.py. REMOTE_ROOT_DIR defaults to /media/user/data/agenthle. OS_TYPE is "linux". VARIANT_NAME is "base". [code]

VM directory contract. input/ visible to the agent. software/ visible. output/ writable. reference/ hidden and staged only after the agent finishes, decrypted from reference.7z at eval time. tasks/demo/hello/main.py docstring. [code][doc]

Credentials injection. tasks/common_setup.py BaseTaskSetup copies requiredCredentials from <repo>/secret/agent_time into input/credentials/ on the VM. Env override AGENTHLE_CREDENTIALS_DIR. [code]

task_card.json anatomy, example tasks/demo/hello/task_card.json. [code]

- taskId "demo/hello". Must match the folder path. [doc][code]
- title, summary, category. [code]
- vm block. snapshot, vcpus, memory_gb, disk_gb, timeout_s. [code]
- taskPrompt. Long instruction strings in many cards. They name visible files under base/input and required outputs under base/output. Example tasks/business_finance/llm_ecosystem_privacy_audit_realdata_1/task_card.json. [code]
- taxonomy. domain_id, subdomain_id, subdomain_code, subdomain_name, classifier. Example tasks/business_finance/digital_marketing_ab_test_analysis_1/task_card.json lines 23-26. [code]
- requiredSystemPackages. Lists tools that must be preinstalled, matching dirs under env/packages-linux/ or env/packages-win/. [code]
- vm.network.mode. Absent by default, meaning "on". Four cards set "off" at HEAD. [code]

A representative grader pattern. tasks/business_finance/digital_marketing_ab_test_analysis_1/main.py evaluate() writes scripts/verify_ab_test_outputs.py into /tmp/agenthle_eval/<task> on the VM, runs it with --input-dir --reference-dir --output-dir --external-report flags, and parses JSON stdout into a score plus component scores. Useful reference when converting graders. [code]

## 4. Domains and counts

Domains are top-level folders under tasks/. Table compares task folders containing a main.py (in git) with entries in tasks/published_tasks.json (published set). [code]

| domain | in git | published |
|---|---|---|
| demo | 8 | 0 |
| computing_math | 19 | 19 |
| business_finance | 19 | 19 |
| health_medicine | 19 | 19 |
| engineering | 17 | 16 |
| visual_media | 15 | 11 |
| physical_sciences | 14 | 14 |
| life_sciences | 12 | 12 |
| psychology_neuro | 3 | 3 |
| other | 2 | 2 |
| transport_safety | 2 | 2 |
| legal | 2 | 2 |
| education_info | 2 | 2 |
| social_sciences | 1 | 1 |
| agriculture_env | 0 | 0 |
| utils | 0 | 0 |
| total | 135 | 122 |

Demo tasks are excluded from the published manifest. demo/ holds hello, hello_win, readfile_secret, seecheck, seecheck_win, tool_smoke, tool_smoke_win, apply_patch_win. [code]

Retired tasks stay in git. 30 tasks were retired between v1 and v1.1. Full list in docs/releases/v1.1-task-review.md. Examples. agriculture_env/crop_rotation_d02, engineering/mold-flow, visual_media/inkscape_cultural_poster_design. [doc]

Difficulty split. selected_tasks/full/near-term.txt has 45 entries, full-spectrum.txt 46, last-exam.txt 36. Total 122. [code]

Snapshot split. From the vm census of all 135 cards. cpu-free-ubuntu about 90, cpu-free 37, gpu-free 3, gpu-license 5. selected_tasks/cpu.txt lists 119, gpu.txt lists 3. [code]

Taxonomy. 13 industry clusters and 55 subdomains per README.md. Every card carries an O*NET derived taxonomy block with classifier provenance fields. [doc][code]

## 5. CLI

Entry point. python -m ale_run, prog name "ale". ale_run/cli.py. [code]

There is no ale/cmd.py. That path never existed in any commit. git log --all -- ale/cmd.py is empty. The only cmd*.py hits are files inside vendored submodules. [code]

Subcommands at HEAD. Exactly two. [code]

- run SPEC_PATH. Flags --dry-run, --agent, --task, --disable-resume, --verbose. Drives one experiment yaml. auto_resume skips finished units whose task revision matches. [code]
- list. Prints tasks. --verbose adds path, snapshot and title. [code]

Subcommands absent. build, compose, push, fetch, convert, prefetch, register, resolve, build-community, pack, meta, sources do not exist here. They belong to a private AgentHLE CLI, not this public repo. [inference]

History check. Commit 7cbb636 (v0.1.0) had an ale/ package whose ale/cli.py offered only run and list. That package was deleted in the public rewrite. [code]

Flags controlling OS and provider. None on the CLI. Both come from data. OS type comes from the task config class. Provider and snapshot come from the experiment yaml environment block. [code][inference]

Adjacent tooling. scripts/fetch_task_data.sh downloads the gated data archive with pinned --revision and --sha256. env/verify_host_env.sh checks host deps and all 122 task entry imports. [code]

## 6. Providers and OS

Guest OS values. Two, "linux" and "windows". No mac VM. [code]

- Windows is the default. GeneralTaskConfig.OS_TYPE is "windows" in tasks/common_config.py. Remote root E:\agenthle. [code]
- Linux opt-in. LinuxTaskConfig.OS_TYPE is "linux" in tasks/linux_runtime.py. Remote root /media/user/data/agenthle. [code]
- mac appears only agent-side. The ale_claw prompt helper maps mac or darwin to macOS for key naming. ale_run/agents/ale_claw/harness/prompt.py lines 52-62. [code]

Host OS. Ubuntu 22.04/24.04/26.04 or Debian 12/13. env/README.md. docs/ale-docs-site/pages/local.html line 209 states "macOS and Windows hosts are not supported." [doc]

Providers. Six modules under ale_run/environments/providers/: aliyun, aws, docker, gcloud, qemu, static. [code]

- gcloud is the main cloud path. VMs run from snapshot images ale-ubuntu22-v1-1 and ale-win10-v1-1. configs/environments/environment_gcloud.yaml. [code]
- aws runs EC2 with S3 task data. aliyun runs ECS with OSS. qemu runs local KVM from about 173 GB qcow2 images published on Hugging Face. docker runs a local Linux subset. static assumes an existing sandbox. [code]
- README provider table lists gcloud, AWS, Alibaba, QEMU/KVM, local Docker, static. README.md. [doc]

Snapshots. cpu-free-ubuntu Linux GUI. cpu-free Windows GUI at resolution 1024x768. gpu-free Windows GPU at 1920x1080. gpu-license keeps original licensed workflows. configs/environments/environment_gcloud.yaml. [code]

OS-specific behavior.

- GUI driving. A unified CUA MCP bridge gives screenshots, clicks and typing on both OSes. README.md how-it-works. [doc]
- Windows resolution limits. GCE verified mode lists constrain resolutions, non-GPU up to 1920x1440. configs/environments/environment_gcloud.yaml comments. [code]
- Windows line endings. Task authors must use \r\n in Windows task prompts. docs/ale-docs-site/pages/add-task.html. [doc]
- Windows desktop wallpaper is set programmatically for GNOME and XFCE on Linux side. tasks/linux_runtime.py set_desktop_wallpaper(). [code]

Preinstalls. Two package libraries exist. env/packages-linux holds about 40 tool dirs, e.g. qe-bgw-6.7.0-4.0, terraform-1.7.0, wireshark-4.4.14, r-base-4.3.2, minikube-1.32.0. env/packages-win holds e.g. autodesk-civil-3d-2024, blender-5.0.1, davinci-resolve-21.0, rhino-8, microdicom-2025.3, kicad-10.0.0. Task cards declare needs via requiredSystemPackages. [code]

How API keys reach the agent. [code][doc]

- Inventory. secret/.env.example lists ANTHROPIC_API_KEY, OPENROUTER_API_KEY, OPENAI_API_KEY, XAI_API_KEY, MOONSHOT_API_KEY, META_API_KEY, GLM_API_KEY, HF_TOKEN, HF_INFERENCE_TOKEN, OCTAVUS_AGENT_API_KEY, BRAVE_API_KEY, plus GCP credentials and ALE_REFERENCE_ARCHIVE_PASSWORD. [code]
- The archive password is public and project-wide. It is intentionally never forwarded into the agent sandbox. secret/.env.example comments. [code]
- Flow. The experiment yaml names secret_file. The config loader resolves ${env:VAR} strings. Agent yamls carry provider, base_url and api_key fields. example_exp.yaml, configs/agents/claude_code.yaml. [code]
- In-sandbox safety. Executors write a sibling _secrets.json next to _spec.json. The in-guest entry reads it once, injects it into the process env, then deletes it. Log gathering excludes that filename. ale_run/executors/_secrets.py lines 1-11. [code]
- Graders use separate keys. secret/eval_time/openai.env.example sets JUDGE_BASE_URL, JUDGE_API_KEY, JUDGE_MODEL=gpt-5.4, AUDIO_JUDGE_MODEL=gpt-audio-1.5. Judged tasks use a shared host-side judge. tasks/utils/evaluation.py. [code]

## 7. Conversion

No convert command exists in this repo. Git history sweep confirms it was never here. [code]

What conversion means, three layers. [inference]

- Format. Tasks have always been cua-bench style main.py plus task_card.json since v0.1.0. docs/ale-docs-site/pages/tasks.html states ALE adopts the cua-bench task spec. [doc]
- Release conversion v1 to v1.1. 122 active tasks after 30 retirements, 57 modified plus 65 retained. Change types. 47 instruction, 43 verification, 32 environment, 23 data. docs/releases/v1.1.md, README.md:54-66. [doc]
- Software conversion. Six licensed workflows moved to open source with the same task IDs. engineering/2d_drawings_to_3d_building_model to Blender, cailian_road_highway_alignment_2 to FreeCAD Road, gcode to FreeCAD CAM plus LinuxCNC plus CAMotics, inner_support_elevation_optimization to Kratos, visual_media/music_transcription to MuseScore, project_migration to Ardour. engineering/mold-flow was removed, no open source equivalent. docs/releases/v1.1.md. [doc]

v1 pin. The v1 tag preserves the original licensed run. Never mix v1 and v1.1 images, data or logs. docs/releases/v1.md. [doc]

Asset pinning. releases/v1.1/assets.json pins every list, HF repo, image and data archive with SHA256. scripts/fetch_task_data.sh refuses to run without --revision and --sha256. [code]

A v2 format experiment exists. Branch remotes/origin/feat/tasks-v2 is unmerged. For demo/hello it adds instruction.md, setup/run.sh, verify/run.sh, oracle/run.sh and task.yaml beside the old pair. Its commits read "rebuild demo/hello against the published data", "declare data inline, create what you need", "artifacts are paths". [code]

Relation to the new engine. The sibling snapshot 02_ale holds the new engine, packages/ale-core with taskspec.py, task.py and harness.py. The old format here is the conversion source into that template engine. [inference]

v1.1 is frozen. "Task designs and source are frozen" for v1.1. docs/releases/v1.1.md. [doc]

## 8. Assets

Asset census inside tasks/. 621 files. py 404, json 154, md 27, txt 8, FCMacro 7, sh 3, lua 3, csv 3, patch 2, plus one each of toml, tex, ps1, obj, m, gz, cpp, cc, FCStd. [code]

Types found. [code]

- CAD. engineering/cailian_road_highway_alignment_2 holds four FCMacro scripts, one FCStd model, one obj mesh and five csv survey files. engineering/gcode holds FCMacro macros, patch files, sh scripts and native_stock_driver.cpp. [code]
- TeX. tasks/computing_math/clustered_cyclic_code_circuit_level_simulation/assets/ has a .tex file. [code]
- MATLAB. tasks/health_medicine/prostate_imrt_matrad_reproduction/scripts/replay.m. [code]
- DAW project. tasks/visual_media/project_migration/assets/celeste_symphonic_suite.tar.gz is 56 MB, plus lua and cc helpers. [code]
- PowerShell. tasks/visual_media/scene_restoration/scripts/render_candidate_views.ps1. [code]
- Shell. e.g. tasks/computing_math/cp_test_gen_1/scripts/run_judge_wrapper.sh. [code]

Images and audio mostly live outside git. Input images ship in VM images or data archives. Example. The butterfly task references input/butterfly.jpeg in tasks/visual_media/butterfly_flap_animation/task_spec.md. [code][inference]

Multilingual content exists. tasks/education_info/yi_manuscript_translation_1 is a manuscript translation task whose prompt forbids internet, noted in branch commit a23031c. [code][inference]

Internet and external services. Tiny surface by design. [code][doc]

- Nine distinct URLs appear across all task prompts. Three are public sites. https://lifescience.opensource.epam.com/ketcher, https://ruffle.rs/demo and the cheminfo.org SMILES validator. [code]
- Every other URL is a staged local app. localhost:8069 Odoo, localhost:8080 Flowable, localhost:8080 tax forms, localhost:3000. [code]
- Egress control. vm.network.mode accepts "off" or "on". 4 of 135 cards set "off" at HEAD. [code]
- Unmerged branch feat/controlled-network-off marks 16 tasks mode off. Ten already forbid internet in their prompts. Six are cases where agents pulled public answers. It also adds QEMU network sealing with experiment keys network_off_policy and network_allowlist. Commits a23031c and f25ed68. [code]
- One task stays online on purpose. egt710_table1_smiles_extraction needs the online ChemInfo SMILES validator. [code]
- Host side. Quickstart instructs restricting guest networking to the CUA port TCP 5000 from the ALE host. docs/quickstart.md. [doc]

## 9. Open questions

1. [unknown] Which private repo owns the full CLI. build, compose, push, fetch, convert, prefetch, register, resolve, build-community, pack, meta, sources appear nowhere in this public history. Where do those commands live today?
2. [unknown] Why only four cards carry vm.network.mode "off" at main while the 16-card branch was never merged. Which enforcement is real for published v1.1 runs?
3. [unknown] What exactly the new engine expects from a converted task. The mapping between ale-core taskspec.py in snapshot 02_ale and this main.py plus task_card pair needs the sibling audit.
4. [unknown] Where each task's runtime data lives. bake versus gs:// versus HF archive is configured per task data source. No in-repo manifest maps task to data location, only releases/v1.1/assets.json hashes.
5. [unknown] The fate of demo tasks in the new template. demo/ has 8 tasks and zero published entries. Conversion targets or training material?
6. [unknown] The meaning of tag runtime-qe-bgw-6.7.0-4.0. It matches env/packages-linux/qe-bgw-6.7.0-4.0. Presumably a release for the silicon and mose2 QE-BGW tasks. Unconfirmed.
7. [unknown] Whether hidden references are one global archive or per-task archives. reference.7z appears at eval time and the archive password exists. Grouping per task is not verified.
8. [unknown] How much trust to put in the per-card taxonomy classifier. Cards record a model and source for each classification, e.g. gpt-4o-mini. Whether that provenance is audited downstream is unknown.

END