"""Local, self-contained prototype server for the EKA `tech-query` grounded Q&A.

This is a DEMONSTRATION prototype only. It is NOT a Power Platform deployment and
has NO connection to any Microsoft 365 / Power Platform tenant. It stands in for
the designed Copilot Studio `tech-query` agent so a human can try the grounded
Q&A behaviour in a browser.

Design constraints (match the rest of prototypes/):
  * Python standard library ONLY. No third-party packages, no network, no CDNs.
  * Grounded, NOT generative. The server answers ONLY from the committed
    JEM-GEN-SPC-M-014 atom corpus. Retrieval is a simple, transparent,
    deterministic keyword score over clause / clause_title / rule_text /
    applies_to. It never invents or paraphrases clause numbers, limits, or
    acceptance criteria. When nothing matches above a threshold it returns an
    empty result set honestly.

The search function (`search`) and corpus loader (`load_atoms`) are pure and
importable without binding a port, so they can be unit-tested directly.

Run:
    cd prototypes/tech-query-app && python3 server.py
then open http://localhost:8000 in a browser.
"""

from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# --------------------------------------------------------------------------- #
# Corpus location
# --------------------------------------------------------------------------- #

# This file lives at <repo-root>/prototypes/tech-query-app/server.py.
# The corpus lives at <repo-root>/knowledge/jem-gen-spc-m-014/atoms/...
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir, os.pardir))
CORPUS_PATH = os.path.join(
    _REPO_ROOT,
    "knowledge",
    "jem-gen-spc-m-014",
    "atoms",
    "jem-gen-spc-m-014.atoms.jsonl",
)

# The exact verbatim draft marker from the corpus manifest (em dash preserved).
DRAFT_MARKER = "DRAFT — pending engineering review"

DEFAULT_PORT = 8000

# A query must score at least this to count as a hit. Keeps the no-answer path
# honest: a nonsense query returns nothing rather than the "least bad" atom.
SCORE_THRESHOLD = 1

# Modality -> plain meaning (mirrors agent-design.md section 3.1).
MODALITY_MEANING = {
    "shall": "mandatory requirement",
    "should": "recommended; not mandatory",
    "may": "permitted / optional",
    "not_permitted": "explicitly disallowed",
    "prohibited": "explicitly forbidden",
    "informational": "context / definition; not an obligation on its own",
}

# Approval class -> plain meaning (Appendix F legend, agent-design.md 3.2).
APPROVAL_CLASS_MEANING = {
    "A": "mandatory Jemena approval",
    "B": "subject to variation at Jemena discretion",
    "C": "typically N/A unless conditions vary",
}

# Very small, transparent stop-word list so common filler words do not inflate
# scores. Kept deliberately short and visible.
_STOP_WORDS = frozenset(
    {
        "the", "a", "an", "of", "for", "to", "and", "or", "is", "are", "be",
        "do", "i", "how", "what", "which", "when", "where", "in", "on", "at",
        "with", "my", "me", "it", "that", "this", "requirements", "requirement",
    }
)


# --------------------------------------------------------------------------- #
# Corpus loading
# --------------------------------------------------------------------------- #

def load_atoms(path: str = CORPUS_PATH):
    """Load the atom corpus from a JSONL file.

    One JSON object per non-blank line. Raises FileNotFoundError with a clear
    message if the corpus is missing, and ValueError if a line is malformed.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "Corpus not found at {}. Expected the JEM-GEN-SPC-M-014 atom corpus "
            "(knowledge/jem-gen-spc-m-014/atoms/jem-gen-spc-m-014.atoms.jsonl). "
            "Run this prototype from a branch that contains the corpus.".format(path)
        )
    atoms = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                atoms.append(json.loads(line))
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                raise ValueError(
                    "Malformed JSON on line {} of {}: {}".format(lineno, path, exc)
                )
    return atoms


# --------------------------------------------------------------------------- #
# Retrieval (pure, deterministic, explainable)
# --------------------------------------------------------------------------- #

def _tokenise(text: str):
    """Lowercase word tokens, stop-words removed. Deterministic."""
    tokens = re.findall(r"[a-z0-9]+", (text or "").lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]


def _score_atom(query_tokens, atom):
    """Score one atom against the query tokens.

    Transparent weighted token overlap over the fields that carry meaning for
    retrieval. Weights are chosen so clause/title matches rank above incidental
    rule_text matches, and a direct clause-number match ranks highest.
    """
    if not query_tokens:
        return 0

    clause = str(atom.get("clause") or "")
    clause_title = str(atom.get("clause_title") or "")
    rule_text = str(atom.get("rule_text") or "")
    applies_to = " ".join(atom.get("applies_to") or [])

    title_tokens = set(_tokenise(clause_title))
    text_tokens = set(_tokenise(rule_text))
    applies_tokens = set(_tokenise(applies_to))

    score = 0
    for qt in query_tokens:
        # Direct clause-number reference, e.g. query contains "6.5.7".
        if qt == clause.lower() or (len(qt) > 1 and qt in clause.lower()):
            score += 6
        if qt in title_tokens:
            score += 4
        if qt in applies_tokens:
            score += 2
        if qt in text_tokens:
            score += 1
    return score


def search(query, atoms, limit=10, threshold=SCORE_THRESHOLD):
    """Return the top matching atoms for `query`, each enriched for rendering.

    Deterministic. Returns a list of dicts, each containing the full atom plus a
    `_score` and pre-computed display helpers (modality meaning, approval line).
    Returns an empty list when nothing scores at or above `threshold` (the
    honest no-answer path). Ties break by score, then clause, then rule_id so
    ordering is stable.
    """
    query_tokens = _tokenise(query)
    scored = []
    for atom in atoms:
        s = _score_atom(query_tokens, atom)
        if s >= threshold:
            scored.append((s, atom))

    scored.sort(
        key=lambda pair: (
            -pair[0],
            str(pair[1].get("clause") or ""),
            str(pair[1].get("rule_id") or ""),
        )
    )

    results = []
    for s, atom in scored[:limit]:
        results.append(_enrich(atom, s))
    return results


def _enrich(atom, score):
    """Attach display-ready, grounded helpers without altering source fields."""
    rule_id = atom.get("rule_id")
    clause = atom.get("clause")
    modality = atom.get("modality")
    approval_required = bool(atom.get("approval_required"))
    approval_class = atom.get("approval_class")

    enriched = dict(atom)
    enriched["_score"] = score
    # Exact citation form from agent-design.md section 3.
    enriched["_citation"] = (
        "JEM-GEN-SPC-M-014 Clause {clause} (rule_id {rule_id})".format(
            clause=clause, rule_id=rule_id
        )
    )
    enriched["_modality_meaning"] = MODALITY_MEANING.get(modality, "")
    if approval_required:
        meaning = APPROVAL_CLASS_MEANING.get(approval_class)
        if approval_class and meaning:
            enriched["_approval_line"] = "Appendix F approval class {cls} — {meaning}.".format(
                cls=approval_class, meaning=meaning
            )
        else:
            enriched["_approval_line"] = "Approval required (no Appendix F class recorded)."
    else:
        enriched["_approval_line"] = None
    return enriched


def hold_witness_atoms(atoms):
    """All atoms flagged as hold or witness points (for the checklist view)."""
    out = [a for a in atoms if a.get("hold_witness_point")]
    out.sort(key=lambda a: (str(a.get("clause") or ""), str(a.get("rule_id") or "")))
    return [_enrich(a, 0) for a in out]


def approval_atoms(atoms):
    """All atoms that carry an Appendix F approval class (approval_required)."""
    out = [a for a in atoms if a.get("approval_required") and a.get("approval_class")]
    out.sort(
        key=lambda a: (
            str(a.get("approval_class") or ""),
            str(a.get("clause") or ""),
            str(a.get("rule_id") or ""),
        )
    )
    return [_enrich(a, 0) for a in out]


# --------------------------------------------------------------------------- #
# No-answer fallback text (safety-critical, matches agent-design.md section 4)
# --------------------------------------------------------------------------- #

NO_ANSWER_MESSAGE = (
    "The JEM-GEN-SPC-M-014 corpus does not contain a governing obligation that "
    "matches this question as asked. This prototype will not guess, infer, or "
    "fabricate a clause number, limit, or acceptance criterion. Please rephrase "
    "using the specification's terms, or defer to the responsible engineer and "
    "the authoritative JEM-GEN-SPC-M-014 document."
)


# --------------------------------------------------------------------------- #
# HTTP server
# --------------------------------------------------------------------------- #

class _Handler(BaseHTTPRequestHandler):
    # Set by make_server(); the loaded corpus shared across requests.
    atoms = []

    server_version = "EKA-tech-query-prototype/0.1"

    def log_message(self, fmt, *args):  # keep the console readable
        return

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path

        if route in ("/", "/index.html"):
            self._send_html(INDEX_HTML)
            return

        if route == "/api/search":
            params = parse_qs(parsed.query)
            query = (params.get("q", [""])[0]).strip()
            results = search(query, self.atoms) if query else []
            self._send_json(
                {
                    "query": query,
                    "count": len(results),
                    "results": results,
                    "no_answer": (len(results) == 0),
                    "no_answer_message": NO_ANSWER_MESSAGE,
                    "draft_marker": DRAFT_MARKER,
                }
            )
            return

        if route == "/api/checklist":
            self._send_json(
                {
                    "hold_witness": hold_witness_atoms(self.atoms),
                    "approvals": approval_atoms(self.atoms),
                    "draft_marker": DRAFT_MARKER,
                }
            )
            return

        self._send_json({"error": "not found", "path": route}, status=404)


def make_server(port=DEFAULT_PORT, atoms=None):
    """Create (but do not serve) the HTTP server. Loads the corpus if needed."""
    if atoms is None:
        atoms = load_atoms()
    _Handler.atoms = atoms
    return ThreadingHTTPServer(("127.0.0.1", port), _Handler), atoms


def main():
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    try:
        httpd, atoms = make_server(port)
    except FileNotFoundError as exc:
        print("ERROR: {}".format(exc))
        raise SystemExit(1)
    print("EKA tech-query prototype (LOCAL DEMO — not a Power Platform tenant)")
    print("Loaded {} atoms from the JEM-GEN-SPC-M-014 corpus.".format(len(atoms)))
    print("Open http://localhost:{} in your browser. Press Ctrl+C to stop.".format(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        httpd.shutdown()


# --------------------------------------------------------------------------- #
# Static UI (single self-contained page; no external assets)
# --------------------------------------------------------------------------- #
# NOTE: INDEX_HTML is defined after main() purely for readability. It is a plain
# string with vanilla HTML/CSS/JS. No CDN, no external fonts, no build step.

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>EKA tech-query prototype — JEM-GEN-SPC-M-014</title>
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
  <strong>LOCAL PROTOTYPE — demonstration only.</strong>
  Not connected to any Power Platform / Microsoft 365 tenant. Answers are grounded on the
  committed JEM-GEN-SPC-M-014 atom corpus and are DRAFTS for qualified-engineer review.
</div>

<header>
  <h1>Engineering Knowledge Assistant — tech-query (prototype)</h1>
  <p>Grounded Q&amp;A over <b>JEM-GEN-SPC-M-014</b> "Piping and Mechanical Equipment –
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
  This prototype uses the Python standard library only, serves from localhost, and loads no
  external fonts, scripts, or styles. It cannot and does not deploy to a Power Platform tenant.
</footer>

<script>
// ------- tiny helpers (no framework) -------
function esc(s) {
  // Escape to prevent broken markup / injection, but PRESERVE characters such
  // as the en dash and degree symbol (they are left intact; only markup-significant
  // characters are entity-encoded).
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
  var modMeaning = a._modality_meaning ? (" — " + a._modality_meaning) : "";
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
               ' <span class="pill">pointer only — text not reproduced</span></div>');
  }
  parts.push('</div>');
  return parts.join("");
}

function runSearch(q) {
  var box = document.getElementById("q");
  box.value = q;
  var out = document.getElementById("results");
  out.innerHTML = '<p class="count">Searching…</p>';
  fetch("/api/search?q=" + encodeURIComponent(q))
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var html = '<div class="qline">You asked: <b>' + esc(data.query) + '</b></div>';
      if (data.no_answer) {
        html += '<div class="noanswer">' + esc(data.no_answer_message) + '</div>';
      } else {
        html += '<p class="count">' + data.count +
                ' matching obligation(s), highest-scoring first.</p>';
        for (var i = 0; i < data.results.length; i++) {
          html += atomCard(data.results[i]);
        }
      }
      out.innerHTML = html;
    })
    .catch(function (e) {
      out.innerHTML = '<div class="noanswer">Request failed: ' + esc(e) + '</div>';
    });
}

function loadChecklist() {
  fetch("/api/checklist")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      document.getElementById("draftMarker").textContent = data.draft_marker;
      var hw = document.getElementById("holdWitness");
      var ap = document.getElementById("approvals");
      document.getElementById("hwHeading").textContent =
        "Hold & witness points (" + data.hold_witness.length + ")";
      document.getElementById("apHeading").textContent =
        "Appendix F approval-class obligations (" + data.approvals.length + ")";
      hw.innerHTML = data.hold_witness.length
        ? data.hold_witness.map(atomCard).join("")
        : '<p class="count">None flagged in the corpus.</p>';
      ap.innerHTML = data.approvals.length
        ? data.approvals.map(atomCard).join("")
        : '<p class="count">None in the corpus.</p>';
    });
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


if __name__ == "__main__":
    main()
