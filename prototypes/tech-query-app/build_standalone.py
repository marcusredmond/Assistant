"""Generate the single-file, zero-setup, offline EKA tech-query standalone app.

This script produces `tech-query-standalone.html`: ONE self-contained HTML file
that embeds the entire JEM-GEN-SPC-M-014 atom corpus and reimplements the exact
same deterministic retrieval as `server.py`, all in inline vanilla JavaScript.
It runs by double-clicking the file (file:// protocol) in a browser. No server,
no Python, no install, no internet, no CDNs, no external fonts/scripts/styles.

Why this exists: the server-based prototype (`server.py`) needs Python running
and a localhost connection. On a locked-down PC with no dev tools, that is not
possible. The embedded data MUST be inlined because browsers block fetch()/XHR
of local files over file://. So the generator serialises the corpus into a
`<script type="application/json" id="eka-atoms">` block that the page parses at
load, and the retrieval/rendering runs entirely client-side.

Design constraints (match server.py exactly):
  * Python standard library ONLY. Deterministic and idempotent: re-running
    yields byte-identical output (so a committed HTML has no spurious diff).
  * Retrieval mirrors server.py: same tokenise rules, same field weights
    (clause 6, clause_title 4, applies_to 2, rule_text 1), same threshold 1,
    same sort (score desc, clause, rule_id), same cap of 10, same honest
    no-answer message, same citation format, same guardrail wording.

Run:
    cd prototypes/tech-query-app && python3 build_standalone.py
"""

from __future__ import annotations

import json
import os

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir, os.pardir))
CORPUS_PATH = os.path.join(
    _REPO_ROOT,
    "knowledge",
    "jem-gen-spc-m-014",
    "atoms",
    "jem-gen-spc-m-014.atoms.jsonl",
)
OUTPUT_PATH = os.path.join(_HERE, "tech-query-standalone.html")

# The exact verbatim draft marker from the corpus manifest (em dash preserved).
DRAFT_MARKER = "DRAFT \u2014 pending engineering review"

# Honest no-answer fallback, identical text to server.py NO_ANSWER_MESSAGE.
NO_ANSWER_MESSAGE = (
    "The JEM-GEN-SPC-M-014 corpus does not contain a governing obligation that "
    "matches this question as asked. This prototype will not guess, infer, or "
    "fabricate a clause number, limit, or acceptance criterion. Please rephrase "
    "using the specification's terms, or defer to the responsible engineer and "
    "the authoritative JEM-GEN-SPC-M-014 document."
)


# --------------------------------------------------------------------------- #
# Corpus loading (same shape as server.load_atoms)
# --------------------------------------------------------------------------- #

def load_atoms(path: str = CORPUS_PATH):
    """Load the atom corpus from a JSONL file. One JSON object per non-blank line."""
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "Corpus not found at {}. Expected the JEM-GEN-SPC-M-014 atom corpus "
            "(knowledge/jem-gen-spc-m-014/atoms/jem-gen-spc-m-014.atoms.jsonl). "
            "Run this generator from a branch that contains the corpus.".format(path)
        )
    atoms = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                atoms.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Malformed JSON on line {} of {}: {}".format(lineno, path, exc)
                )
    return atoms


def _embed_json(atoms):
    """Serialise atoms deterministically for inlining in a <script> JSON block.

    `ensure_ascii=False` keeps characters such as the en dash and degree symbol
    intact (the page is UTF-8). `sort_keys=True` + fixed separators make the
    output deterministic/idempotent. The only unsafe sequence inside an HTML
    <script> block is `</` (it can prematurely close the tag), so escape it as
    `<\\/`; JSON parsers treat `<\\/` and `</` identically, so this is lossless.
    """
    text = json.dumps(
        atoms,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return text.replace("</", "<\\/")


# --------------------------------------------------------------------------- #
# HTML template
# --------------------------------------------------------------------------- #
# The two Python-side substitutions are the embedded JSON corpus and the
# draft/no-answer constants. Everything else is literal. We avoid str.format on
# the whole template (the CSS/JS use braces heavily) and use simple token
# replacement on unique placeholders instead.

_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>EKA tech-query standalone &#8212; JEM-GEN-SPC-M-014</title>
<style>
  :root {
    --ink: #1b2430;
    --muted: #5b6b7b;
    --line: #d8dee6;
    --bg: #f4f6f9;
    --card: #ffffff;
    --accent: #0b5394;
    --warn-bg: #fff4e5;
    --warn-line: #e0a640;
    --mono: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Consolas, monospace;
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: var(--sans); line-height: 1.5; font-size: 16px;
  }
  .banner {
    background: var(--warn-bg); border-bottom: 2px solid var(--warn-line);
    color: #6b4a10; padding: 10px 16px; font-size: 14px; text-align: center;
  }
  .banner strong { color: #5a3d08; }
  .banner .offline { display: block; margin-top: 4px; font-size: 13px; }
  header { padding: 20px 16px 8px; max-width: 980px; margin: 0 auto; }
  header h1 { margin: 0 0 4px; font-size: 22px; }
  header p { margin: 0; color: var(--muted); font-size: 14px; }
  main { max-width: 980px; margin: 0 auto; padding: 12px 16px 48px; }
  .tabs { display: flex; gap: 6px; border-bottom: 1px solid var(--line); margin: 14px 0 18px; }
  .tab {
    border: 1px solid var(--line); border-bottom: none; background: #eef1f5;
    padding: 8px 14px; cursor: pointer; border-radius: 6px 6px 0 0; font-size: 14px;
    color: var(--muted);
  }
  .tab[aria-selected="true"] { background: var(--card); color: var(--ink); font-weight: 600; }
  .ask-row { display: flex; gap: 8px; margin-bottom: 10px; }
  #q {
    flex: 1; padding: 11px 12px; font-size: 16px; border: 1px solid var(--line);
    border-radius: 6px; font-family: var(--sans);
  }
  button.primary {
    padding: 11px 18px; font-size: 15px; background: var(--accent); color: #fff;
    border: none; border-radius: 6px; cursor: pointer;
  }
  button.primary:hover { background: #094074; }
  .examples { margin: 4px 0 16px; font-size: 14px; color: var(--muted); }
  .examples button {
    background: #eaf1f8; border: 1px solid #c7dbef; color: var(--accent);
    border-radius: 14px; padding: 5px 12px; margin: 3px 4px 0 0; cursor: pointer;
    font-size: 13px;
  }
  .examples button:hover { background: #dceafa; }
  .qline { font-size: 15px; color: var(--muted); margin: 6px 0 14px; }
  .qline b { color: var(--ink); }
  .atom {
    background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--accent);
    border-radius: 8px; padding: 14px 16px; margin: 0 0 14px;
  }
  .rule-text {
    font-size: 16px; margin: 0 0 10px; white-space: pre-wrap;
    background: #f7f9fb; border: 1px solid var(--line); border-radius: 6px; padding: 10px 12px;
  }
  .cite { font-family: var(--mono); font-size: 13px; color: var(--accent); margin: 0 0 8px; word-break: break-word; }
  .meta { font-size: 14px; margin: 2px 0; }
  .meta .label { color: var(--muted); display: inline-block; min-width: 112px; }
  .pill {
    display: inline-block; font-size: 12px; padding: 2px 8px; border-radius: 10px;
    background: #eef1f5; color: var(--muted); margin-left: 4px;
  }
  .pill.shall { background: #fde8e8; color: #a12020; }
  .pill.not_permitted, .pill.prohibited { background: #f3dede; color: #7a1414; }
  .pill.may { background: #e6f0e6; color: #2a6b2a; }
  .pill.informational { background: #eef1f5; color: var(--muted); }
  .pill.hold { background: #fff0d6; color: #8a5a00; }
  .noanswer {
    background: #fff; border: 1px solid var(--warn-line); border-left: 4px solid var(--warn-line);
    border-radius: 8px; padding: 16px; color: #6b4a10; font-size: 15px;
  }
  .draft-marker {
    font-family: var(--mono); font-size: 12px; color: #8a5a00; background: var(--warn-bg);
    border: 1px dashed var(--warn-line); border-radius: 6px; padding: 6px 10px;
    display: inline-block; margin-bottom: 14px;
  }
  .checklist-group h3 { margin: 18px 0 8px; font-size: 16px; }
  .hidden { display: none; }
  .count { color: var(--muted); font-size: 14px; margin: 0 0 10px; }
  footer { max-width: 980px; margin: 0 auto; padding: 0 16px 40px; color: var(--muted); font-size: 12px; }
  code { font-family: var(--mono); font-size: 13px; }
</style>
</head>
<body>
<div class="banner">
  <strong>LOCAL / OFFLINE demonstration only.</strong>
  Not connected to any Power Platform / Microsoft 365 tenant. Answers are grounded on the
  committed JEM-GEN-SPC-M-014 atom corpus and are DRAFTS for qualified-engineer review.
  <span class="offline">This single file runs entirely in your browser with <b>no server</b> &#8212;
  the corpus is embedded in the page, so it works when opened directly from the file system
  (that is why this works even though localhost refused to connect).</span>
</div>

<header>
  <h1>Engineering Knowledge Assistant &#8212; tech-query (standalone)</h1>
  <p>Grounded Q&amp;A over <b>JEM-GEN-SPC-M-014</b> "Piping and Mechanical Equipment &#8211;
     Shop Fabrication Specification For Facilities" (version 4), Jemena shop-fabrication scope.
     Deterministic keyword retrieval; it quotes the governing rule verbatim and cites clause + rule_id.
     It never invents clause numbers or limits.</p>
</header>

<main>
  <div class="tabs" role="tablist">
    <div class="tab" role="tab" id="tab-ask" aria-selected="true" tabindex="0">Ask a question</div>
    <div class="tab" role="tab" id="tab-checklist" aria-selected="false" tabindex="0">Hold &amp; witness / approvals</div>
  </div>

  <!-- ASK VIEW -->
  <section id="view-ask">
    <div class="ask-row">
      <input id="q" type="text" placeholder="e.g. max interpass temperature for carbon steel"
             autocomplete="off" aria-label="Engineering question" />
      <button class="primary" id="askBtn">Ask</button>
    </div>
    <div class="examples">
      Try:
      <button class="ex" data-q="max interpass temperature for carbon steel">max interpass temperature for carbon steel</button>
      <button class="ex" data-q="how do I raise a deviation">how do I raise a deviation</button>
      <button class="ex" data-q="branch connection requirements">branch connection requirements</button>
    </div>
    <div id="results"></div>
  </section>

  <!-- CHECKLIST VIEW -->
  <section id="view-checklist" class="hidden">
    <div class="draft-marker" id="draftMarker"></div>
    <p class="count">Read-only checklist of inspection hold/witness points and Appendix F
       approval-class obligations, drawn verbatim from the corpus. Draft for engineering review.</p>
    <div class="checklist-group">
      <h3 id="hwHeading">Hold &amp; witness points</h3>
      <div id="holdWitness"></div>
    </div>
    <div class="checklist-group">
      <h3 id="apHeading">Appendix F approval-class obligations</h3>
      <div id="approvals"></div>
    </div>
  </section>
</main>

<footer>
  This standalone file uses no server and no network. It loads no external fonts, scripts, or
  styles, and makes no fetch/XHR calls. The entire JEM-GEN-SPC-M-014 atom corpus is embedded in
  the page. It cannot and does not deploy to a Power Platform tenant.
</footer>

<!-- Embedded corpus: the full JEM-GEN-SPC-M-014 atom set, parsed at load time.
     Browsers block network reads of local files over file://, so the data is
     inlined here rather than loaded at runtime. -->
<script type="application/json" id="eka-atoms">__EKA_ATOMS_JSON__</script>

<script>
// =========================================================================
// Embedded grounding corpus. Parsed from the <script type="application/json">
// block above. No fetch, no XHR, no network: works over file://.
// =========================================================================
var ATOMS = JSON.parse(document.getElementById("eka-atoms").textContent);

// Constants mirrored verbatim from server.py.
var DRAFT_MARKER = "__EKA_DRAFT_MARKER__";
var NO_ANSWER_MESSAGE = "__EKA_NO_ANSWER_MESSAGE__";
var SCORE_THRESHOLD = 1;

// Modality -> plain meaning (mirrors server.py MODALITY_MEANING).
var MODALITY_MEANING = {
  "shall": "mandatory requirement",
  "should": "recommended; not mandatory",
  "may": "permitted / optional",
  "not_permitted": "explicitly disallowed",
  "prohibited": "explicitly forbidden",
  "informational": "context / definition; not an obligation on its own"
};

// Approval class -> plain meaning (Appendix F legend; server.py APPROVAL_CLASS_MEANING).
var APPROVAL_CLASS_MEANING = {
  "A": "mandatory Jemena approval",
  "B": "subject to variation at Jemena discretion",
  "C": "typically N/A unless conditions vary"
};

// Small, transparent stop-word list (mirrors server.py _STOP_WORDS).
var STOP_WORDS = {
  "the": 1, "a": 1, "an": 1, "of": 1, "for": 1, "to": 1, "and": 1, "or": 1,
  "is": 1, "are": 1, "be": 1, "do": 1, "i": 1, "how": 1, "what": 1, "which": 1,
  "when": 1, "where": 1, "in": 1, "on": 1, "at": 1, "with": 1, "my": 1, "me": 1,
  "it": 1, "that": 1, "this": 1, "requirements": 1, "requirement": 1
};

// ------- retrieval (pure, deterministic; mirrors server.py) -------

function tokenise(text) {
  // Lowercase alphanumeric tokens; drop stop-words and tokens of length <= 1.
  var lower = String(text == null ? "" : text).toLowerCase();
  var raw = lower.match(/[a-z0-9]+/g) || [];
  var out = [];
  for (var i = 0; i < raw.length; i++) {
    var t = raw[i];
    if (!STOP_WORDS[t] && t.length > 1) out.push(t);
  }
  return out;
}

function uniqueTokenSet(text) {
  var set = {};
  var toks = tokenise(text);
  for (var i = 0; i < toks.length; i++) set[toks[i]] = 1;
  return set;
}

function scoreAtom(queryTokens, atom) {
  if (!queryTokens.length) return 0;
  var clause = String(atom.clause == null ? "" : atom.clause).toLowerCase();
  var titleTokens = uniqueTokenSet(atom.clause_title);
  var textTokens = uniqueTokenSet(atom.rule_text);
  var appliesTokens = uniqueTokenSet((atom.applies_to || []).join(" "));

  var score = 0;
  for (var i = 0; i < queryTokens.length; i++) {
    var qt = queryTokens[i];
    // Direct clause-number reference, e.g. query contains "6.5.7".
    if (qt === clause || (qt.length > 1 && clause.indexOf(qt) !== -1)) score += 6;
    if (titleTokens[qt]) score += 4;
    if (appliesTokens[qt]) score += 2;
    if (textTokens[qt]) score += 1;
  }
  return score;
}

function search(query, limit, threshold) {
  if (limit == null) limit = 10;
  if (threshold == null) threshold = SCORE_THRESHOLD;
  var queryTokens = tokenise(query);
  var scored = [];
  for (var i = 0; i < ATOMS.length; i++) {
    var s = scoreAtom(queryTokens, ATOMS[i]);
    if (s >= threshold) scored.push([s, ATOMS[i]]);
  }
  // Sort by score desc, then clause asc, then rule_id asc (stable ordering).
  scored.sort(function (x, y) {
    if (x[0] !== y[0]) return y[0] - x[0];
    var cx = String(x[1].clause == null ? "" : x[1].clause);
    var cy = String(y[1].clause == null ? "" : y[1].clause);
    if (cx < cy) return -1;
    if (cx > cy) return 1;
    var rx = String(x[1].rule_id == null ? "" : x[1].rule_id);
    var ry = String(y[1].rule_id == null ? "" : y[1].rule_id);
    if (rx < ry) return -1;
    if (rx > ry) return 1;
    return 0;
  });
  var results = [];
  for (var j = 0; j < scored.length && j < limit; j++) {
    results.push(enrich(scored[j][1], scored[j][0]));
  }
  return results;
}

function enrich(atom, score) {
  var out = {};
  for (var k in atom) { if (atom.hasOwnProperty(k)) out[k] = atom[k]; }
  out._score = score;
  // Exact citation form (mirrors server.py).
  out._citation = "JEM-GEN-SPC-M-014 Clause " + atom.clause +
                  " (rule_id " + atom.rule_id + ")";
  out._modality_meaning = MODALITY_MEANING[atom.modality] || "";
  if (atom.approval_required) {
    var cls = atom.approval_class;
    var meaning = APPROVAL_CLASS_MEANING[cls];
    if (cls && meaning) {
      out._approval_line = "Appendix F approval class " + cls + " \u2014 " + meaning + ".";
    } else {
      out._approval_line = "Approval required (no Appendix F class recorded).";
    }
  } else {
    out._approval_line = null;
  }
  return out;
}

function holdWitnessAtoms() {
  var out = ATOMS.filter(function (a) { return a.hold_witness_point; });
  out.sort(function (x, y) {
    var cx = String(x.clause == null ? "" : x.clause);
    var cy = String(y.clause == null ? "" : y.clause);
    if (cx !== cy) return cx < cy ? -1 : 1;
    var rx = String(x.rule_id == null ? "" : x.rule_id);
    var ry = String(y.rule_id == null ? "" : y.rule_id);
    return rx < ry ? -1 : (rx > ry ? 1 : 0);
  });
  return out.map(function (a) { return enrich(a, 0); });
}

function approvalAtoms() {
  var out = ATOMS.filter(function (a) { return a.approval_required && a.approval_class; });
  out.sort(function (x, y) {
    var ax = String(x.approval_class == null ? "" : x.approval_class);
    var ay = String(y.approval_class == null ? "" : y.approval_class);
    if (ax !== ay) return ax < ay ? -1 : 1;
    var cx = String(x.clause == null ? "" : x.clause);
    var cy = String(y.clause == null ? "" : y.clause);
    if (cx !== cy) return cx < cy ? -1 : 1;
    var rx = String(x.rule_id == null ? "" : x.rule_id);
    var ry = String(y.rule_id == null ? "" : y.rule_id);
    return rx < ry ? -1 : (rx > ry ? 1 : 0);
  });
  return out.map(function (a) { return enrich(a, 0); });
}

// ------- rendering (mirrors server.py INDEX_HTML) -------

function esc(s) {
  // Escape markup-significant characters only; PRESERVE the en dash, degree
  // symbol, etc. (they are left intact).
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function atomCard(a) {
  var parts = [];
  parts.push('<div class="atom">');
  parts.push('<div class="rule-text">' + esc(a.rule_text) + '</div>');
  parts.push('<div class="cite">' + esc(a._citation) + '</div>');
  parts.push('<div class="meta"><span class="label">Clause title</span>' +
             esc(a.clause_title) + '</div>');
  parts.push('<div class="meta"><span class="label">Source page</span>' +
             esc(a.source_page) + '</div>');

  var mod = a.modality || "";
  var modMeaning = a._modality_meaning ? (" \u2014 " + a._modality_meaning) : "";
  parts.push('<div class="meta"><span class="label">Modality</span>' +
             '<span class="pill ' + esc(mod) + '">' + esc(mod) + '</span>' +
             esc(modMeaning) + '</div>');

  if (a._approval_line) {
    parts.push('<div class="meta"><span class="label">Approval</span>' +
               esc(a._approval_line) + '</div>');
  }
  if (a.hold_witness_point) {
    parts.push('<div class="meta"><span class="label">Inspection</span>' +
               '<span class="pill hold">hold / witness point</span></div>');
  }
  if (a.cross_references && a.cross_references.length) {
    parts.push('<div class="meta"><span class="label">Cross-references</span>' +
               esc(a.cross_references.join(", ")) + '</div>');
  }
  if (a.references && a.references.length) {
    parts.push('<div class="meta"><span class="label">Referenced standards</span>' +
               esc(a.references.join(", ")) +
               ' <span class="pill">pointer only \u2014 text not reproduced</span></div>');
  }
  parts.push('</div>');
  return parts.join("");
}

function runSearch(q) {
  var box = document.getElementById("q");
  box.value = q;
  var out = document.getElementById("results");
  var results = search(q);
  var html = '<div class="qline">You asked: <b>' + esc(q) + '</b></div>';
  if (!results.length) {
    html += '<div class="noanswer">' + esc(NO_ANSWER_MESSAGE) + '</div>';
  } else {
    html += '<p class="count">' + results.length +
            ' matching obligation(s), highest-scoring first.</p>';
    for (var i = 0; i < results.length; i++) {
      html += atomCard(results[i]);
    }
  }
  out.innerHTML = html;
}

function loadChecklist() {
  document.getElementById("draftMarker").textContent = DRAFT_MARKER;
  var hw = holdWitnessAtoms();
  var ap = approvalAtoms();
  document.getElementById("hwHeading").textContent =
    "Hold & witness points (" + hw.length + ")";
  document.getElementById("apHeading").textContent =
    "Appendix F approval-class obligations (" + ap.length + ")";
  document.getElementById("holdWitness").innerHTML = hw.length
    ? hw.map(atomCard).join("")
    : '<p class="count">None flagged in the corpus.</p>';
  document.getElementById("approvals").innerHTML = ap.length
    ? ap.map(atomCard).join("")
    : '<p class="count">None in the corpus.</p>';
}

// ------- wiring -------
document.getElementById("askBtn").addEventListener("click", function () {
  var q = document.getElementById("q").value.trim();
  if (q) runSearch(q);
});
document.getElementById("q").addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    var q = this.value.trim();
    if (q) runSearch(q);
  }
});
var exBtns = document.querySelectorAll(".examples .ex");
for (var i = 0; i < exBtns.length; i++) {
  exBtns[i].addEventListener("click", function () { runSearch(this.getAttribute("data-q")); });
}

var tabAsk = document.getElementById("tab-ask");
var tabChk = document.getElementById("tab-checklist");
var viewAsk = document.getElementById("view-ask");
var viewChk = document.getElementById("view-checklist");
var checklistLoaded = false;
function selectTab(which) {
  var askSel = which === "ask";
  tabAsk.setAttribute("aria-selected", askSel ? "true" : "false");
  tabChk.setAttribute("aria-selected", askSel ? "false" : "true");
  viewAsk.classList.toggle("hidden", !askSel);
  viewChk.classList.toggle("hidden", askSel);
  if (!askSel && !checklistLoaded) { loadChecklist(); checklistLoaded = true; }
}
tabAsk.addEventListener("click", function () { selectTab("ask"); });
tabChk.addEventListener("click", function () { selectTab("checklist"); });
</script>
</body>
</html>
"""


def _js_string(value: str) -> str:
    """Escape a Python string for safe inlining inside a double-quoted JS string.

    Uses json.dumps and strips the surrounding quotes (json string escaping is a
    valid subset of JS string escaping). Also neutralises `</` so the value can
    never prematurely close the enclosing <script> element.
    """
    encoded = json.dumps(value, ensure_ascii=False)[1:-1]
    return encoded.replace("</", "<\\/")


def render(atoms) -> str:
    """Render the standalone HTML with the corpus and constants embedded."""
    html = _TEMPLATE
    html = html.replace("__EKA_ATOMS_JSON__", _embed_json(atoms))
    html = html.replace("__EKA_DRAFT_MARKER__", _js_string(DRAFT_MARKER))
    html = html.replace("__EKA_NO_ANSWER_MESSAGE__", _js_string(NO_ANSWER_MESSAGE))
    return html


def build(corpus_path: str = CORPUS_PATH, output_path: str = OUTPUT_PATH) -> int:
    """Generate the standalone HTML file. Returns the number of embedded atoms."""
    atoms = load_atoms(corpus_path)
    html = render(atoms)
    with open(output_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    return len(atoms)


def main():
    count = build()
    print(
        "Wrote {} with {} embedded atoms (offline, single-file, no server).".format(
            os.path.relpath(OUTPUT_PATH, _REPO_ROOT), count
        )
    )


if __name__ == "__main__":
    main()
