# S1-02B1 child-worker resilience protocol (mandatory text for future rounds)

Lessons from S1-02B1: two child workers died silently after completing research but
before/during file writing (med_b original, life_cluster original + resume). Cause
unproven, pattern consistent: accumulate everything in context, write at the end,
die at the write step or just before it.

Mandatory text for every research-child brief in future rounds:
1. Write output files EARLY and INCREMENTALLY: after the first subdomain, write the
   CSV with header + rows via csv.DictWriter, re-read from disk; after each later
   subdomain, rewrite the full accumulated file, re-read. Never hold all rows until the end.
2. Never abort on tool errors (web_search/web_fetch 403/timeout): retry once, then
   continue with other sources, record the failure honestly in the row.
3. Write files BEFORE composing the final return message; verify with re-read asserts.
4. Known bot-block patterns this environment hits: EGA/dbGaP registration pages 403/404,
   OECD/ECHA Cloudflare 403, IAEA/NIST bot protection. Briefs should pre-empt these:
   "do not burn time retrying them; cite public docs and record honest pending-flags."
