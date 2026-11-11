# -*- coding: utf-8 -*-
import csv,re,hashlib,collections,os,sys
ok=True
def chk(name,cond,detail=""):
    global ok
    print(("PASS " if cond else "FAIL ")+name+(" "+detail if detail else ""))
    ok = ok and cond

FILES=["S1_02B3_SCOPE_MATRIX.csv","S1_02B3_WORKFLOW_CANDIDATES.csv","S1_02B3_SOURCE_CLAIM_MAP.csv",
       "S1_02B3_DUPLICATE_ATTRIBUTION.csv","S1_02B3_OVERLAP_AND_RISKS.md","S1_02B3_REVIEW_SUMMARY.md"]
for f in FILES: chk("file "+f, os.path.isfile(f) and os.path.getsize(f)>0, str(os.path.getsize(f) if os.path.exists(f) else 0))

wf=list(csv.DictReader(open(FILES[1],encoding="utf-8")))
chk("workflow rows=27", len(wf)==27, str(len(wf)))
chk("workflow cols=43", len(wf[0])==43, str(len(wf[0])))
cnt=collections.Counter(r["subdomain_code"] for r in wf)
chk("9 subdomains x3", len(cnt)==9 and all(v==3 for v in cnt.values()), str(dict(cnt)))
chk("no E2/E4", all(r["evidence_level"] in {"E1","E3"} for r in wf))
chk("linux all NOT_VERIFIED", all(r["linux_verification_state"]=="NOT_VERIFIED" for r in wf))
chk("ids unique", len({r["candidate_id"] for r in wf})==27)
sm=list(csv.DictReader(open(FILES[2],encoding="utf-8")))
chk("claim map rows=27", len(sm)==27)
chk("claim ids match", {r["candidate_id"] for r in sm}=={r["candidate_id"] for r in wf})
dur=list(csv.DictReader(open(FILES[3],encoding="utf-8")))
chk("dup rows=10 all no", len(dur)==10 and all(r["substantively_duplicate"]=="no" for r in dur))
sc=list(csv.DictReader(open(FILES[0],encoding="utf-8")))
chk("matrix rows=9", len(sc)==9)
chk("matrix batch ok", all(r["s1_02b3_batch"]=="batch_3" for r in sc))
chk("matrix counts=3", all(int(r["candidate_workflow_count"])==3 for r in sc))
md1=open(FILES[4],encoding="utf-8").read(); md2=open(FILES[5],encoding="utf-8").read()
heads=["视觉媒体与工程设计邻接边界","视觉媒体与商业金融品牌资产","交通安全与城市规划工程","教育信息与健康医疗宣教","教育信息与法律出版与版权"]
chk("5 group headers in overlap", all(h in md1 for h in heads))
items=[m.group(1).strip() for m in re.finditer(r"^\d+\.\s+(.+)$",open("evidence/s1_02b2_research/b1_open_review_items.md",encoding="utf-8").read(),re.M)]
chk("B1 five items verbatim in both md", all(i in md1 and i in md2 for i in items), str(len(items)))
b2=hashlib.sha256(open("S1_02B2_EFFECTIVE_CANDIDATES.csv","rb").read()).hexdigest()
chk("B2-effective unchanged", b2=="eb99cdb41962bc120aa16c77641c6fc457195b6b1dd52f0145efc2854be05e3f", b2[:12])
for f in ["S1_02A_EFFECTIVE_CANDIDATES.csv","S1_02B1_WORKFLOW_CANDIDATES.csv","S1_01_CATEGORY_MAPPING.csv"]:
    chk("frozen readable "+f, os.path.isfile(f))
print("---")
print("level",dict(collections.Counter(r["evidence_level"] for r in wf)))
print("kind",dict(collections.Counter(r["evidence_kind"] for r in wf)))
print("mode",dict(collections.Counter(r["source_support_mode"] for r in wf)))
print("adapt",dict(collections.Counter(r["software_adaptation"] for r in wf)))
print("eng_pending_nonempty",sum(1 for r in wf if r["engineering_pending"]))
print("expert_pending_nonempty",sum(1 for r in wf if r["expert_pending"]))
print("ALL", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
