import streamlit as st
from engine import profile, recommend_sort, recommend_search
from c_engine import insertion_sort as c_insertion_sort
st.set_page_config(
    page_title="Algorithm Recommender",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- State ----------
for k, v in {"history": [], "last": None, "p": None}.items():
    st.session_state.setdefault(k, v)

hist = st.session_state.history


def commit(res):
    hist.append(res)
    st.session_state.last = res
    st.rerun()


# ---------- Visual system ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #171717;
        --body: #5f5c57;
        --muted: #77736d;
        --paper: #f5f4f1;
        --card: #ffffff;
        --line: #dedbd5;
        --soft: #eeece7;
        --yellow: #f4cf32;
        --green: #e4f1e4;
    }

    html, body, [class*="css"], .stApp {
        font-family: "Manrope", sans-serif !important;
    }

    html, body {
        background: #aaa8a5 !important;
    }

    .stApp {
        background: #aaa8a5 !important;
        color: var(--ink) !important;
    }

    /* The actual Streamlit page surface — explicit selectors avoid theme inheritance. */
    [data-testid="stAppViewContainer"] {
        background: #aaa8a5 !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: #aaa8a5 !important;
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1380px !important;
        padding: 42px 56px 80px !important;
        background: var(--paper) !important;
        color: var(--ink) !important;
        border-radius: 30px !important;
        margin: 24px auto !important;
        box-shadow: 0 22px 55px rgba(0,0,0,.12) !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Global Streamlit text reset for light main canvas */
    [data-testid="stAppViewContainer"] .main p,
    [data-testid="stAppViewContainer"] .main span,
    [data-testid="stAppViewContainer"] .main label,
    [data-testid="stAppViewContainer"] .main li,
    [data-testid="stAppViewContainer"] .main div,
    [data-testid="stAppViewContainer"] .main td,
    [data-testid="stAppViewContainer"] .main th {
        color: inherit;
    }

    [data-testid="stAppViewContainer"] .main .stCaption,
    [data-testid="stAppViewContainer"] .main [data-testid="stCaptionContainer"] {
        color: #69655f !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #1b1b1b !important;
    }
    section[data-testid="stSidebar"] > div {
        padding: 30px 22px !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f7f6f2;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"],
    section[data-testid="stSidebar"] small {
        color: #f1efeb !important;
    }

    .brand {
        color: #f7f6f2 !important;
        font-size: 17px;
        font-weight: 800;
        letter-spacing: -0.4px;
        margin-bottom: 34px;
    }
    .brand span {
        display: inline-block;
        width: 7px;
        height: 7px;
        background: var(--yellow);
        border-radius: 50%;
        margin-left: 3px;
        vertical-align: 2px;
    }

    .side-label {
        color: #aaa7a1 !important;
        text-transform: uppercase;
        letter-spacing: 1.7px;
        font-size: 10px !important;
        font-weight: 800;
        margin: 20px 0 9px;
    }

    .hero-kicker {
        color: #77736d !important;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 8px;
        margin-bottom: 16px;
    }

    .hero-title {
        color: #111111 !important;
        font-size: clamp(44px, 5.3vw, 76px);
        line-height: .97;
        letter-spacing: -4.5px;
        font-weight: 800;
        margin: 0;
        max-width: 920px;
    }

    .hero-title .light {
        color: #96938e !important;
    }

    .hero-copy {
        color: #65615b !important;
        font-size: 14px;
        line-height: 1.75;
        max-width: 760px;
        margin-top: 24px;
        margin-bottom: 28px;
    }

    .pill {
        display: inline-block;
        border: 1px solid #d8d4cd;
        border-radius: 999px;
        padding: 9px 14px;
        font-size: 11px;
        font-weight: 800;
        color: #4f4c47 !important;
        background: #ffffff;
        margin-right: 7px;
    }

    .metric-card {
        background: #ffffff !important;
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 18px 19px;
        min-height: 106px;
    }

    .metric-label {
        color: #7b7770 !important;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #171717 !important;
        font-size: 27px;
        font-weight: 800;
        letter-spacing: -1.2px;
    }

    .section-head {
        color: #171717 !important;
        font-size: 27px;
        font-weight: 800;
        letter-spacing: -1.2px;
        margin: 32px 0 6px;
    }

    .section-sub {
        color: #69655f !important;
        font-size: 12px;
        margin-bottom: 18px;
    }

    .result-card {
        background: #ffffff !important;
        color: #171717 !important;
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 26px 28px;
        margin-top: 18px;
    }

    .result-card b,
    .result-card strong {
        color: #171717 !important;
    }

    .number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 29px;
        height: 29px;
        border-radius: 50%;
        background: #171717 !important;
        color: #ffffff !important;
        font-size: 12px;
        font-weight: 800;
        margin-right: 9px;
    }

    .result-title {
        font-size: 19px;
        font-weight: 800;
        letter-spacing: -.4px;
        color: #171717 !important;
        margin-bottom: 12px;
    }

    .answer {
        background: #f4f3ef !important;
        border-radius: 13px;
        padding: 14px 16px;
        font-size: 14px;
        font-weight: 700;
        color: #242321 !important;
        border: 1px solid #e6e3dc;
        margin-bottom: 20px;
    }

    .green-answer {
        background: var(--green) !important;
        border-color: #cce4cc;
        color: #17351e !important;
    }

    .why-list {
        color: #55514b !important;
        font-size: 13px;
        line-height: 1.65;
        margin: 0;
    }

    .why-list li {
        color: #55514b !important;
        margin-bottom: 8px;
    }

    .mono {
        font-family: "DM Mono", monospace;
    }

    /* Native Streamlit widgets */
    [data-testid="stTabs"] button {
        color: #4d4a45 !important;
        font-weight: 700 !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #171717 !important;
    }

    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stSelectbox"] label {
        color: #35332f !important;
    }

    div[data-testid="stButton"] > button {
        border-radius: 999px !important;
        border: 1px solid #171717 !important;
        background: #171717 !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        min-height: 44px;
    }

    div[data-testid="stButton"] > button:hover {
        background: #333333 !important;
        border-color: #333333 !important;
        color: #ffffff !important;
    }

    div[data-testid="stTextArea"] textarea,
    div[data-testid="stNumberInput"] input {
        background: #ffffff !important;
        border: 1px solid #d8d4cd !important;
        border-radius: 12px !important;
        color: #171717 !important;
        -webkit-text-fill-color: #171717 !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder,
    div[data-testid="stNumberInput"] input::placeholder {
        color: #858078 !important;
        opacity: 1 !important;
    }

    div[data-testid="stFileUploader"] {
        background: #252525 !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 14px !important;
        padding: 8px !important;
    }

    /* Tables must stay dark on the light canvas. */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        color: #171717 !important;
    }
    [data-testid="stTable"] table {
        background: #ffffff !important;
        color: #171717 !important;
        border: 1px solid #dedbd5 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    [data-testid="stTable"] th {
        background: #f0eee9 !important;
        color: #4b4843 !important;
        font-weight: 800 !important;
    }
    [data-testid="stTable"] td {
        background: #ffffff !important;
        color: #252321 !important;
        border-color: #e5e2dc !important;
    }

    /* Expanders / JSON */
    [data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #d9d5ce !important;
        border-radius: 14px !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span {
        color: #252321 !important;
        font-weight: 700 !important;
    }

    .history-item {
        font-family: "DM Mono", monospace;
        font-size: 11px;
        color: #c8c5bf !important;
        padding: 8px 0;
        border-bottom: 1px solid #333;
    }
    .history-top {
        color: #ffffff !important;
        font-weight: 600;
    }

    .trade {
        padding: 12px 0;
        border-bottom: 1px solid var(--line);
        color: #55514b !important;
        font-size: 13px;
        line-height: 1.55;
    }
    .trade b {
        color: #171717 !important;
    }

    /* Alerts / captions on the light canvas */
    [data-testid="stAlert"] * {
        color: #252321 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="brand">ALGORITHM LAB<span></span></div>', unsafe_allow_html=True)

    st.markdown('<div class="side-label">Input data</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload TXT / CSV", type=["txt", "csv"])
    txt = st.text_area(
        "Or enter integers",
        "42 7 19 3 56 28 11 91 34 65 2 77 23 48 15",
        height=115,
        label_visibility="collapsed",
    )

    if st.button("Analyze data", use_container_width=True):
        try:
            raw = up.getvalue().decode() if up else txt
            a = [int(x) for x in raw.replace(",", " ").split()]
            if not 1 <= len(a) <= 100000:
                raise ValueError
        except ValueError:
            st.error("Enter 1 to 100000 valid integers.")
        else:
            st.session_state.p = profile(a)
            st.session_state.input_values = a
            st.session_state.last = recommend_sort(st.session_state.p) if len(a) > 1 else None
            if st.session_state.last:
                hist.append(st.session_state.last)
            st.rerun()

    st.markdown('<div class="side-label">Decision history · stack</div>', unsafe_allow_html=True)

    if hist:
        for i, h in enumerate(reversed(hist)):
            cls = "history-top" if i == 0 else ""
            st.markdown(
                f'<div class="history-item {cls}">{"TOP → " if i == 0 else "• "}{h["title"]}</div>',
                unsafe_allow_html=True,
            )
        if st.button("Undo last decision", use_container_width=True):
            hist.pop()
            st.session_state.last = hist[-1] if hist else None
            st.rerun()
    else:
        st.caption("Stack is empty.")

# ---------- Main ----------
p = st.session_state.p

st.markdown('<div class="hero-kicker">Data structures × algorithms</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-title">Make the right<br><span class="light">algorithmic choice.</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-copy">A cost-model based recommender for sorting and searching. '
    'Analyze your data, choose the constraints, and get an explainable recommendation backed by complexity analysis.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<span class="pill">C logic port</span><span class="pill">Explainable</span><span class="pill">Cost based</span>',
    unsafe_allow_html=True,
)

if not p:
    st.markdown(
        '<div class="result-card"><b>Start with your data.</b><br>'
        '<span style="color:#77736d;font-size:13px">Enter integers in the left panel and click Analyze data.</span></div>',
        unsafe_allow_html=True,
    )
    st.stop()

if p["n"] < 2:
    st.warning("Only one element: nothing to sort or search.")
    st.stop()

# Profile cards
st.markdown('<div class="section-head">Dataset profile</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">The recommender first measures the shape of your input.</div>', unsafe_allow_html=True)

m = st.columns(5)
metrics = [
    ("SIZE (N)", str(p["n"])),
    ("MIN / MAX", f'{p["min"]} / {p["max"]}'),
    ("ASCENDING PAIRS", f'{p["asc_pct"]:.1f}%'),
    ("INVERSIONS", str(p["inversions"])),
    ("DISTINCT VALUES", str(p["distinct"])),
]
for col, (label, value) in zip(m, metrics):
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div></div>',
            unsafe_allow_html=True,
        )

tab_sort, tab_search = st.tabs(["Sorting", "Searching"])

with tab_sort:
    st.markdown('<div class="section-head">Sorting strategy</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Tell the recommender what matters for your implementation.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        linked = st.radio("Storage", ["Array", "Linked list"], horizontal=True, key="storage_sort") == "Linked list"
    with c2:
        stable = st.checkbox("Must be stable")
    with c3:
        worst = st.checkbox("Guaranteed O(n log n) worst case")

    mem = st.checkbox("Memory is tight", disabled=linked)

    if st.button("Recommend sorting algorithm", type="primary"):
        commit(recommend_sort(p, linked, stable, worst, mem and not linked))
        st.markdown(
        '<div class="section-sub">Run the native C implementation on your analyzed data.</div>',
        unsafe_allow_html=True,
    )

    if st.button("Execute C Insertion Sort"):
        raw_values = st.session_state.get("input_values")

        if raw_values is None:
            st.info("Analyze your data again before running the C sort.")
        else:
            result = c_insertion_sort(raw_values)
            st.success("C insertion sort completed.")
            st.write("Sorted array:", result["sorted"])
            st.write("Comparisons:", result["comparisons"])
            st.write("Element shifts:", result["shifts"])

with tab_search:
    st.markdown('<div class="section-head">Searching strategy</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Compare search cost against sorting and update overhead.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        linked2 = st.radio("Storage", ["Array", "Linked list"], horizontal=True, key="storage_search") == "Linked list"
    with c2:
        Q = st.number_input("Number of searches", 1, 10**9, 1000)
    with c3:
        U = st.number_input("Insertions / deletions", 0, 10**9, 0, disabled=linked2)

    if st.button("Recommend searching method", type="primary"):
        commit(recommend_search(p, linked2, int(Q), 0 if linked2 else int(U)))

# ---------- Required 5-point output ----------
r = st.session_state.last
if r:
    st.markdown('<div class="section-head">Recommendation</div>', unsafe_allow_html=True)
    st.caption("Constraints: " + r["constraints"])

    if r["note"]:
        st.warning(r["note"])
    if r["warning"]:
        st.warning(r["warning"])

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown(
            f'<div class="result-card"><div class="result-title"><span class="number">1</span>'
            f'Data structure needed</div><div class="answer">{r["data_structure"]}</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="result-card"><div class="result-title"><span class="number">2</span>'
            f'Algorithm / overall solving approach</div>'
            f'<div class="answer green-answer">{r["recommended"]}</div></div>',
            unsafe_allow_html=True,
        )

        why_html = "".join(f"<li>{x}</li>" for x in r["why"])
        st.markdown(
            f'<div class="result-card"><div class="result-title"><span class="number">3</span>'
            f'Why this combination is suitable</div><ul class="why-list">{why_html}</ul></div>',
            unsafe_allow_html=True,
        )

    with right:
        rows = r["complexity"]
        header = list(rows[0].keys())
        table_html = '<table style="width:100%;border-collapse:collapse;font-size:12px">'
        table_html += "<tr>" + "".join(
            f'<th style="text-align:left;padding:10px;border-bottom:1px solid #dedbd5;color:#77736d">{h}</th>'
            for h in header
        ) + "</tr>"
        for row in rows:
            table_html += "<tr>" + "".join(
                f'<td style="padding:11px 10px;border-bottom:1px solid #eeeae3">{row[h]}</td>'
                for h in header
            ) + "</tr>"
        table_html += "</table>"

        st.markdown(
            f'<div class="result-card"><div class="result-title"><span class="number">4</span>'
            f'Time and space complexity</div>{table_html}'
            f'<div style="color:#77736d;font-size:12px;margin-top:12px">{r["properties"]}</div></div>',
            unsafe_allow_html=True,
        )

        trade_html = "".join(
            f'<div class="trade"><b>{x["algorithm"]}</b> · {x["times_work"]}× the work<br>{x["trade_off"]}</div>'
            for x in r["alternatives"]
        )
        if not trade_html:
            trade_html = '<div class="trade">No alternative remains under the selected constraints.</div>'

        st.markdown(
            f'<div class="result-card"><div class="result-title"><span class="number">5</span>'
            f'Alternative approaches and trade-offs</div>{trade_html}</div>',
            unsafe_allow_html=True,
        )

    with st.expander("Full ranking · estimated steps"):
        st.table(r["ranking"])

    with st.expander("Raw JSON output"):
        st.json(r)
