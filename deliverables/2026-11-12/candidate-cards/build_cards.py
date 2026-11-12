from pathlib import Path

ROLES = [
    {
        "id": "p-b1-accounting",
        "tag": "商业与金融 · 会计",
        "title": "会计与财务分析<br>任务设计专家",
        "accent": "#a66a1f",
        "lede": "把一张财报勾稽表，变成一道同行能复现、能判分的专业任务。",
        "do": "你会用两家同行业公司的公开财报，设计一条会计核对与异常识别任务。",
        "do_bullets": [
            "选两家公司，定三年财报范围和任务边界。",
            "写任务说明、输入文件、操作步骤、预期交付物和成功标准。",
            "做一份参考解，标出三处异常和判断依据。",
            "和工程一起确认任务能运行、能判分，不写代码。",
        ],
        "deliver": [
            "一份任务源，按统一模板的十块字段填写。",
            "一份资料清单，写清公开来源和授权说明。",
            "一份参考交付物和评分要点。",
            "一次评审答复，最多两轮返修。",
        ],
        "must": [
            "3 年以上财报分析、审计、FP&A 或预算经验。",
            "能读三张表，做勾稽，识别收入确认和现金流异常。",
            "能用英文写任务说明和交付物。",
            "能拿到公开财报、招股书或监管问询。",
        ],
        "chips": ["Excel", "三表勾稽", "收入确认", "现金流质量", "英文 memo"],
        "trial": "两家公司三年财报，做一张勾稽表，标三处异常，写 300 字英文 memo。",
        "fit": [
            "你喜欢解释“我是怎么发现这个异常的”。",
            "你能把判断拆成别人能照着做的步骤。",
            "你愿意只用公开或合成资料。",
        ],
        "notfit": [
            "你只想给投资结论，不想拆步骤。",
            "你只能用客户底稿或未公开资料。",
            "你不能写英文，或不能保证每周 20 小时。",
        ],
    },
    {
        "id": "p-n1-neuroimaging",
        "tag": "心理与神经 · 神经影像",
        "title": "神经影像<br>任务设计专家",
        "accent": "#356b86",
        "lede": "把一次 DICOM 到 BIDS 的整理，变成一道可复现、可质控的影像任务。",
        "do": "你会用 5 个被试的公开 DICOM，设计一条影像数据整理与质量检查任务。",
        "do_bullets": [
            "定数据集、模态和去识别边界。",
            "写转换步骤、目录结构、质量检查和失败处理。",
            "跑 bids-validator，把常见错误和修法写进任务。",
            "做一份参考 BIDS 结构和质量报告，不写平台代码。",
        ],
        "deliver": [
            "一份任务源，按统一模板的十块字段填写。",
            "一份数据清单，写清公开来源和去识别说明。",
            "一份参考 BIDS 结构和质量报告。",
            "一次评审答复，最多两轮返修。",
        ],
        "must": [
            "3 年以上 DICOM、BIDS、fMRIPrep 或相关影像处理经验。",
            "懂去识别和再识别风险，知道哪些元数据必须删。",
            "能用 dcm2niix、fMRIPrep、bids-validator 或同类工具。",
            "能拿到 OpenNeuro 公开数据或合成 DICOM。",
        ],
        "chips": ["dcm2niix", "fMRIPrep", "bids-validator", "OpenNeuro", "去识别"],
        "trial": "5 个被试 DICOM 转 BIDS，跑 bids-validator，列三个常见错误和修法，写 300 字英文方法说明。",
        "fit": [
            "你对元数据和去识别很谨慎。",
            "你能解释 validator 报错，而不是只会重跑。",
            "你愿意用公开数据，不碰患者数据。",
        ],
        "notfit": [
            "你只做临床扫描，不熟悉 BIDS 或 fMRIPrep。",
            "你觉得去识别可以“差不多就行”。",
            "你只想用医院患者数据，不能提供公开或合成数据。",
        ],
    },
    {
        "id": "p-e1-building-energy",
        "tag": "工程与建筑 · 建筑节能",
        "title": "建筑节能<br>任务设计专家",
        "accent": "#4d7346",
        "lede": "把一次能耗模型校准，变成一道能判定对错、能复现的 M&V 任务。",
        "do": "你会用 12 个月账单和气象数据，设计一条建筑能耗模型校准与 M&V 任务。",
        "do_bullets": [
            "定建筑边界、用能系统和数据口径。",
            "写基线校准步骤、验收指标和失败处理。",
            "做一次参考校准，报告 CVRMSE 和 NMBE。",
            "和工程一起确认任务能运行、能判分，不写代码。",
        ],
        "deliver": [
            "一份任务源，按统一模板的十块字段填写。",
            "一份数据清单，写清公开或合成来源。",
            "一份参考校准报告和排查路径。",
            "一次评审答复，最多两轮返修。",
        ],
        "must": [
            "3 年以上 EnergyPlus、ASHRAE Guideline 14、计量与验证经验。",
            "能读电费、燃气账单和气象数据，能做基线校准。",
            "懂 CVRMSE、NMBE 和常见不达标原因。",
            "能拿到公开建筑数据或合成计量数据。",
        ],
        "chips": ["EnergyPlus", "OpenStudio", "ASHRAE 14", "CVRMSE", "M&V"],
        "trial": "12 个月账单校准一个小模型，报告 CVRMSE 和 NMBE，列三个不达标原因和排查顺序。",
        "fit": [
            "你喜欢解释“校准为什么没过”。",
            "你能把模型边界和数据口径说清楚。",
            "你愿意用公开或合成数据，不碰业主真实账单。",
        ],
        "notfit": [
            "你只做设计或咨询，不做计量验证。",
            "你只会用 Excel 估算，不会 EnergyPlus。",
            "你只能用业主真实账单，不能提供公开或合成数据。",
        ],
    },
]

CSS = """
:root {
  --ink: #1c231e;
  --muted: #5d685f;
  --line: #d9d2c5;
  --paper: #fbf8f1;
  --soft: #f2eee5;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: #e8e3d8;
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
}
.page {
  width: 210mm;
  min-height: 297mm;
  margin: 18px auto;
  padding: 14mm 14mm 11mm;
  background: var(--paper);
  box-shadow: 0 12px 40px rgba(28, 35, 30, .14);
  position: relative;
  overflow: hidden;
}
.hero {
  border-top: 6px solid var(--accent);
  padding-top: 7mm;
}
.kicker {
  font-size: 9.5px;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--muted);
  font-weight: 600;
}
.role-tag {
  display: inline-block;
  margin-top: 5mm;
  padding: 2.5px 8px;
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
}
h1 {
  margin: 4mm 0 3mm;
  font-family: "Songti SC", "Noto Serif SC", "STSong", serif;
  font-size: 34px;
  line-height: 1.16;
  letter-spacing: -.02em;
  font-weight: 700;
}
.lede {
  margin: 0;
  max-width: 155mm;
  font-size: 13.5px;
  line-height: 1.7;
  color: #35423a;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 4mm;
}
.meta span {
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--soft);
  color: #445047;
  font-size: 9.5px;
}
.grid {
  display: grid;
  grid-template-columns: 1.32fr .88fr;
  gap: 8mm;
  margin-top: 7mm;
}
h2 {
  margin: 0 0 2mm;
  font-size: 10.5px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
}
p, li {
  font-size: 11.2px;
  line-height: 1.62;
}
p { margin: 0 0 2mm; }
ul {
  margin: 0 0 4.5mm;
  padding-left: 14px;
}
li { margin-bottom: 1.2mm; }
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 2mm;
}
.chip {
  padding: 2.5px 7px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fff;
  color: #3d4a41;
  font-size: 9.5px;
}
.offer {
  margin-top: 3mm;
  padding-top: 2.5mm;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 9.5px;
  line-height: 1.6;
}
.side .box {
  padding: 2.6mm 3mm;
  margin-bottom: 2.4mm;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: #fff;
}
.side h3 {
  margin: 0 0 1.6mm;
  font-size: 10px;
  color: var(--ink);
}
.side p, .side li {
  font-size: 9.7px;
  line-height: 1.55;
}
.side ul {
  margin: 0;
  padding-left: 12px;
}
.side li { margin-bottom: 1mm; }
.trial {
  border-left: 2px solid var(--accent);
  padding-left: 2.2mm;
}
.bottom {
  display: grid;
  grid-template-columns: 1.05fr .95fr;
  gap: 7mm;
  margin-top: 4mm;
  padding-top: 4mm;
  border-top: 1px solid var(--line);
}
.bottom h2 {
  margin-bottom: 2mm;
}
.about p {
  font-size: 10.2px;
  line-height: 1.65;
  margin: 0;
}
.faq dl {
  margin: 0;
}
.faq dt {
  font-size: 10.2px;
  font-weight: 700;
  margin-top: 1.6mm;
}
.faq dd {
  margin: .5mm 0 0;
  font-size: 9.8px;
  line-height: 1.55;
  color: #445047;
}
.next {
  grid-column: 1 / -1;
  margin-top: 1mm;
  padding: 3mm 4mm;
  background: var(--soft);
  border-left: 3px solid var(--accent);
  font-size: 10.5px;
  line-height: 1.6;
}
.next .small {
  display: block;
  margin-top: 1.2mm;
  font-size: 9px;
  color: var(--muted);
}
@media print {
  body { background: #fff; }
  .page {
    margin: 0;
    box-shadow: none;
    width: 210mm;
    min-height: 297mm;
  }
}
"""

TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_plain} · ALE 专业任务计划</title>
<style>{css}</style>
</head>
<body>
<div class="page" style="--accent: {accent}">
  <header class="hero">
    <div class="kicker">ALE 专业任务计划 · 领域专家（兼职）</div>
    <div class="role-tag">{tag}</div>
    <h1>{title}</h1>
    <p class="lede">{lede}</p>
    <div class="meta">
      <span>兼职 · 按任务合作</span>
      <span>远程</span>
      <span>2 到 3 周</span>
      <span>每周约 20 小时</span>
      <span>付费试标</span>
    </div>
  </header>

  <main class="grid">
    <section class="main">
      <h2>你在做什么</h2>
      <p>{do}</p>
      <ul>{do_bullets}</ul>

      <h2>你会交付什么</h2>
      <ul>{deliver}</ul>

      <h2>我们希望你具备</h2>
      <ul>{must}</ul>
      <div class="chips">{chips}</div>
      <div class="offer">我们提供：任务模板、30 分钟 kickoff、工程与环境支持、AI 与翻译辅助、公开或合成资料指引。你不需要写 Docker、验证器或平台代码。</div>
    </section>

    <aside class="side">
      <div class="box">
        <h3>合作方式</h3>
        <p>远程，按任务合作。1 条试点任务，2 到 3 周，每周约 20 小时。任务文本用英文，沟通可用中文。试标和试点任务均有报酬，具体在签约前确认。</p>
      </div>
      <div class="box">
        <h3>筛选流程</h3>
        <p>20 分钟沟通 → 4 小时试标 → 1 条试点任务。</p>
      </div>
      <div class="box">
        <h3>4 小时试标</h3>
        <p class="trial">{trial}</p>
      </div>
      <div class="box">
        <h3>适合你，如果你</h3>
        <ul>{fit}</ul>
      </div>
      <div class="box">
        <h3>可能不适合，如果你</h3>
        <ul>{notfit}</ul>
      </div>
    </aside>
  </main>

  <section class="bottom">
    <div class="about">
      <h2>关于这个项目</h2>
      <p>ALE（Agents' Last Exam）是一个评测 AI 在真实专业工作中表现的基准，覆盖多个行业。我们正在为它设计一批新的专业任务。你要做的，是把一项真实工作拆成可运行、可评测的任务，让另一个同行能照着做，让工程能跑，让评审能判分。</p>
    </div>
    <div class="faq">
      <h2>常见问题</h2>
      <dl>
        <dt>需要写代码吗？</dt>
        <dd>不需要。你写任务和资料，工程负责环境、验证器、运行。</dd>
        <dt>需要客户数据吗？</dt>
        <dd>不需要。只用公开或合成数据。</dd>
        <dt>英文不好怎么办？</dt>
        <dd>任务文本用英文，可用翻译工具或 AI，沟通用中文。</dd>
        <dt>这是全职吗？</dt>
        <dd>不是。按任务合作，2 到 3 周，每周约 20 小时。</dd>
      </dl>
    </div>
    <div class="next">下一步：20 分钟沟通 → 4 小时试标 → 1 条试点任务。感兴趣请回复招募负责人，附上方向与相关经历。<span class="small">这不是全职岗位。按任务合作，资料只用公开或合成数据，不接触客户或患者材料。</span></div>
  </section>

</div>
</body>
</html>
"""


def li(items):
    return "".join(f"<li>{x}</li>" for x in items)


def main():
    out = Path(__file__).parent
    for role in ROLES:
        html = TEMPLATE.format(
            css=CSS,
            title=role["title"],
            title_plain=role["title"].replace("<br>", " "),
            tag=role["tag"],
            accent=role["accent"],
            lede=role["lede"],
            do=role["do"],
            do_bullets=li(role["do_bullets"]),
            deliver=li(role["deliver"]),
            must=li(role["must"]),
            chips="".join(f'<span class="chip">{x}</span>' for x in role["chips"]),
            trial=role["trial"],
            fit=li(role["fit"]),
            notfit=li(role["notfit"]),
        )
        path = out / f"{role['id']}.html"
        path.write_text(html)
        print(path)


if __name__ == "__main__":
    main()
