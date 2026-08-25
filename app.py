# toolcontract_figma_style.py
# Figma-inspired bright gallery UI for ToolContract
#
# Put this file at:
#   C:\Users\user\ToolContract\app.py
#
# Run:
#   python -m streamlit run app.py

from __future__ import annotations

import html
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st
from dotenv import load_dotenv


# ============================================================
# Project imports
# ============================================================

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

load_dotenv(ROOT / ".env")

from toolcontract.analyzer import analyze_tools
from toolcontract.behavior.runner import BehaviorTestRunner
from toolcontract.behavior.evaluator import BehaviorEvaluator


# ============================================================
# Page setup
# ============================================================

st.set_page_config(
    page_title="ToolContract",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Figma-inspired light visual system
# ============================================================

st.markdown(
    """
<style>
:root {
    --bg: #ffffff;
    --ink: #171717;
    --muted: #6f6f75;
    --line: #e7e7ea;
    --soft: #f7f7f8;
    --purple: #5b4df7;
    --blue: #4f7df3;
    --mint: #67dcc2;
    --pink: #f49ac2;
    --yellow: #f6d87a;
    --red: #e75b6f;
    --green: #1f9d74;
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
                 "Segoe UI", sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--ink);
}

.block-container {
    max-width: 1380px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

#MainMenu, footer, [data-testid="stToolbar"] {
    visibility: hidden;
}
[data-testid="stHeader"] {
    height: 0;
    background: transparent;
}

/* ---------- top nav ---------- */
.tc-nav {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:1rem;
    padding:.25rem 0 1.25rem;
    border-bottom:1px solid var(--line);
}
.tc-brandwrap {
    display:flex;
    align-items:center;
    gap:.72rem;
}
.tc-logo {
    width:35px;
    height:35px;
    border-radius:11px;
    background:
        radial-gradient(circle at 30% 30%, #fff 0 9%, transparent 10%),
        linear-gradient(135deg,#695cff,#8d7bff 45%,#60dfc4);
    box-shadow:0 8px 25px rgba(91,77,247,.20);
    position:relative;
}
.tc-logo:after {
    content:"";
    position:absolute;
    inset:9px;
    border:2px solid #fff;
    border-radius:5px;
}
.tc-brand {
    font-weight:780;
    letter-spacing:-.03em;
    font-size:1.06rem;
}
.tc-alpha {
    font-size:.68rem;
    color:#777;
    background:#f3f3f5;
    border:1px solid var(--line);
    border-radius:999px;
    padding:.18rem .42rem;
}
.tc-navlinks {
    display:flex;
    gap:1.25rem;
    color:#555;
    font-size:.86rem;
}

/* ---------- hero ---------- */
.tc-hero {
    text-align:center;
    padding:4.4rem 0 2.5rem;
}
.tc-kicker {
    display:inline-flex;
    align-items:center;
    gap:.45rem;
    padding:.38rem .72rem;
    border-radius:999px;
    background:#f4f3ff;
    color:#5b4df7;
    font-size:.77rem;
    font-weight:700;
    margin-bottom:1.2rem;
}
.tc-spark {
    width:7px;height:7px;border-radius:50%;
    background:#5b4df7;
}
.tc-hero h1 {
    max-width:960px;
    margin:0 auto;
    font-size:clamp(3.15rem,6.5vw,6rem);
    line-height:.96;
    letter-spacing:-.067em;
    font-weight:800;
    color:var(--ink);
}
.tc-hero h1 span {
    background:linear-gradient(90deg,#5b4df7 0%,#7e73ff 48%,#38bfa3 100%);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.tc-hero p {
    max-width:760px;
    margin:1.35rem auto 0;
    font-size:1.04rem;
    line-height:1.72;
    color:var(--muted);
}

/* ---------- gallery cards ---------- */
.tc-gallery {
    margin-top:1.15rem;
}
.tc-color-card {
    border:1px solid rgba(0,0,0,.05);
    border-radius:20px;
    min-height:220px;
    padding:1.25rem;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    overflow:hidden;
    position:relative;
}
.tc-color-card:after {
    content:"";
    position:absolute;
    width:150px;height:150px;
    border-radius:50%;
    background:rgba(255,255,255,.34);
    top:-42px;right:-42px;
}
.tc-purple { background:linear-gradient(135deg,#c9c2ff,#8f80ff); }
.tc-mint   { background:linear-gradient(135deg,#baf3e4,#73dbc0); }
.tc-pink   { background:linear-gradient(135deg,#ffd0e2,#f397bd); }
.tc-yellow { background:linear-gradient(135deg,#fff0b6,#f6d06c); }

.tc-card-index {
    font-size:.72rem;
    font-weight:750;
    letter-spacing:.12em;
    text-transform:uppercase;
    color:rgba(23,23,23,.60);
}
.tc-color-title {
    font-size:1.55rem;
    line-height:1.08;
    letter-spacing:-.035em;
    font-weight:780;
    max-width:250px;
}
.tc-color-body {
    color:rgba(23,23,23,.66);
    font-size:.86rem;
    line-height:1.55;
    max-width:280px;
}

/* ---------- upload / action panels ---------- */
.tc-panel {
    border:1px solid var(--line);
    border-radius:18px;
    background:#fff;
    padding:1.2rem;
}
.tc-panel-soft {
    border:1px solid var(--line);
    border-radius:18px;
    background:#fafafa;
    padding:1.15rem;
}
.tc-label {
    color:#8b8b91;
    font-size:.72rem;
    font-weight:750;
    text-transform:uppercase;
    letter-spacing:.11em;
    margin-bottom:.45rem;
}
.tc-title {
    color:var(--ink);
    font-size:1.1rem;
    font-weight:740;
    letter-spacing:-.025em;
}
.tc-body {
    color:var(--muted);
    line-height:1.58;
    font-size:.88rem;
    margin-top:.4rem;
}

/* ---------- dashboard ---------- */
.tc-filebar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:1rem;
    border:1px solid var(--line);
    border-radius:14px;
    padding:.9rem 1rem;
    margin:.75rem 0 1.1rem;
    background:#fff;
}
.tc-fileleft {
    display:flex;align-items:center;gap:.75rem;
}
.tc-fileicon {
    width:31px;height:31px;border-radius:9px;
    display:grid;place-items:center;
    background:#f2f0ff;
    color:#5b4df7;
    font-weight:800;
}
.tc-filename {
    font-weight:720;
}
.tc-meta {
    color:#8b8b91;
    font-size:.79rem;
}

/* KPI cards */
.tc-kpi {
    border:1px solid var(--line);
    border-radius:17px;
    min-height:132px;
    padding:1rem 1.05rem;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    background:#fff;
}
.tc-kpi-purple { background:#f3f1ff; }
.tc-kpi-mint   { background:#eefbf7; }
.tc-kpi-pink   { background:#fff1f6; }
.tc-kpi-yellow { background:#fff9e6; }

.tc-kpilabel {
    color:#74747a;
    font-size:.7rem;
    font-weight:760;
    text-transform:uppercase;
    letter-spacing:.1em;
}
.tc-kpivalue {
    font-size:2.35rem;
    font-weight:790;
    letter-spacing:-.06em;
    line-height:1;
    margin-top:.65rem;
}
.tc-kpisub {
    color:#777;
    font-size:.78rem;
    margin-top:.35rem;
}

/* sections */
.tc-section {
    margin:1rem 0 .75rem;
}
.tc-section h3 {
    margin:0;
    font-size:1.25rem;
    letter-spacing:-.03em;
    font-weight:760;
}
.tc-section p {
    margin:.2rem 0 0;
    color:#777;
    font-size:.85rem;
}

/* issues */
.tc-issue {
    border:1px solid var(--line);
    border-radius:15px;
    background:#fff;
    padding:1rem 1.05rem;
    margin-bottom:.65rem;
}
.tc-issuetop {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:.8rem;
    margin-bottom:.52rem;
}
.tc-rule {
    display:inline-flex;
    border-radius:8px;
    background:#fff5d9;
    color:#8e6500;
    border:1px solid #f2dfaa;
    padding:.22rem .46rem;
    font-size:.73rem;
    font-weight:800;
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
.tc-tool {
    color:#666;
    font-size:.79rem;
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
.tc-msg {
    color:#303038;
    font-size:.89rem;
    line-height:1.55;
}

/* behavior */
.tc-run {
    border:1px solid var(--line);
    border-radius:14px;
    background:#fff;
    padding:.8rem .9rem;
    margin-bottom:.55rem;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:1rem;
}
.tc-runleft {
    display:flex;align-items:center;gap:.75rem;
}
.tc-num {
    width:31px;height:31px;border-radius:9px;
    display:grid;place-items:center;
    background:#f5f5f6;
    color:#777;
    font-size:.74rem;
    font-weight:760;
}
.tc-runtool {
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    font-size:.84rem;
    font-weight:700;
}
.tc-args {
    color:#8b8b91;
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    font-size:.74rem;
    margin-top:.15rem;
}
.tc-pill {
    display:inline-flex;
    border-radius:999px;
    padding:.27rem .55rem;
    font-size:.72rem;
    font-weight:820;
}
.tc-pass { background:#e8f8f2;color:#147254; }
.tc-fail { background:#fff0f2;color:#b83f51; }

/* selection distribution */
.tc-conf {
    border:1px solid var(--line);
    border-radius:16px;
    background:#fff;
    padding:1rem;
}
.tc-confrow {
    display:grid;
    grid-template-columns:1fr 125px 48px;
    align-items:center;
    gap:.7rem;
    margin:.65rem 0;
}
.tc-confname {
    color:#333;
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    font-size:.79rem;
}
.tc-track {
    height:8px;
    background:#f0f0f1;
    border-radius:999px;
    overflow:hidden;
}
.tc-fill {
    height:100%;
    border-radius:999px;
    background:linear-gradient(90deg,#5b4df7,#67dcc2);
}
.tc-count {
    color:#7d7d82;
    font-size:.77rem;
    text-align:right;
}

/* compare */
.tc-compare {
    border:1px solid var(--line);
    border-radius:18px;
    overflow:hidden;
    background:#fff;
}
.tc-comparegrid {
    display:grid;
    grid-template-columns:1fr 80px 1fr;
}
.tc-side {
    padding:1.35rem 1.4rem;
}
.tc-before { background:#fff1f6; }
.tc-after  { background:#effbf7; }
.tc-mid {
    display:grid;place-items:center;
    border-left:1px solid var(--line);
    border-right:1px solid var(--line);
    font-size:1.55rem;
    color:#777;
    background:#fafafa;
}
.tc-big {
    font-size:3rem;
    font-weight:800;
    letter-spacing:-.06em;
    line-height:1;
    margin:.7rem 0 .25rem;
}
.tc-delta {
    color:#13795a;
    font-size:.82rem;
    font-weight:730;
    margin-top:.52rem;
}

/* Streamlit controls */
.stButton > button {
    min-height:44px;
    border-radius:11px;
    font-weight:720;
    border:1px solid #d9d9dc;
    background:#fff;
    color:#1f1f22;
}
.stButton > button:hover {
    border-color:#5b4df7;
    color:#5b4df7;
}
.stButton > button[kind="primary"] {
    background:#171717;
    color:#fff;
    border-color:#171717;
}
div[data-testid="stFileUploaderDropzone"] {
    border:1px dashed #d8d8dc;
    background:#fafafa;
    border-radius:14px;
}
.stTextInput input,
.stTextArea textarea,
div[data-baseweb="select"] > div {
    background:#fff !important;
    border-color:#dedee2 !important;
    border-radius:10px !important;
    color:#171717 !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap:.25rem;
    border-bottom:1px solid var(--line);
}
.stTabs [data-baseweb="tab"] {
    color:#777;
    padding:.72rem .85rem;
}
.stTabs [aria-selected="true"] {
    color:#171717 !important;
}
.stProgress > div > div > div {
    background:linear-gradient(90deg,#5b4df7,#67dcc2);
}

@media(max-width:900px) {
    .tc-navlinks { display:none; }
    .tc-comparegrid { grid-template-columns:1fr; }
    .tc-mid {
        min-height:48px;
        border-left:0;border-right:0;
        border-top:1px solid var(--line);
        border-bottom:1px solid var(--line);
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Demo contracts
# ============================================================

BAD_TOOLS = [
    {
        "name": "order_tool_a",
        "description": "주문 관련 정보를 처리합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "order_tool_b",
        "description": "주문 관련 요청을 처리합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"],
        },
    },
]

GOOD_TOOLS = [
    {
        "name": "order_tool_a",
        "description": "주문 ID를 사용하여 기존 주문의 현재 상태와 상세 정보를 조회합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "조회할 주문의 고유 ID",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "order_tool_b",
        "description": "주문 ID를 사용하여 진행 중인 주문을 취소합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "취소할 주문의 고유 ID",
                }
            },
            "required": ["order_id"],
        },
    },
]


# ============================================================
# Helpers
# ============================================================

def esc(v: Any) -> str:
    return html.escape(str(v), quote=True)


def normalize_tools(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, dict):
        data = data.get("tools", [data])

    if not isinstance(data, list):
        raise ValueError("JSON 최상위 값은 Tool 목록(list)이어야 합니다.")

    out = []

    for i, tool in enumerate(data):
        if not isinstance(tool, dict):
            raise ValueError(f"{i+1}번째 Tool이 object가 아닙니다.")

        if tool.get("type") == "function" and isinstance(tool.get("function"), dict):
            fn = tool["function"]
            out.append({
                "name": fn.get("name", f"unknown_{i+1}"),
                "description": fn.get("description", ""),
                "inputSchema": fn.get(
                    "parameters",
                    {"type": "object", "properties": {}},
                ),
            })
        else:
            out.append(tool)

    return out


def read_upload(uploaded) -> List[Dict[str, Any]]:
    return normalize_tools(
        json.loads(uploaded.getvalue().decode("utf-8-sig"))
    )


def parse_args(text: str) -> Dict[str, str]:
    text = (text or "").strip()
    if not text:
        return {}

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return {str(k): str(v) for k, v in parsed.items()}
    except json.JSONDecodeError:
        pass

    result = {}
    for item in text.split(","):
        if "=" not in item:
            raise ValueError("Expected Args는 order_id=123 형식으로 입력하세요.")
        k, v = item.split("=", 1)
        result[k.strip()] = v.strip()

    return result


def issue_rule(issue: Any) -> str:
    if isinstance(issue, dict):
        return str(issue.get("rule", "ISSUE"))
    match = re.search(r"(TC\d{3})", str(issue))
    return match.group(1) if match else "ISSUE"


def issue_tool(issue: Any) -> str:
    if isinstance(issue, dict):
        return str(issue.get("tool", ""))

    for b in re.findall(r"\[([^\]]+)\]", str(issue)):
        if not re.fullmatch(r"TC\d{3}", b):
            return b
    return ""


def issue_msg(issue: Any) -> str:
    if isinstance(issue, dict):
        return str(issue.get("message", issue))
    return str(issue)


def tool_names(tools: List[Dict[str, Any]]) -> List[str]:
    return [str(t.get("name", "unknown")) for t in tools]


def run_behavior(
    tools: List[Dict[str, Any]],
    prompt: str,
    expected_tool: str,
    expected_args: Dict[str, Any],
    repeats: int,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    runner = BehaviorTestRunner()
    evaluator = BehaviorEvaluator()

    results = runner.run_repeated_test(
        prompt=prompt,
        tools=tools,
        num_repeats=repeats,
    )

    metrics = evaluator.calculate_metrics(
        results,
        expected_tool,
        expected_args,
    )

    return results, metrics


def run_ok(
    result: Dict[str, Any],
    expected_tool: str,
    expected_args: Dict[str, Any],
) -> bool:
    evaluator = BehaviorEvaluator()

    tool_ok = evaluator.check_tool_selection(
        result.get("selected_tool"),
        expected_tool,
    )

    args_ok = True
    if expected_args:
        args_ok = evaluator.check_arguments(
            result.get("arguments") or {},
            expected_args,
        )

    return tool_ok and args_ok


def kpi(label: str, value: str, sub: str, cls: str):
    st.markdown(
        f"""
        <div class="tc-kpi {cls}">
            <div class="tc-kpilabel">{esc(label)}</div>
            <div>
                <div class="tc-kpivalue">{esc(value)}</div>
                <div class="tc-kpisub">{esc(sub)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def issue_card(issue: Any):
    st.markdown(
        f"""
        <div class="tc-issue">
            <div class="tc-issuetop">
                <span class="tc-rule">{esc(issue_rule(issue))}</span>
                <span class="tc-tool">{esc(issue_tool(issue))}</span>
            </div>
            <div class="tc-msg">{esc(issue_msg(issue))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def confusion(results: List[Dict[str, Any]], expected_tool: str):
    dist = Counter(str(r.get("selected_tool") or "No tool") for r in results)
    if not dist:
        return

    peak = max(dist.values())
    rows = []

    for tool, count in dist.most_common():
        width = (count / peak) * 100 if peak else 0
        rows.append(
            f"""
            <div class="tc-confrow">
                <div class="tc-confname">{esc(tool)}</div>
                <div class="tc-track">
                    <div class="tc-fill" style="width:{width:.1f}%"></div>
                </div>
                <div class="tc-count">{count}</div>
            </div>
            """
        )

    st.markdown(
        f"""
        <div class="tc-conf">
            <div class="tc-label">Selection distribution</div>
            <div class="tc-title">Expected · {esc(expected_tool)}</div>
            <div style="height:.3rem"></div>
            {''.join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# State
# ============================================================

initial_state = {
    "tools": None,
    "source": None,
    "static_issues": None,
    "behavior_results": None,
    "behavior_metrics": None,
    "expected_tool": None,
    "expected_args": {},
}

for key, value in initial_state.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# Navigation
# ============================================================

st.markdown(
    """
    <div class="tc-nav">
        <div class="tc-brandwrap">
            <div class="tc-logo"></div>
            <div class="tc-brand">ToolContract</div>
            <div class="tc-alpha">alpha</div>
        </div>
        <div class="tc-navlinks">
            <span>Analyze</span>
            <span>Behavior</span>
            <span>Compare</span>
            <span>GitHub ↗</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


tools = st.session_state.tools


# ============================================================
# Landing
# ============================================================

if tools is None:
    st.markdown(
        """
        <div class="tc-hero">
            <div class="tc-kicker">
                <span class="tc-spark"></span>
                AI Agent Tool Quality Testing
            </div>
            <h1>
                Better tool definitions.<br>
                <span>Better agent decisions.</span>
            </h1>
            <p>
                Inspect ambiguous tool contracts, test them against a real LLM,
                and measure whether clearer definitions improve actual tool selection.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # colorful feature gallery
    g1, g2, g3 = st.columns(3, gap="large")

    with g1:
        st.markdown(
            """
            <div class="tc-color-card tc-purple">
                <div class="tc-card-index">01 · Static Analysis</div>
                <div>
                    <div class="tc-color-title">Find ambiguous contracts.</div>
                    <div class="tc-color-body">
                        Detect vague descriptions, missing parameter docs,
                        schema issues and similar tools.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with g2:
        st.markdown(
            """
            <div class="tc-color-card tc-mint">
                <div class="tc-card-index">02 · Behavior Test</div>
                <div>
                    <div class="tc-color-title">Ask the real model.</div>
                    <div class="tc-color-body">
                        Repeat tool-selection calls and see where the model
                        chooses the wrong tool.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with g3:
        st.markdown(
            """
            <div class="tc-color-card tc-pink">
                <div class="tc-card-index">03 · Compare</div>
                <div>
                    <div class="tc-color-title">Measure the improvement.</div>
                    <div class="tc-color-body">
                        Compare risky and improved definitions side by side
                        with actual behavior accuracy.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.1,.9], gap="large")

    with left:
        st.markdown(
            """
            <div class="tc-panel">
                <div class="tc-label">Upload your contract</div>
                <div class="tc-title">Start with your own tools.json</div>
                <div class="tc-body">
                    MCP <code>inputSchema</code> and OpenAI function
                    <code>parameters</code> formats are supported.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Tool JSON",
            type=["json"],
            label_visibility="collapsed",
        )

        if uploaded is not None:
            if st.button(
                "Analyze uploaded contract",
                type="primary",
                use_container_width=True,
            ):
                try:
                    st.session_state.tools = read_upload(uploaded)
                    st.session_state.source = uploaded.name
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    with right:
        st.markdown(
            """
            <div class="tc-panel-soft">
                <div class="tc-label">Try the interactive demo</div>
                <div class="tc-title">No setup required</div>
                <div class="tc-body">
                    Load an intentionally confusing contract, then compare it
                    with a clearer version.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        d1, d2 = st.columns(2)

        with d1:
            if st.button("Risky demo", use_container_width=True):
                st.session_state.tools = BAD_TOOLS
                st.session_state.source = "risky-order-tools.json"
                st.rerun()

        with d2:
            if st.button("Improved demo", use_container_width=True):
                st.session_state.tools = GOOD_TOOLS
                st.session_state.source = "improved-order-tools.json"
                st.rerun()


# ============================================================
# Dashboard
# ============================================================

else:
    source = st.session_state.source or "tool-definition.json"

    st.markdown(
        f"""
        <div class="tc-filebar">
            <div class="tc-fileleft">
                <div class="tc-fileicon">{{ }}</div>
                <div>
                    <div class="tc-filename">{esc(source)}</div>
                    <div class="tc-meta">{len(tools)} tools loaded</div>
                </div>
            </div>
            <div class="tc-meta">Ready to test</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back, _ = st.columns([.18,.82])

    with back:
        if st.button("← New contract", use_container_width=True):
            for key, value in initial_state.items():
                st.session_state[key] = value
            st.rerun()

    issues = st.session_state.static_issues
    metrics = st.session_state.behavior_metrics

    issue_text = "—" if issues is None else str(len(issues))
    behavior_text = "—" if metrics is None else f"{float(metrics.get('accuracy',0)):.0f}%"

    if issues is None and metrics is None:
        gate = "Not run"
    elif issues is not None and len(issues) == 0 and (
        metrics is None or metrics.get("status") == "PASS"
    ):
        gate = "Pass"
    else:
        gate = "Review"

    a,b,c,d = st.columns(4, gap="large")
    with a: kpi("Tools", str(len(tools)), "Loaded definitions", "tc-kpi-purple")
    with b: kpi("Static issues", issue_text, "Contract findings", "tc-kpi-yellow")
    with c: kpi("Behavior", behavior_text, "Selection accuracy", "tc-kpi-mint")
    with d: kpi("Quality gate", gate, "Pre-deploy status", "tc-kpi-pink")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    overview_tab, static_tab, behavior_tab, compare_tab = st.tabs(
        ["Overview", "Static Analysis", "Behavior Test", "Compare"]
    )

    with overview_tab:
        left, right = st.columns([1.05,.95], gap="large")

        with left:
            st.markdown(
                """
                <div class="tc-section">
                    <h3>Tool inventory</h3>
                    <p>Review the metadata the model can actually see.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for tool in tools:
                schema = tool.get("inputSchema", {})
                props = schema.get("properties", {}) if isinstance(schema, dict) else {}

                with st.expander(
                    f"{tool.get('name','unknown')} · {len(props)} parameter(s)"
                ):
                    st.caption(tool.get("description","") or "No description")
                    st.json(schema)

        with right:
            st.markdown(
                """
                <div class="tc-section">
                    <h3>Quick scan</h3>
                    <p>Static checks require no model call.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="tc-panel-soft">
                    <div class="tc-label">Recommended first step</div>
                    <div class="tc-title">Inspect the contract before behavior testing.</div>
                    <div class="tc-body">
                        Find obvious quality problems first, then spend LLM calls
                        on the cases that actually need behavioral verification.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Run static analysis",
                use_container_width=True,
                type="primary",
                key="overview_static",
            ):
                st.session_state.static_issues = analyze_tools(tools)
                st.rerun()

    with static_tab:
        st.markdown(
            """
            <div class="tc-section">
                <h3>Static contract analysis</h3>
                <p>Check clarity, parameter documentation, schema shape and tool overlap.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Analyze contract",
            use_container_width=True,
            type="primary",
            key="static_analyze",
        ):
            st.session_state.static_issues = analyze_tools(tools)
            st.rerun()

        issues = st.session_state.static_issues

        if issues is None:
            st.info("Run the analyzer to inspect this contract.")
        elif not issues:
            st.success("PASS · No static issues found.")
        else:
            counts = Counter(issue_rule(i) for i in issues)

            x1,x2,x3 = st.columns(3, gap="large")
            with x1: kpi("Findings", str(len(issues)), "Total issues", "tc-kpi-yellow")
            with x2: kpi("Rule types", str(len(counts)), "Triggered families", "tc-kpi-purple")
            with x3:
                top = counts.most_common(1)[0][0] if counts else "—"
                kpi("Top rule", top, "Most frequent", "tc-kpi-pink")

            st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

            for issue in issues:
                issue_card(issue)

    with behavior_tab:
        st.markdown(
            """
            <div class="tc-section">
                <h3>LLM behavior verification</h3>
                <p>Repeat the same request and measure actual tool-selection stability.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        n = tool_names(tools)
        default_tool = "order_tool_b" if "order_tool_b" in n else n[0]

        prompt = st.text_area(
            "Prompt",
            value="주문번호 123번을 취소해줘.",
            height=90,
        )

        b1,b2,b3 = st.columns([1,1.15,.55], gap="large")

        with b1:
            expected_tool = st.selectbox(
                "Expected Tool",
                n,
                index=n.index(default_tool),
            )
        with b2:
            expected_args_text = st.text_input(
                "Expected Args",
                value="order_id=123",
            )
        with b3:
            repeats = st.number_input(
                "Repeats",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
            )

        if st.button(
            "Run behavior test",
            use_container_width=True,
            type="primary",
        ):
            if not os.getenv("GROQ_API_KEY"):
                st.error("GROQ_API_KEY가 없습니다. .env를 확인하세요.")
            else:
                try:
                    expected_args = parse_args(expected_args_text)

                    with st.spinner("Running the model..."):
                        results, behavior_metrics = run_behavior(
                            tools,
                            prompt,
                            expected_tool,
                            expected_args,
                            int(repeats),
                        )

                    st.session_state.behavior_results = results
                    st.session_state.behavior_metrics = behavior_metrics
                    st.session_state.expected_tool = expected_tool
                    st.session_state.expected_args = expected_args
                    st.rerun()

                except Exception as exc:
                    st.error(str(exc))

        results = st.session_state.behavior_results
        metrics = st.session_state.behavior_metrics

        if results is not None and metrics is not None:
            total = int(metrics.get("total_runs", len(results)))
            passed = int(metrics.get("pass_count", 0))
            accuracy = float(metrics.get("accuracy", 0))
            status = str(metrics.get("status", "FAIL"))

            y1,y2,y3 = st.columns(3, gap="large")
            with y1: kpi("Accuracy", f"{accuracy:.0f}%", "Correct runs", "tc-kpi-mint")
            with y2: kpi("Passed", f"{passed}/{total}", "Successful calls", "tc-kpi-purple")
            with y3: kpi("Status", status, "Behavior gate", "tc-kpi-pink")

            st.progress(max(0.0, min(1.0, accuracy/100.0)))

            left_runs,right_conf = st.columns([1.05,.95], gap="large")

            with left_runs:
                st.markdown("#### Individual runs")

                for idx, result in enumerate(results, start=1):
                    ok = run_ok(
                        result,
                        st.session_state.expected_tool,
                        st.session_state.expected_args,
                    )

                    badge = (
                        '<span class="tc-pill tc-pass">✓ PASS</span>'
                        if ok
                        else '<span class="tc-pill tc-fail">× WRONG</span>'
                    )

                    st.markdown(
                        f"""
                        <div class="tc-run">
                            <div class="tc-runleft">
                                <div class="tc-num">{idx:02d}</div>
                                <div>
                                    <div class="tc-runtool">{esc(result.get("selected_tool"))}</div>
                                    <div class="tc-args">
                                        {esc(json.dumps(result.get("arguments"),ensure_ascii=False))}
                                    </div>
                                </div>
                            </div>
                            <div>{badge}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with right_conf:
                st.markdown("#### Tool confusion")
                confusion(results, st.session_state.expected_tool)

    with compare_tab:
        st.markdown(
            """
            <div class="tc-section">
                <h3>Contract improvement</h3>
                <p>Compare an ambiguous definition with a clearer version.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        before_issues = analyze_tools(BAD_TOOLS)
        after_issues = analyze_tools(GOOD_TOOLS)

        st.markdown(
            f"""
            <div class="tc-compare">
                <div class="tc-comparegrid">
                    <div class="tc-side tc-before">
                        <div class="tc-label">Before · risky contract</div>
                        <div class="tc-big">{len(before_issues)}</div>
                        <div class="tc-body">Static issues</div>
                    </div>
                    <div class="tc-mid">→</div>
                    <div class="tc-side tc-after">
                        <div class="tc-label">After · improved contract</div>
                        <div class="tc-big">{len(after_issues)}</div>
                        <div class="tc-body">Static issues</div>
                        <div class="tc-delta">
                            {max(0,len(before_issues)-len(after_issues))} issue(s) removed
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        l,r = st.columns(2, gap="large")

        with l:
            st.markdown(
                """
                <div class="tc-panel" style="background:#fff1f6;">
                    <div class="tc-label">Before · order_tool_b</div>
                    <div class="tc-title">“주문 관련 요청을 처리합니다.”</div>
                    <div class="tc-body">
                        Ambiguous intent and missing parameter description.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with r:
            st.markdown(
                """
                <div class="tc-panel" style="background:#effbf7;">
                    <div class="tc-label">After · order_tool_b</div>
                    <div class="tc-title">
                        “주문 ID를 사용하여 진행 중인 주문을 취소합니다.”
                    </div>
                    <div class="tc-body">
                        Clear intent, action boundary and documented argument.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("#### Live behavior comparison")
        st.caption("Runs both contracts against the real model.")

        cp = st.text_input("Compare prompt", "주문번호 123번을 취소해줘.")
        ce = st.text_input("Compare expected tool", "order_tool_b")
        ca = st.text_input("Compare expected args", "order_id=123")
        cr = st.slider("Repeats per contract", 1, 10, 5)

        if st.button(
            "Run before / after",
            use_container_width=True,
            key="compare_button",
        ):
            if not os.getenv("GROQ_API_KEY"):
                st.error("GROQ_API_KEY가 없습니다.")
            else:
                try:
                    ea = parse_args(ca)

                    with st.spinner("Comparing both contracts..."):
                        _, bm = run_behavior(BAD_TOOLS, cp, ce, ea, cr)
                        _, am = run_behavior(GOOD_TOOLS, cp, ce, ea, cr)

                    before = float(bm.get("accuracy", 0))
                    after = float(am.get("accuracy", 0))
                    delta = after - before

                    st.markdown(
                        f"""
                        <div class="tc-compare">
                            <div class="tc-comparegrid">
                                <div class="tc-side tc-before">
                                    <div class="tc-label">Before</div>
                                    <div class="tc-big">{before:.0f}%</div>
                                    <div class="tc-body">Behavior accuracy</div>
                                </div>
                                <div class="tc-mid">→</div>
                                <div class="tc-side tc-after">
                                    <div class="tc-label">After</div>
                                    <div class="tc-big">{after:.0f}%</div>
                                    <div class="tc-body">Behavior accuracy</div>
                                    <div class="tc-delta">
                                        {delta:+.0f} percentage points
                                    </div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                except Exception as exc:
                    st.error(str(exc))