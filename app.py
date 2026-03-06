# app.py
# PulseGuard — Main Application
# Run with: streamlit run app.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from data_fetcher import get_company_data
from scorer import calculate_risk_score
from monitor import (
    add_loan, load_loans, update_loan_score,
    close_loan, get_days_remaining,
    get_all_loans_summary, get_portfolio_health
)
from utils import (
    get_risk_level, format_pkr,
    get_today, get_score_trend,
    PSX_COMPANIES, get_all_tickers
)

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="PulseGuard — Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# SESSION STATE INIT
# This keeps results visible after any
# button click — fixes the refresh bug
# ─────────────────────────────────────────
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "company_data" not in st.session_state:
    st.session_state.company_data = None
if "score_result" not in st.session_state:
    st.session_state.score_result = None
if "ticker_used" not in st.session_state:
    st.session_state.ticker_used = ""
if "approve_success" not in st.session_state:
    st.session_state.approve_success = ""

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0F172A; }
    .stApp { background-color: #0F172A; }

    .pg-header {
        background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .pg-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    .pg-header p {
        color: #93C5FD;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    .score-card {
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .score-number {
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
    }
    .score-label {
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    .score-rec {
        font-size: 0.9rem;
        margin-top: 0.8rem;
        opacity: 0.85;
    }
    .signal-card {
        border-left: 4px solid;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.6rem;
    }
    .signal-high {
        border-color: #DC2626;
        background: #1F0A0A;
    }
    .signal-medium {
        border-color: #CA8A04;
        background: #1A1500;
    }
    .signal-low {
        border-color: #16A34A;
        background: #0A1A0A;
    }
    .metric-card {
        background: #1E293B;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #334155;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #60A5FA;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 0.2rem;
    }
    .alert-critical {
        background: #1F0A0A;
        border: 1px solid #DC2626;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .alert-warning {
        background: #1A1500;
        border: 1px solid #CA8A04;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .alert-normal {
        background: #0A1A0A;
        border: 1px solid #16A34A;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .loan-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    div[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    .stButton > button {
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8, #1E40AF);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="pg-header">
    <h1>🛡️ PulseGuard</h1>
    <p>AI-Powered Business Risk Intelligence Platform — Pakistan Stock Exchange</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ PulseGuard")
    st.markdown(f"*{get_today()}*")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🔍 Loan Assessment", "📊 Loan Monitoring", "📋 Portfolio Overview"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 📌 Quick Search")
    quick_ticker = st.selectbox(
        "PSX Listed Companies",
        ["Select..."] + get_all_tickers(),
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style='color: #64748B; font-size: 0.75rem;'>
    <b>Data Sources</b><br>
    • Yahoo Finance (PSX)<br>
    • Pakistan Stock Exchange<br>
    • Public Financial Filings<br><br>
    <b>Disclaimer</b><br>
    Risk signals are for informational
    purposes only. Not financial advice.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PAGE 1 — LOAN ASSESSMENT
# ═══════════════════════════════════════════
if "🔍 Loan Assessment" in page:

    st.markdown("## 🔍 Loan Assessment")
    st.markdown("Enter a PSX company ticker to assess loan risk before approval.")

    # ── Search Bar ──
    col1, col2 = st.columns([3, 1])
    with col1:
        default_ticker = quick_ticker if quick_ticker != "Select..." else ""
        ticker_input = st.text_input(
            "Company Ticker Symbol",
            value=default_ticker,
            placeholder="e.g. ENGRO, HBL, LUCK, PSO",
            help="Enter the PSX ticker symbol of the company"
        ).upper().strip()

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze Company", use_container_width=True)

    # ── Company List ──
    with st.expander("📋 View Supported PSX Companies"):
        cols = st.columns(4)
        tickers = get_all_tickers()
        for i, t in enumerate(tickers):
            with cols[i % 4]:
                st.markdown(f"**{t}** — {PSX_COMPANIES[t]}")

    # ── Trigger Analysis ──
    # Only fetch new data when button is clicked
    if analyze_btn and ticker_input:
        with st.spinner(f"Fetching real PSX data for {ticker_input}..."):
            company_data = get_company_data(ticker_input)
            score_result = calculate_risk_score(company_data)

        # Save everything to session state
        # This keeps results visible even after
        # Approve button is clicked
        st.session_state.analyzed = True
        st.session_state.company_data = company_data
        st.session_state.score_result = score_result
        st.session_state.ticker_used = ticker_input
        st.session_state.approve_success = ""

    elif analyze_btn and not ticker_input:
        st.warning("⚠️ Please enter a ticker symbol first.")

    # ── Display Results (from session state) ──
    # This block runs as long as we have results
    # regardless of what button was clicked
    if st.session_state.analyzed and st.session_state.score_result:

        score_result = st.session_state.score_result
        company_data = st.session_state.company_data
        ticker_input = st.session_state.ticker_used

        # ── Error Check ──
        if score_result.get("error"):
            st.error(f"❌ {score_result['error']}")
            st.info("💡 Make sure you're using a valid PSX ticker (e.g. ENGRO, HBL, LUCK)")

        else:
            score      = score_result["score"]
            risk       = score_result["risk"]
            signals    = score_result["signals"]
            components = score_result["component_scores"]
            financials = company_data["financials"]
            stock      = company_data["stock"]
            company_name = PSX_COMPANIES.get(ticker_input, ticker_input)

            st.markdown("---")

            # ── Score + Metrics Row ──
            col_score, col_metrics = st.columns([1, 2])

            with col_score:
                st.markdown(f"""
                <div class="score-card"
                     style="background:{risk['bg']}; color:{risk['color']}">
                    <div style="font-size:1rem; font-weight:600;">
                        {company_name} ({ticker_input})
                    </div>
                    <div class="score-number">{score}</div>
                    <div class="score-label">{risk['emoji']} {risk['level']}</div>
                    <div class="score-rec">{risk['recommendation']}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_metrics:
                st.markdown("#### 📊 Key Financial Metrics")
                m1, m2, m3, m4 = st.columns(4)

                cr    = financials.get("current_ratio")
                dte   = financials.get("debt_to_equity")
                pm    = financials.get("profit_margin")
                price = stock.get("current_price")

                with m1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">
                            {f'{cr:.2f}' if cr else 'N/A'}
                        </div>
                        <div class="metric-label">Current Ratio</div>
                    </div>""", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">
                            {f'{dte:.1f}%' if dte else 'N/A'}
                        </div>
                        <div class="metric-label">Debt / Equity</div>
                    </div>""", unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">
                            {f'{pm*100:.1f}%' if pm else 'N/A'}
                        </div>
                        <div class="metric-label">Profit Margin</div>
                    </div>""", unsafe_allow_html=True)
                with m4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">
                            {f'PKR {price:.0f}' if price else 'N/A'}
                        </div>
                        <div class="metric-label">Current Price</div>
                    </div>""", unsafe_allow_html=True)

                # Component bar chart
                st.markdown("<br>", unsafe_allow_html=True)
                if components:
                    colors = []
                    for v in components.values():
                        if v >= 70:   colors.append("#16A34A")
                        elif v >= 40: colors.append("#CA8A04")
                        else:         colors.append("#DC2626")

                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=list(components.keys()),
                        y=list(components.values()),
                        marker_color=colors,
                        text=[str(v) for v in components.values()],
                        textposition="outside"
                    ))
                    fig.update_layout(
                        title="Component Scores Breakdown",
                        paper_bgcolor="#1E293B",
                        plot_bgcolor="#1E293B",
                        font=dict(color="white"),
                        height=220,
                        margin=dict(t=40, b=20, l=20, r=20),
                        yaxis=dict(range=[0, 115], showgrid=False),
                        xaxis=dict(showgrid=False)
                    )
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # ── Signals + Price Chart ──
            col_signals, col_chart = st.columns([1, 1])

            with col_signals:
                st.markdown("#### ⚠️ Risk Signals Detected")
                if not signals:
                    st.success("✅ No significant risk signals detected.")
                else:
                    for sig in signals:
                        sev = sig["severity"]
                        css  = ("signal-high"   if sev == "HIGH"
                                else "signal-medium" if sev == "MEDIUM"
                                else "signal-low")
                        icon = ("🔴" if sev == "HIGH"
                                else "🟡" if sev == "MEDIUM"
                                else "🟢")
                        st.markdown(f"""
                        <div class="signal-card {css}">
                            <strong>{icon} {sig['message']}</strong><br>
                            <small style="color:#94A3B8">{sig['detail']}</small>
                        </div>
                        """, unsafe_allow_html=True)

            with col_chart:
                st.markdown("#### 📈 Price History (2 Years)")
                price_history = stock.get("price_history")
                if price_history is not None and len(price_history) > 0:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=price_history["date"],
                        y=price_history["close"],
                        mode="lines",
                        line=dict(color="#2563EB", width=2),
                        fill="tozeroy",
                        fillcolor="rgba(37,99,235,0.1)",
                        name="Stock Price"
                    ))
                    fig2.update_layout(
                        paper_bgcolor="#1E293B",
                        plot_bgcolor="#1E293B",
                        font=dict(color="white"),
                        height=300,
                        margin=dict(t=20, b=20, l=20, r=20),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True,
                                   gridcolor="#334155",
                                   title="PKR")
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Price history not available.")

            st.markdown("---")

            # ── Approve & Monitor Section ──
            st.markdown("#### 🔒 Approve Loan & Add to Monitoring")
            st.markdown(
                "Set the loan details below. "
                "PulseGuard will watch this company "
                "for the full duration of the loan."
            )

            mon_col1, mon_col2, mon_col3 = st.columns(3)
            with mon_col1:
                loan_amount = st.number_input(
                    "Loan Amount (PKR)",
                    min_value=100000,
                    max_value=10000000000,
                    value=10000000,
                    step=1000000,
                    format="%d"
                )
            with mon_col2:
                loan_duration = st.selectbox(
                    "Loan Duration",
                    [3, 6, 12, 24, 36, 48, 60],
                    index=2,
                    format_func=lambda x: f"{x} months"
                )
            with mon_col3:
                st.markdown("<br>", unsafe_allow_html=True)
                add_monitoring_btn = st.button(
                    "✅ Approve & Monitor",
                    use_container_width=True
                )

            # Show previous approval message if any
            if st.session_state.approve_success:
                st.success(st.session_state.approve_success)
                st.info("➡️ Go to **📊 Loan Monitoring** in the sidebar to track this company.")

            if add_monitoring_btn:
                result = add_loan(
                    ticker=ticker_input,
                    company_name=company_name,
                    loan_amount=loan_amount,
                    loan_duration_months=loan_duration,
                    initial_score=score
                )
                if result["success"]:
                    # Save message to session so it
                    # survives the rerun
                    st.session_state.approve_success = (
                        f"✅ {company_name} loan approved! "
                        f"{format_pkr(loan_amount)} for "
                        f"{loan_duration} months. "
                        "Now being monitored."
                    )
                    st.success(st.session_state.approve_success)
                    st.info("➡️ Go to **📊 Loan Monitoring** in the sidebar.")
                else:
                    st.warning(result["message"])


# ═══════════════════════════════════════════
# PAGE 2 — LOAN MONITORING
# ═══════════════════════════════════════════
elif "📊 Loan Monitoring" in page:

    st.markdown("## 📊 Loan Monitoring")
    st.markdown(
        "Track all active loans. "
        "Re-check scores and get alerts when risk changes."
    )

    loans = load_loans()
    active_loans = [l for l in loans if l["status"] == "ACTIVE"]

    if not active_loans:
        st.info(
            "📭 No active loans being monitored yet.\n\n"
            "Go to **🔍 Loan Assessment**, analyze a company, "
            "approve the loan, and it will appear here."
        )
    else:
        # ── Portfolio Summary ──
        summary = get_all_loans_summary()

        h1, h2, h3, h4 = st.columns(4)
        with h1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{summary['total_active']}</div>
                <div class="metric-label">Active Loans</div>
            </div>""", unsafe_allow_html=True)
        with h2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#DC2626">
                    {summary['critical_alerts']}
                </div>
                <div class="metric-label">🚨 Critical</div>
            </div>""", unsafe_allow_html=True)
        with h3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#CA8A04">
                    {summary['warnings']}
                </div>
                <div class="metric-label">⚠️ Warnings</div>
            </div>""", unsafe_allow_html=True)
        with h4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:#16A34A">
                    {summary['normal']}
                </div>
                <div class="metric-label">✅ Normal</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Loan Cards ──
        for loan in active_loans:
            risk      = get_risk_level(loan["current_score"])
            days_left = get_days_remaining(loan["end_date"])
            trend     = get_score_trend(
                loan["initial_score"], loan["current_score"]
            )

            with st.expander(
                f"{risk['emoji']}  {loan['company_name']} "
                f"({loan['ticker']})  —  Score: "
                f"{loan['current_score']}  |  {risk['level']}  "
                f"|  {days_left} days remaining",
                expanded=loan["alert_level"] in ["CRITICAL", "WARNING"]
            ):
                lc1, lc2, lc3 = st.columns(3)

                with lc1:
                    st.markdown("**📋 Loan Details**")
                    st.markdown(f"Amount: **{format_pkr(loan['loan_amount'])}**")
                    st.markdown(f"Duration: **{loan['loan_duration_months']} months**")
                    st.markdown(f"Start: **{loan['start_date']}**")
                    st.markdown(f"End: **{loan['end_date']}**")
                    st.markdown(f"Days Left: **{days_left} days**")

                with lc2:
                    st.markdown("**📊 Risk Score Tracking**")
                    st.markdown(f"Initial Score: **{loan['initial_score']}**")
                    st.markdown(f"Current Score: **{loan['current_score']}**")
                    st.markdown(f"Lowest Score: **{loan['lowest_score']}**")
                    st.markdown(f"Trend: **{trend}**")

                    if len(loan["score_history"]) > 1:
                        hist_df = pd.DataFrame(loan["score_history"])
                        fig3 = go.Figure()
                        fig3.add_trace(go.Scatter(
                            x=hist_df["date"],
                            y=hist_df["score"],
                            mode="lines+markers",
                            line=dict(color="#2563EB", width=2),
                            marker=dict(size=6)
                        ))
                        fig3.add_hline(
                            y=40, line_dash="dash",
                            line_color="#DC2626",
                            annotation_text="High Risk"
                        )
                        fig3.add_hline(
                            y=70, line_dash="dash",
                            line_color="#16A34A",
                            annotation_text="Low Risk"
                        )
                        fig3.update_layout(
                            paper_bgcolor="#1E293B",
                            plot_bgcolor="#1E293B",
                            font=dict(color="white"),
                            height=200,
                            margin=dict(t=10, b=10, l=10, r=10),
                            showlegend=False,
                            yaxis=dict(range=[0, 100])
                        )
                        st.plotly_chart(fig3, use_container_width=True)

                with lc3:
                    st.markdown("**🔔 Alerts**")
                    if not loan["alerts"]:
                        st.markdown("✅ No alerts generated yet.")
                    else:
                        for alert in reversed(loan["alerts"][-3:]):
                            atype = alert.get("type", "")
                            css = (
                                "alert-critical" if atype == "CRITICAL"
                                else "alert-warning" if atype == "WARNING"
                                else "alert-normal"
                            )
                            st.markdown(f"""
                            <div class="{css}">
                                <small style="color:#94A3B8">
                                    {alert['date']}
                                </small><br>
                                <strong>{alert['message']}</strong><br>
                                <small>{alert['action']}</small>
                            </div>
                            """, unsafe_allow_html=True)

                # ── Buttons ──
                btn1, btn2 = st.columns(2)
                with btn1:
                    if st.button(
                        f"🔄 Re-check {loan['ticker']}",
                        key=f"recheck_{loan['ticker']}"
                    ):
                        with st.spinner("Fetching latest data..."):
                            fresh_data  = get_company_data(loan["ticker"])
                            fresh_score = calculate_risk_score(fresh_data)

                        if fresh_score.get("score") is not None:
                            new_score = fresh_score["score"]
                            result    = update_loan_score(
                                loan["ticker"], new_score
                            )
                            if result["alert"]:
                                a = result["alert"]
                                if a["type"] == "CRITICAL":
                                    st.error(a["message"])
                                elif a["type"] == "WARNING":
                                    st.warning(a["message"])
                                else:
                                    st.success(a["message"])
                                st.info(f"**Action:** {a['action']}")
                            else:
                                st.success(
                                    f"✅ Score updated to {new_score}. "
                                    "No significant change."
                                )
                            st.rerun()
                        else:
                            st.error("Could not fetch updated data.")

                with btn2:
                    if st.button(
                        f"🔒 Close Loan",
                        key=f"close_{loan['ticker']}"
                    ):
                        result = close_loan(loan["ticker"])
                        st.success(result["message"])
                        st.rerun()


# ═══════════════════════════════════════════
# PAGE 3 — PORTFOLIO OVERVIEW
# ═══════════════════════════════════════════
elif "📋 Portfolio Overview" in page:

    st.markdown("## 📋 Portfolio Overview")
    st.markdown(
        "Complete overview of all companies assessed and monitored."
    )

    loans  = load_loans()
    active = [l for l in loans if l["status"] == "ACTIVE"]
    closed = [l for l in loans if l["status"] == "CLOSED"]

    if not loans:
        st.info(
            "No data yet. Start by assessing a company "
            "in **🔍 Loan Assessment**."
        )
    else:
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(active)}</div>
                <div class="metric-label">Active Monitored Loans</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(closed)}</div>
                <div class="metric-label">Closed Loans</div>
            </div>""", unsafe_allow_html=True)
        with s3:
            total_exposure = sum(l["loan_amount"] for l in active)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">
                    {format_pkr(total_exposure)}
                </div>
                <div class="metric-label">Total Active Exposure</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if active:
            st.markdown("### 🟢 Active Loans")
            table_data = []
            for l in active:
                risk = get_risk_level(l["current_score"])
                table_data.append({
                    "Company":      l["company_name"],
                    "Ticker":       l["ticker"],
                    "Loan Amount":  format_pkr(l["loan_amount"]),
                    "Score":        l["current_score"],
                    "Risk Level":   f"{risk['emoji']} {risk['level']}",
                    "Alert Status": l["alert_level"],
                    "Days Left":    get_days_remaining(l["end_date"]),
                    "Start Date":   l["start_date"]
                })
            st.dataframe(
                pd.DataFrame(table_data),
                use_container_width=True,
                hide_index=True
            )

        if active:
            st.markdown("### 📊 Risk Distribution")
            low  = sum(1 for l in active if l["current_score"] >= 70)
            med  = sum(1 for l in active if 40 <= l["current_score"] < 70)
            high = sum(1 for l in active if l["current_score"] < 40)

            fig4 = go.Figure(data=[go.Pie(
                labels=["Low Risk", "Medium Risk", "High Risk"],
                values=[low, med, high],
                marker_colors=["#16A34A", "#CA8A04", "#DC2626"],
                hole=0.4
            )])
            fig4.update_layout(
                paper_bgcolor="#1E293B",
                font=dict(color="white"),
                height=300,
                margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig4, use_container_width=True)

        if closed:
            st.markdown("### 🔒 Closed Loans")
            closed_data = []
            for l in closed:
                closed_data.append({
                    "Company":       l["company_name"],
                    "Ticker":        l["ticker"],
                    "Loan Amount":   format_pkr(l["loan_amount"]),
                    "Initial Score": l["initial_score"],
                    "Final Score":   l["current_score"],
                    "Closed Date":   l.get("closed_date", "N/A")
                })
            st.dataframe(
                pd.DataFrame(closed_data),
                use_container_width=True,
                hide_index=True
            )