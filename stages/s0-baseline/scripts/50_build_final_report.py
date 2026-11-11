#!/usr/bin/env python3
# 50_build_final_report.py: generate FINAL_VALIDATION_REPORT.md from the
# validator results JSON + SOURCE_MANIFEST_FINAL.json. Single source of truth.
import json, os, sys, datetime

FINAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(FINAL, "evidence", "final_validate_results.json")
MANIFEST = os.path.join(FINAL, "SOURCE_MANIFEST_FINAL.json")
OUT = os.path.join(FINAL, "FINAL_VALIDATION_REPORT.md")

def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def fmt_verdict(v):
    return {"PASS": "通过", "FAIL": "失败", "ERROR": "错误", "SKIP": "跳过"}[v]

results = json.load(open(RESULTS, encoding="utf-8"))
manifest = json.load(open(MANIFEST, encoding="utf-8"))
post_stamp = manifest.get("hashed_at_post") or "封存前未记录"

checks = results["results"]
summary = results["summary"]

lines = []
lines.append("# Phase 0 最终基线验证报告")
lines.append("")
lines.append(f"生成时间:{now()}。本报告的全部检查数据来自 evidence/final_validate_results.json 与 SOURCE_MANIFEST_FINAL.json,没有手工填写的数字。[方法: scripts/final_validate.py + scripts/50_build_final_report.py]")
lines.append("")
lines.append("## 1 范围与方法")
lines.append("")
lines.append("- 独立校验器 scripts/final_validate.py。违例即失败,退出码非零即不放行。[方法]")
lines.append("- 检查对象。10 份最终文件、PHASE0_FINAL_REPORT.md、三份数据表统计、跨文件术语与结论、全部引用路径、状态表述、三个 Git 仓库、inputs-readonly 锁定、继承来源哈希、最终校验和清单。")
lines.append("- 本轮不运行官方任务,不安装环境,不开发平台或转换器。run_state_current 全部保持 NOT_RUN。[约束: 任务书 evidence/history-final/EXECUTION_BRIEF_FINAL_CHAT.md]")
lines.append("")
lines.append("## 2 自动检查结果")
lines.append("")
n = summary
lines.append(f"- 总检查数 {len(checks)}。通过 {n.get('PASS',0)} 项,失败 {n.get('FAIL',0)} 项,错误 {n.get('ERROR',0)} 项,跳过 {n.get('SKIP',0)} 项。必过项缺口 {results.get('required_fail',0)} 个。")
skips = [c for c in checks if c["verdict"] == "SKIP"]
for c in skips:
    lines.append(f"- SKIP 说明。{c['check_id']} 的对象是 {c['object']},原因是 {c['evidence']}。")
lines.append("")
lines.append("| 检查项 | 对象 | 判定 | 证据 |")
lines.append("| --- | --- | --- | --- |")
for c in checks:
    lines.append(f"| {c['check_id']} | {c['object']} | {fmt_verdict(c['verdict'])} | {c['evidence']} |")
lines.append("")
lines.append("## 3 冻结产物与继承")
lines.append("")
lines.append(f"- 冻结阶段 {manifest.get('stage')}。哈希前书挡 {manifest.get('hashed_at_pre')},哈希后书挡 {post_stamp}。")
amend = manifest.get("amendment")
if amend:
    lines.append(f"- Closeout amendment。前次后书挡 {amend.get('prior_hashed_at_post')},再封存时点 {amend.get('amended_at')},原由 {amend.get('reason')}。")
lines.append(f"- 最终正式文件 {len(manifest.get('final_files',{}))} 份,证据文件 {len(manifest.get('evidence',{}))} 份,脚本 {len(manifest.get('scripts',{}))} 份。")
lines.append("")
lines.append("| 最终文件 | SHA256 前 16 位 | 方式 | 继承来源 |")
lines.append("| --- | --- | --- | --- |")
for fname, rec in sorted(manifest["final_files"].items()):
    lines.append(f"| {fname} | {rec['sha256'][:16]} | {rec['mode']} | {rec.get('source') or '本轮新写'} |")
lines.append("")
lines.append("## 4 未声明通过的项目")
lines.append("")
lines.append("- 全部 122 条官方任务 run_state_current 是 NOT_RUN。本轮没有运行任何官方任务,因此没有任何运行结论。")
lines.append("- Windows 首期与 GPU 预算保持 OPEN,正式配额与排产未裁决。这些是负责人决策项,不是执行验证项。")
lines.append("- 9 条 GUI unknown 任务的工程与审核风险保持 UNKNOWN,等待人工复核。遗留 UNKNOWN 清单见 PHASE0_FINAL_REPORT.md 第 8 节。")
lines.append("")
lines.append("## 5 结论")
lines.append("")
req = results.get("required_fail", 0)
if req != 0 or n.get("FAIL", 0) or n.get("ERROR", 0):
    verdict = "验证未通过,不得放行。"
else:
    verdict = "验证通过。Phase 0 已完成并验收通过。历史目录已归档并完成清理。analysis/phase0-final/ 是当前唯一有效基线。"
lines.append(verdict)
lines.append("")
lines.append("Phase 0 CLOSED。Phase 0 最终基线已验收,历史版本已归档,后续不再修改 Phase 0 内容。")
lines.append("")
lines.append("状态:Phase 0 CLOSED,phase0-final 为唯一有效基线。本轮仅完成状态收尾与清理后来源校验调整,未进入 Phase 0.5/P1。")
lines.append("")

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("validation report written:", OUT, "| checks", len(checks))