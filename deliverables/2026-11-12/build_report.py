from pathlib import Path
from datetime import date
from html import escape
import re

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "07-expert-supply.md"
OUT = Path(__file__).parent / "ale-500-boss-brief.html"
text = DOC.read_text()
lines = text.splitlines()

def table_after(title, ncols):
    i = lines.index(title)
    rows = []
    started = False
    for line in lines[i + 1:]:
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            if cells[0].startswith("一级") or cells[0] == "类目":
                started = True
                continue
            if started:
                rows.append(cells)
        elif rows:
            break
    return rows

def num(s):
    return int(s.replace(",", "").replace("*", "").strip())

domains = []
for r in table_after("## 一级类目配额", 5):
    if r[0] == "合计":
        continue
    domains.append({
        "name": r[0], "official": num(r[1]), "subs": r[2],
        "quota": num(r[3]), "share": r[4]
    })

subs = []
for r in table_after("## 二级类目配额", 7):
    if len(r) < 7 or r[0] == "合计":
        continue
    subs.append({
        "domain": r[0], "name": r[1], "official": num(r[2]),
        "candidates": num(r[3]), "quota": num(r[4]),
        "batch": r[5], "first": r[6]
    })

fees = []
for r in table_after("## 费用方案", 6):
    if len(r) < 6 or r[0].startswith("**合计**"):
        continue
    fees.append({
        "name": r[0], "pilot": num(r[1]), "first": num(r[2]),
        "formal": num(r[3]), "price": r[4], "subtotal": num(r[5])
    })

assert sum(d["quota"] for d in domains) == 500
assert sum(d["official"] for d in domains) == 122
assert sum(s["quota"] for s in subs) == 500
assert len(subs) == 56
assert sum(f["subtotal"] for f in fees) == 875000
assert sum(f["pilot"] for f in fees) == 3
assert sum(f["first"] for f in fees) == 30
assert sum(f["formal"] for f in fees) == 470

legal_quota = next(d["quota"] for d in domains if d["name"] == "法律")
expert_quota = 500 - legal_quota
first_legal = 8
first_expert = 30 - first_legal
formal_legal = 34
formal_expert = 470 - formal_legal
wave1_legal = 42
wave1_expert = 120 - wave1_legal
wave1_rest_legal = wave1_legal - first_legal
wave1_rest_expert = 90 - wave1_rest_legal
ai_low, ai_high = 46100, 92200
all_low, all_high = 921100, 967200
cap = 1050000
task_fee_500 = 875000 - 10000

# timeline
t0, t1 = date(2026, 11, 1), date(2027, 5, 1)
total_days = (t1 - t0).days
def pct(d):
    return (d - t0).days / total_days * 100
def bar(start, end):
    left = pct(start)
    width = pct(end) - left
    return f"left:{left:.2f}%;width:{width:.2f}%"

rows = [
    ("试点 3 条", date(2026, 11, 18), date(2026, 11, 28), "pilot"),
    ("首批 30 条", date(2026, 12, 1), date(2027, 1, 1), "first"),
    ("W1 余 90 条", date(2026, 12, 1), date(2027, 1, 16), "wave1"),
    ("W2 128 条", date(2027, 1, 1), date(2027, 2, 16), "wave2"),
    ("W3 126 条", date(2027, 2, 1), date(2027, 3, 16), "wave3"),
    ("W4 126 条", date(2027, 3, 1), date(2027, 4, 16), "wave4"),
    ("评测与交付", date(2027, 4, 16), date(2027, 5, 1), "deliver"),
]
gantt = "\n".join(
    f'<div class="gantt-row"><div class="gantt-label">{escape(label)}</div>'
    f'<div class="gantt-track"><div class="gantt-bar {cls}" style="{bar(s,e)}">'
    f'<span>{escape(label)}</span></div></div></div>'
    for label, s, e, cls in rows
)

months = [("11 月", date(2026, 11, 1)), ("12 月", date(2026, 12, 1)),
          ("1 月", date(2027, 1, 1)), ("2 月", date(2027, 2, 1)),
          ("3 月", date(2027, 3, 1)), ("4 月", date(2027, 4, 1))]
month_ticks = "\n".join(
    f'<div class="month-tick" style="left:{pct(d):.2f}%">{escape(m)}</div>'
    for m, d in months
)

# domain table
max_quota = max(d["quota"] for d in domains)
domain_rows = []
for d in domains:
    width = d["quota"] / max_quota * 100
    domain_rows.append(
        f'<tr><td class="name">{escape(d["name"])}</td>'
        f'<td class="num">{d["official"]}</td>'
        f'<td class="num muted">{escape(d["subs"])}</td>'
        f'<td class="num strong">{d["quota"]}</td>'
        f'<td><div class="bar"><span style="width:{width:.1f}%"></span></div></td>'
        f'<td class="num">{escape(d["share"])}</td></tr>'
    )

# sub table grouped
sub_rows = []
current = None
for s in subs:
    if s["domain"] != current:
        current = s["domain"]
        group_quota = sum(x["quota"] for x in subs if x["domain"] == current)
        sub_rows.append(
            f'<tr class="group-row"><td colspan="7">{escape(current)}'
            f'<span>{group_quota} 条</span></td></tr>'
        )
    first = '<span class="chip chip-orange">首批</span>' if s["first"] else ""
    batch = f'<span class="chip">{escape(s["batch"])}</span>' if s["batch"] else '<span class="muted">不计</span>'
    sub_rows.append(
        f'<tr><td class="muted">{escape(s["domain"])}</td>'
        f'<td class="name">{escape(s["name"])}</td>'
        f'<td class="num">{s["official"]}</td>'
        f'<td class="num">{s["candidates"]}</td>'
        f'<td class="num strong">{s["quota"]}</td>'
        f'<td>{batch}</td><td>{first}</td></tr>'
    )

# fee table
fee_rows = []
for f in fees:
    is_building = "建筑执业签字" in f["name"]
    name = f["name"]
    if is_building:
        name = "建筑执业签字"
    fee_rows.append(
        f'<tr class="{"building" if is_building else ""}">'
        f'<td class="name">{escape(name)}</td>'
        f'<td class="num">{f["pilot"] or ""}</td>'
        f'<td class="num">{f["first"] or ""}</td>'
        f'<td class="num">{f["formal"] or ""}</td>'
        f'<td class="price">{escape(f["price"])}</td>'
        f'<td class="num strong">{f["subtotal"]:,}</td></tr>'
    )

# funnel
funnel = [("触达", 1946), ("回复", 584), ("电话", 292), ("合格", 174), ("offer", 122), ("签约", 104)]
max_f = funnel[0][1]
funnel_bars = "\n".join(
    f'<div class="funnel-row"><span class="funnel-label">{label}</span>'
    f'<div class="funnel-track"><div class="funnel-bar" style="width:{20+80*(v/max_f):.1f}%"></div></div>'
    f'<span class="funnel-value">{v:,}</span></div>'
    for label, v in funnel
)

# AI scenarios
scenarios = [
    ("无 AI", 16.6, 8350, 1336000, 100, "gray"),
    ("部分 AI", 12.5, 6262, 1002000, 75, "orange"),
    ("完整 AI + 平台", 10.5, 5270, 843000, 63, "green"),
]
scenario_bars = "\n".join(
    f'<div class="scenario-row"><div class="scenario-head"><strong>{name}</strong>'
    f'<span>{hours:,} 小时 · {cost:,} 元</span></div>'
    f'<div class="scenario-track"><div class="scenario-bar {cls}" style="width:{width}%"></div></div>'
    f'<div class="scenario-note">{h} 小时 / 条</div></div>'
    for name, h, hours, cost, width, cls in scenarios
)

CSS = r"""
:root{
  --ink:#18231f; --muted:#6d7974; --line:#dfe4dc; --paper:#f3f0e7;
  --card:#fffdf8; --green:#1e5646; --green2:#2f7d66; --green3:#dcebe4;
  --orange:#d97845; --orange2:#f6e2d4; --gold:#b68a2e; --red:#a9473e;
  --shadow:0 10px 30px rgba(28,42,36,.08);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif;
  font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
.page{max-width:1180px;margin:0 auto;padding:26px 22px 54px}
.hero{position:relative;overflow:hidden;border-radius:28px;padding:42px 42px 30px;
  background:linear-gradient(135deg,#173f35 0%,#1f5a49 55%,#2b6b57 100%);color:#f8f4e9;box-shadow:var(--shadow)}
.hero:after{content:"";position:absolute;right:-90px;top:-120px;width:420px;height:420px;border-radius:50%;
  border:1px solid rgba(255,255,255,.16);box-shadow:0 0 0 45px rgba(255,255,255,.03),0 0 0 90px rgba(255,255,255,.02)}
.hero:before{content:"";position:absolute;right:180px;bottom:-160px;width:300px;height:300px;border-radius:50%;
  background:radial-gradient(circle,rgba(217,120,69,.35),transparent 65%)}
.eyebrow{display:flex;justify-content:space-between;gap:20px;align-items:center;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#cfe3d8}
.eyebrow .tag{border:1px solid rgba(255,255,255,.25);padding:5px 10px;border-radius:999px;letter-spacing:.08em}
.hero h1{margin:18px 0 6px;font-size:clamp(44px,6.2vw,84px);line-height:.95;letter-spacing:-.055em;font-weight:760}
.hero h1 span{color:#f0a06e}
.hero .sub{max-width:760px;font-size:clamp(17px,2.1vw,23px);line-height:1.35;color:#e9f2eb;margin:14px 0 0}
.hero .meta{display:flex;flex-wrap:wrap;gap:10px 22px;margin-top:26px;color:#cfe3d8;font-size:12.5px}
.hero .meta b{color:#fff;font-weight:600}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:22px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px 18px 16px;box-shadow:0 4px 16px rgba(28,42,36,.04)}
.kpi .k{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:650}
.kpi .v{font-size:31px;line-height:1.1;letter-spacing:-.04em;font-weight:760;margin:9px 0 3px}
.kpi .d{font-size:12.5px;color:var(--muted)}
.kpi.green .v{color:var(--green)}
.kpi.orange .v{color:var(--orange)}
.kpi.red .v{color:var(--red)}
.notice{margin-top:14px;background:#fff7e8;border:1px solid #f0d8a8;border-radius:16px;padding:12px 16px;font-size:13px;color:#6b4a1f;display:flex;gap:10px;align-items:flex-start}
.notice b{color:#4d3412}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--orange);margin-top:7px;flex:none}
.toc{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0}
.toc a{font-size:12.5px;color:var(--green);text-decoration:none;border:1px solid #cfdcd4;background:#fbfaf5;padding:6px 11px;border-radius:999px}
.section{background:var(--card);border:1px solid var(--line);border-radius:24px;padding:28px 30px;margin-top:20px;box-shadow:var(--shadow)}
.sec-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-end;margin-bottom:16px}
.sec-head .num{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--orange);font-size:12px;letter-spacing:.12em}
.sec-head h2{margin:2px 0 0;font-size:28px;line-height:1.2;letter-spacing:-.035em}
.sec-head p{margin:0;color:var(--muted);font-size:13px;max-width:520px;text-align:right}
h3{font-size:17px;margin:22px 0 10px;letter-spacing:-.015em}
.lead{font-size:17px;line-height:1.55;max-width:900px}
.lead b{color:var(--green)}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.grid-2{display:grid;grid-template-columns:1.15fr .85fr;gap:18px}
.card{border:1px solid var(--line);border-radius:18px;padding:18px;background:#fcfaf4}
.card h4{margin:0 0 8px;font-size:16px}
.card p{margin:0;color:var(--muted);font-size:13px}
.card .big{font-size:30px;font-weight:760;letter-spacing:-.04em;line-height:1.1;margin:6px 0 4px}
.tagline{display:inline-flex;align-items:center;gap:6px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--green);background:var(--green3);padding:4px 8px;border-radius:999px;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:13px}
th{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;background:#f2efe6;padding:9px 8px;border-bottom:1px solid var(--line);font-weight:700}
td{padding:9px 8px;border-bottom:1px solid #ece9e0;vertical-align:top}
tr:last-child td{border-bottom:none}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.name{font-weight:600}
.strong{font-weight:760}
.muted{color:var(--muted)}
.price{white-space:nowrap;font-size:12.5px;color:#4c5953}
.bar{height:7px;background:#e9e6dc;border-radius:99px;overflow:hidden;min-width:70px}
.bar span{display:block;height:100%;background:linear-gradient(90deg,var(--green2),#79ad95);border-radius:99px}
.total-row td{background:#f2efe6;font-weight:760;border-top:1px solid #d8d4c8}
.group-row td{background:#f2f0e8;font-weight:760;color:var(--green);padding:7px 8px;font-size:12px}
.group-row td span{float:right;color:var(--muted);font-weight:500}
.chip{display:inline-block;font-size:11px;line-height:1.4;padding:1px 6px;border-radius:999px;background:#e9f0eb;color:var(--green);white-space:nowrap;font-weight:650}
.chip-orange{background:var(--orange2);color:#8a4521}
.building td{background:#fffaf1}
.note{font-size:12px;color:var(--muted);margin:8px 0 0}
.callout{border-left:4px solid var(--orange);background:#fff8ef;padding:14px 16px;border-radius:0 12px 12px 0;font-size:13.5px;color:#5f4527}
.callout b{color:#7a4623}
.gantt{margin-top:10px;border-top:1px solid var(--line);padding-top:18px}
.gantt-months{position:relative;height:20px;margin-left:130px;border-bottom:1px solid var(--line)}
.month-tick{position:absolute;top:0;transform:translateX(-50%);font-size:11px;color:var(--muted);white-space:nowrap}
.month-tick:after{content:"";position:absolute;left:50%;top:19px;height:210px;border-left:1px dashed #e3e0d7}
.gantt-row{display:grid;grid-template-columns:130px 1fr;align-items:center;min-height:34px;gap:10px}
.gantt-label{font-size:12px;color:var(--muted);text-align:right;padding-right:2px}
.gantt-track{position:relative;height:24px;background:#f2efe7;border-radius:7px;overflow:hidden}
.gantt-bar{position:absolute;top:3px;bottom:3px;border-radius:5px;display:flex;align-items:center;padding:0 8px;overflow:hidden}
.gantt-bar span{font-size:10.5px;color:#fff;white-space:nowrap;font-weight:650;opacity:.95}
.gantt-bar.pilot{background:#b68a2e}.gantt-bar.first{background:var(--orange)}
.gantt-bar.wave1{background:#2f7d66}.gantt-bar.wave2{background:#4c927a}
.gantt-bar.wave3{background:#6aa38b}.gantt-bar.wave4{background:#8bb8a3}
.gantt-bar.deliver{background:#263c34}
.split{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.donut-card{display:flex;gap:14px;align-items:center;border:1px solid var(--line);border-radius:16px;padding:14px;background:#fcfaf4}
.donut{width:86px;height:86px;border-radius:50%;flex:none;position:relative;display:grid;place-items:center}
.donut:after{content:"";position:absolute;inset:11px;background:var(--card);border-radius:50%}
.donut b{position:relative;z-index:1;font-size:20px;letter-spacing:-.03em}
.donut-card .t{font-size:12px;color:var(--muted)}
.donut-card .t strong{display:block;font-size:13px;color:var(--ink)}
.donut-card .t span{display:block;margin-top:3px}
.legend{display:flex;gap:12px;flex-wrap:wrap;font-size:11.5px;color:var(--muted);margin-top:8px}
.legend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:4px}
.legend .l1{background:var(--orange)}.legend .l2{background:var(--green2)}
.funnel-row{display:grid;grid-template-columns:52px 1fr 56px;gap:8px;align-items:center;margin:7px 0}
.funnel-label{font-size:12px;color:var(--muted)}
.funnel-track{height:22px;background:#f0ede4;border-radius:6px;overflow:hidden}
.funnel-bar{height:100%;background:linear-gradient(90deg,var(--orange),#e5a57c);border-radius:6px}
.funnel-value{font-size:12px;text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)}
.scenario-row{margin:12px 0}
.scenario-head{display:flex;justify-content:space-between;gap:10px;font-size:13px}
.scenario-head span{color:var(--muted);font-size:12px}
.scenario-track{height:11px;background:#eeeae0;border-radius:99px;overflow:hidden;margin-top:6px}
.scenario-bar{height:100%;border-radius:99px}
.scenario-bar.gray{background:#8f9892}.scenario-bar.orange{background:var(--orange)}.scenario-bar.green{background:var(--green2)}
.scenario-note{font-size:11px;color:var(--muted);margin-top:3px}
.risk-table td:first-child{font-weight:700}
.gate{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:10px}
.gate .g{border:1px solid var(--line);border-radius:14px;padding:13px;background:#fcfaf4}
.gate .g b{display:block;font-size:19px;letter-spacing:-.03em}
.gate .g span{font-size:12px;color:var(--muted)}
.confirm{border:1px solid #e6cfa5;background:linear-gradient(135deg,#fff8e9,#fffdf7);border-radius:18px;padding:20px}
.confirm h3{margin:0 0 8px;color:#6b4a1f}
.confirm ol{margin:8px 0 0 20px;padding:0}
.confirm li{margin:5px 0}
.footer{color:var(--muted);font-size:11.5px;line-height:1.7;margin:24px 4px 0}
.footer a{color:var(--green)}
.small{font-size:11.5px;color:var(--muted)}
.divider{height:1px;background:var(--line);margin:18px 0}
details{margin-top:12px;border:1px solid var(--line);border-radius:14px;background:#fcfaf4;padding:0 14px}
summary{cursor:pointer;padding:12px 2px;font-weight:650;color:var(--green)}
details[open]{padding-bottom:12px}
.subtable-wrap{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:10px}
.subtable-wrap thead th{position:sticky;top:0;z-index:1}
.print-btn{position:fixed;right:22px;bottom:22px;z-index:20;background:var(--green);color:#fff;border:none;border-radius:999px;padding:12px 18px;font-size:13px;font-weight:700;box-shadow:0 8px 22px rgba(30,86,70,.25);cursor:pointer}
@media(max-width:900px){
  .kpis{grid-template-columns:repeat(2,1fr)}
  .grid-3,.grid-2,.split,.gate{grid-template-columns:1fr}
  .hero{padding:30px 24px}
  .section{padding:22px 18px}
  .sec-head{display:block}
  .sec-head p{text-align:left;margin-top:6px}
  .gantt-row{grid-template-columns:98px 1fr}
  .gantt-months{margin-left:98px}
}
@media print{
  @page{size:A4;margin:11mm}
  body{background:#fff;font-size:11px}
  .page{max-width:none;padding:0}
  .hero{border-radius:0;padding:24px 24px 18px;box-shadow:none}
  .hero h1{font-size:54px}
  .section,.kpi,.card,.confirm{box-shadow:none;break-inside:avoid}
  .section{margin-top:10px;padding:16px 18px;border-radius:12px}
  .no-print,.print-btn,.toc{display:none!important}
  .gantt-months .month-tick:after{height:180px}
  .subtable-wrap{max-height:none;overflow:visible}
  details{break-inside:auto}
  details:not([open]) > *:not(summary){display:block!important}
  .footer{font-size:9px}
}
"""

HTML = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ALE 500 条任务生产计划 · 计划版</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">

<header class="hero">
  <div class="eyebrow">
    <span>ALE 500 · 专家生产计划</span>
    <span class="tag">计划版 v1 · 2026-11-12</span>
  </div>
  <h1>500<span> 条</span><br>专业任务</h1>
  <p class="sub">配额、费用、分批与交付节奏。</p>
  <div class="meta">
    <span>交付目标 <b>2027-04-30</b></span>
    <span>首批 30 条 <b>2026-12-31</b></span>
    <span>试点费 <b>1.0 万</b></span>
    <span>首批费 <b>4.8 万</b></span>
    <span>正式费 <b>81.7 万</b></span>
  </div>
</header>

<div class="notice">
  <span class="dot"></span>
  <div><b>这是计划基线，不是完成报告。</b> 当前已生产 0 / 500 条，已签约 0 / 104 份专家合同，平台 MVP 未上线。下面的数字是目标、产能和费用，不是实际产出。</div>
</div>

<nav class="toc no-print">
  <a href="#summary">一页看懂</a>
  <a href="#path">生产路径</a>
  <a href="#batches">分批</a>
  <a href="#quota">配额</a>
  <a href="#fee">费用</a>
  <a href="#experts">专家与评审</a>
  <a href="#risk">风险与闸门</a>
</nav>

<div class="kpis">
  <div class="kpi green"><div class="k">总交付</div><div class="v">500</div><div class="d">条原创专业任务</div></div>
  <div class="kpi orange"><div class="k">三段结构</div><div class="v">3 + 30 + 470</div><div class="d">试点、首批、正式生产</div></div>
  <div class="kpi"><div class="k">数据构成</div><div class="v">42 + 458</div><div class="d">法律供应方包与专家自产</div></div>
  <div class="kpi"><div class="k">专家合同</div><div class="v">104</div><div class="d">22 核心 + 4 后备，四批</div></div>
  <div class="kpi green"><div class="k">试点费用</div><div class="v">1.0 万</div><div class="d">3 条，任务费</div></div>
  <div class="kpi orange"><div class="k">首批费用</div><div class="v">4.8 万</div><div class="d">30 条，任务费</div></div>
  <div class="kpi"><div class="k">正式费用</div><div class="v">81.7 万</div><div class="d">470 条，任务费</div></div>
  <div class="kpi red"><div class="k">当前状态</div><div class="v">0 / 500</div><div class="d">未开始生产，先跑 3 条试点</div></div>
</div>

<section class="section" id="summary">
  <div class="sec-head">
    <div><div class="num">01 · 一页看懂</div><h2>先跑 3 条，再交 30 条，最后 470 条</h2></div>
    <p>所有数字为设计基线。正式生产 500 条，试点 3 条不计入。</p>
  </div>
  <p class="lead">用 <b>3 条试点</b>验证专家、资料、合同、转换和判分链路；<b>12 月 31 日前</b>交付首批 <b>30 条</b>；<b>2027 年 4 月 30 日前</b>完成 <b>500 条</b>。费用按试点、首批、正式三段分别估算，详见费用页。</p>
  <div class="grid-3" style="margin-top:16px">
    <div class="card"><span class="tagline">P0 · 试点</span><div class="big">3 条</div><p>不计入 500。11-18 到 11-27，验证合同和链路。3 名专家，3 个方向，商业 1、神经 1、建筑 1。</p></div>
    <div class="card"><span class="tagline">F1 · 首批</span><div class="big">30 条</div><p>计入 500。12-01 到 12-31。商业 14、法律 8、社会 8。22 条专家自产，8 条法律供应方导入。</p></div>
    <div class="card"><span class="tagline">W1 到 W4 · 正式</span><div class="big">470 条</div><p>W1 余 90、W2 128、W3 126、W4 126。01-01 到 04-15，04-16 到 04-30 评测、修补、打包和交付。</p></div>
  </div>
</section>

<section class="section" id="path">
  <div class="sec-head">
    <div><div class="num">02 · 生产路径</div><h2>三段不是串行，W1 与首批并行</h2></div>
    <p>首批 30 条是 W1 的前 30 条。W1 余 90 条不从 01-01 才开始，12-01 就与首批并行。</p>
  </div>
  <div class="gantt">
    <div class="gantt-months">{month_ticks}</div>
    {gantt}
    
  </div>
  <p class="note">时间轴按 2026-11-01 到 2027-05-01 画。W2 到 W4 相邻两批重叠两周，用来吸收返修和节假日。今天 11-12，3 条试点尚未开始。</p>
</section>

<section class="section" id="batches">
  <div class="sec-head">
    <div><div class="num">03 · 分批</div><h2>500 条怎么切</h2></div>
    <p>试点不计入 500。首批与 W1 余量合计 120 条。</p>
  </div>
  <table>
    <thead><tr><th>批次</th><th class="num">数量</th><th>计入 500</th><th>时间</th><th>构成</th><th>目的</th></tr></thead>
    <tbody>
      <tr><td class="name">P0 试点</td><td class="num strong">3</td><td><span class="chip">不计</span></td><td>11-18 到 11-27</td><td>商业 1、神经 1、建筑 1</td><td>合同、资料、转换、判分</td></tr>
      <tr><td class="name">F1 首批</td><td class="num strong">30</td><td><span class="chip chip-orange">计入</span></td><td>12-01 到 12-31</td><td>商业 14、法律 8、社会 8</td><td>首批正式交付</td></tr>
      <tr><td class="name">W1 余量</td><td class="num strong">90</td><td><span class="chip chip-orange">计入</span></td><td>12-01 到 01-15</td><td>商业 36、法律 34、社会 20</td><td>与首批并行，摊薄启动成本</td></tr>
      <tr><td class="name">W2</td><td class="num strong">128</td><td><span class="chip chip-orange">计入</span></td><td>01-01 到 02-15</td><td>心理 34、生命 48、自然 46</td><td>中专业密度批次</td></tr>
      <tr><td class="name">W3</td><td class="num strong">126</td><td><span class="chip chip-orange">计入</span></td><td>02-01 到 03-15</td><td>健康 60、工程 36、农业 16、体育 14</td><td>高专业与长尾批次</td></tr>
      <tr><td class="name">W4</td><td class="num strong">126</td><td><span class="chip chip-orange">计入</span></td><td>03-01 到 04-15</td><td>工程 14、教育 32、视觉 36、交通 30、兜底 14</td><td>收口批次</td></tr>
      <tr class="total-row"><td>合计</td><td class="num">500</td><td>不含 3 条试点</td><td>04-30 交付</td><td>14 个一级类目</td><td>四批完成</td></tr>
    </tbody>
  </table>
  <div class="split" style="margin-top:16px">
    <div class="donut-card"><div class="donut" style="background:conic-gradient(var(--orange) 0 30.24deg,var(--green2) 30.24deg 360deg)"><b>500</b></div><div class="t"><strong>500 条总盘</strong><span>42 条法律供应方包</span><span>458 条专家自产</span></div></div>
    <div class="donut-card"><div class="donut" style="background:conic-gradient(var(--orange) 0 96deg,var(--green2) 96deg 360deg)"><b>30</b></div><div class="t"><strong>首批 30 条</strong><span>8 条法律导入</span><span>22 条专家自产</span></div></div>
    <div class="donut-card"><div class="donut" style="background:conic-gradient(var(--orange) 0 26.04deg,var(--green2) 26.04deg 360deg)"><b>470</b></div><div class="t"><strong>正式 470 条</strong><span>34 条法律导入</span><span>436 条专家自产</span></div></div>
  </div>
  <div class="legend"><span><i class="l1"></i>法律供应方包</span><span><i class="l2"></i>专家自产</span><span>法律 42 条走 ALE-data 导入，不走专家写作和平台评审。</span></div>
</section>

<section class="section" id="quota">
  <div class="sec-head">
    <div><div class="num">04 · 配额</div><h2>14 个一级类目，500 条</h2></div>
    <p>官方 122 条只做参考，不计入 500。computing_math 按项目口径为 0。</p>
  </div>
  <div class="grid-2">
    <div>
      <table>
        <thead><tr><th>一级类目</th><th class="num">官方</th><th class="num">子域/活跃</th><th class="num">配额</th><th>结构</th><th class="num">占比</th></tr></thead>
        <tbody>{''.join(domain_rows)}</tbody>
        <tfoot><tr class="total-row"><td>合计</td><td class="num">122</td><td class="num">55/49</td><td class="num">500</td><td></td><td class="num">100%</td></tr></tfoot>
      </table>
    </div>
    <div>
      <div class="card"><h4>结构判断</h4><p><b>健康 60 条</b>最大，占 12%。工程、商业各 50，法律 42。前四个类目占 40.4%。</p></div>
      <div class="card" style="margin-top:10px"><h4>法律 42 条</h4><p>全部由供应方按 ALE-data 提供，计入 500，但标供应方包。合作方最终验收要接受这个口径。</p></div>
      <div class="card" style="margin-top:10px"><h4>6 个官方零覆盖</h4><p>化工、采矿、精准农业、航空、海事、教育技术，合计给 5 到 11 条种子配额。不是硬凑，研究里有候选工作流。</p></div>
      <div class="card" style="margin-top:10px"><h4>computing 0 条</h4><p>项目口径，不是官方口径。7 个 computing 子域配额为 0，不在这轮生产里。</p></div>
    </div>
  </div>
  <details>
    <summary>展开 56 个二级类目配额</summary>
    <div class="subtable-wrap">
      <table>
        <thead><tr><th>一级</th><th>二级</th><th class="num">官方</th><th class="num">候选</th><th class="num">配额</th><th>批次</th><th>首批</th></tr></thead>
        <tbody>{''.join(sub_rows)}</tbody>
        <tfoot><tr class="total-row"><td>合计</td><td>55 个官方子域 + 1 个兜底桶</td><td class="num">122</td><td class="num">174</td><td class="num">500</td><td>四批</td><td>6 子域</td></tr></tfoot>
      </table>
    </div>
    <p class="note">首批列的“首批”标的是子域，不是人数。首批 30 条从 6 个子域出，商业 14、法律 8、社会 8。</p>
  </details>
</section>

<section class="section" id="fee">
  <div class="sec-head">
    <div><div class="num">05 · 费用</div><h2>三段分别估算，不做总包价</h2></div>
    <p>按条计价，不按小时。试点、首批、正式三层，层内按类目定价；本页不汇总总数。</p>
  </div>
  <div class="grid-3" style="margin-top:0">
    <div class="kpi green"><div class="k">试点 · 3 条</div><div class="v">1.0 万</div><div class="d">商业 1、神经 1、建筑 1</div></div>
    <div class="kpi orange"><div class="k">首批 · 30 条</div><div class="v">4.8 万</div><div class="d">商业 14、法律 8、社会 8</div></div>
    <div class="kpi"><div class="k">正式 · 470 条</div><div class="v">81.7 万</div><div class="d">W1 余 90、W2 128、W3 126、W4 126</div></div>
  </div>

  <h3>按类目的三层价格</h3>
  <table>
    <thead><tr><th>类目</th><th class="num">试点 3</th><th class="num">首批 30</th><th class="num">正式 470</th><th>单价（试点/首批/正式）</th><th class="num">小计</th></tr></thead>
    <tbody>{''.join(fee_rows)}</tbody>
  </table>
  <p class="note">表中只列每个类目的阶段小计，不列总数。建筑执业签字 3 条已含在工程 50 条内，不重复计任务。3,000 元是另付给外部注册工程师的签字费。</p>

  <div class="grid-2" style="margin-top:18px">
    <div>
      <h3>三阶段预估</h3>
      <table>
        <thead><tr><th>阶段</th><th class="num">任务数</th><th class="num">任务费预估</th></tr></thead>
        <tbody>
          <tr><td>试点</td><td class="num">3</td><td class="num">10,000</td></tr>
          <tr><td>首批 30</td><td class="num">30</td><td class="num">48,000</td></tr>
          <tr><td>正式 470</td><td class="num">470</td><td class="num">817,000</td></tr>
        </tbody>
      </table>
      <p class="note">三段分别估算，不做总包价。单价按任务计，不按小时。</p>
    </div>
    <div>
      <div class="card"><h4>计价口径</h4><p>单价按任务计，不按小时。正式阶段单价已按平台自动化和 AI 辅助后的工时估算；首批 30 条后按实测工时和返修轮次校准，未达标则执行正式价上调条款。</p></div>
      <div class="card" style="margin-top:12px"><h4>分段核算</h4><p>只给试点、首批、正式三段的任务费预估，不汇总总包价。每段按任务数和类目单价独立核算，便于分段批复和分段考核。</p></div>
    </div>
  </div>

  <h3>付款、返修、材料</h3>
  <div class="grid-3">
    <div class="card"><h4>付款</h4><p>试点 50% 启动、50% 验收。首批和正式 30% 启动、40% 交稿、30% 验收。法律供应方 50% 导入校验、50% 转换通过。</p></div>
    <div class="card"><h4>返修</h4><p>两轮返修含在单价内。第三轮 150 元一小时，单任务封顶 1,000 元。两次验收不过，不再付最后 30%，任务改派。</p></div>
    <div class="card"><h4>材料</h4><p>原始资料由专家提供，平台脱敏、存储和记录授权。资料不齐可用 Agent 合成，合成件必须标注，每个任务至少保留一份真实来源。</p></div>
  </div>
</section>

<section class="section" id="experts">
  <div class="sec-head">
    <div><div class="num">06 · 专家与评审</div><h2>22 名核心，4 名后备，评审不另招</h2></div>
    <p>专家主线生产，副线评审。系统自动派单，不设专职评审岗位。</p>
  </div>
  <div class="grid-2">
    <div>
      <div class="grid-3">
        <div class="card"><div class="big">22 + 4</div><p>每批核心与后备</p></div>
        <div class="card"><div class="big">104</div><p>四批合同席位</p></div>
        <div class="card"><div class="big">44</div><p>峰值同时在产</p></div>
      </div>
      <div class="card" style="margin-top:12px"><h4>产能口径</h4><p>20 小时一周，6.5 周一批，四批重叠两周。实际人头 90 到 104，工程类目可在 W3 和 W4 续签，其余不跨批复用。3 条试点 3 名专家，首批 9 份招募合同。</p></div>
      <div class="card" style="margin-top:12px"><h4>评审副线</h4><p>每批 22 名核心分 294 小时，每人约 13.4 小时、5 到 6 条，折每周约 2 小时。总负荷上限 1,175 小时，法律 42 条不排评审，实际约 1,073 小时。5 个工作日 SLA，10% 双评，错误率高的移出评审池。</p></div>
    </div>
    <div>
      <h3 style="margin-top:0">招募漏斗</h3>
      {funnel_bars}
      <p class="note">漏斗按 104 份合同等比放大，比例沿用旧基准，数字是推断。3 条试点按画像触达 56 条冷启动，不依赖名单。</p>
      <div class="card" style="margin-top:12px"><h4>画像与试标</h4><p>16 个专家画像覆盖 14 个一级类目。通用门槛 3 年以上经验，能拿公开或合成资料，英文任务文本，每周 20 小时。试标固定 1,000 元、4 小时封顶，通过后 14 天内签约可抵首笔。</p></div>
    </div>
  </div>
</section>

<section class="section" id="risk">
  <div class="sec-head">
    <div><div class="num">07 · 风险与闸门</div><h2>四个闸门，六个风险</h2></div>
    <p>先过合同，再过首批，最后过交付。任何一闸不过，不扩量。</p>
  </div>
  <div class="gate">
    <div class="g"><b>11-27</b><span>3 条试点 3/3 PASS</span></div>
    <div class="g"><b>12-15</b><span>22 名核心到位</span></div>
    <div class="g"><b>12-31</b><span>首批 30 条通过四道门</span></div>
    <div class="g"><b>04-30</b><span>500 条交付</span></div>
  </div>
  <table class="risk-table" style="margin-top:16px">
    <thead><tr><th>风险</th><th>触发</th><th>影响</th><th>应对</th></tr></thead>
    <tbody>
      <tr><td>试点不过</td><td>11-27 未 3/3</td><td>首批 12-31 失守</td><td>切 5 条试点方案，30 条顺延到 01-08</td></tr>
      <tr><td>专家不到位</td><td>12-15 未到 22 名</td><td>首批 30 条和 W1 余量挤压</td><td>后备转正，缩 W1 余量，保首批</td></tr>
      <tr><td>平台未上线</td><td>11-30 MVP 未可用</td><td>首批只能手工兜底</td><td>手工评审和手工导出，平台后补</td></tr>
      <tr><td>AI 不达预期</td><td>工时中位数高于 16 小时，或 AI 辅助使用率低于 50%</td><td>正式阶段单价上调，或正式量缩减</td><td>正式价加 300 到 500 元一条，或正式量从 470 降到 400</td></tr>
      <tr><td>法律包不被接受</td><td>合作方不接受供应方包</td><td>500 条要重排，法律 42 条要另找专家</td><td>签约前书面确认口径，预留 2 名法律专家后备</td></tr>
      <tr><td>建筑签字人未定</td><td>11-28 没有签字人</td><td>工程 3 条不能放行</td><td>换 3 条其他工程任务，不占建筑配额</td></tr>
    </tbody>
  </table>
</section>

<section class="section">
  <div class="confirm">
    <div class="num" style="color:#8a5a1f">待确认事项</div>
    <h3>三件事定了，计划就能锁版</h3>
    <ol>
      <li><b>500 条配额</b>按本文 14 个一级类目执行，法律 42 条供应方包计入 500。</li>
      <li><b>三段费用</b>按试点 1.0 万、首批 4.8 万、正式 81.7 万分别批复，不做总包价。</li>
      <li><b>交付节奏</b>为 12-31 首批 30 条，04-30 完成 500 条。</li>
    </ol>
  </div>
</section>

<footer class="footer">
  <p>口径来源：<a href="../../docs/07-expert-supply.md">docs/07-expert-supply.md</a>、<a href="../../docs/02-plan.md">docs/02-plan.md</a>、<a href="../../docs/04-roles-and-decisions.md">docs/04-roles-and-decisions.md</a>、<a href="../../docs/06-decisions-and-blockers.md">docs/06-decisions-and-blockers.md</a>。数据截至 2026-11-12。</p>
  <p>这是计划基线，不是完成报告。所有任务数为计划值，当前生产 0 条、签约 0 份、平台未上线。详细执行稿在 `plan/expert-supply` 与 `plan/platform-p1` 分支。</p>
</footer>

</div>
<button class="print-btn no-print" onclick="window.print()">打印 / 存为 PDF</button>
<script>
window.addEventListener('beforeprint', function(){{
  document.querySelectorAll('details').forEach(function(d){{ d.open = true; }});
}});
</script>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(HTML)
print(OUT)
print(f"domains={len(domains)} subs={len(subs)} fees={len(fees)}")
print(f"quota={sum(d['quota'] for d in domains)} official={sum(d['official'] for d in domains)}")
print(f"fee={sum(f['subtotal'] for f in fees):,} counts={sum(f['pilot'] for f in fees)}/{sum(f['first'] for f in fees)}/{sum(f['formal'] for f in fees)}")
