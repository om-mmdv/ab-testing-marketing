"""
Marketing A/B test dashboard (Streamlit).

Run from the project folder:
    streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import norm

BLUE, CYAN, ORANGE = "#3b82f6", "#06b6d4", "#f97316"
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]

st.set_page_config(page_title="A/B test", page_icon="🧮", layout="wide")
st.markdown(
    """<style>
    .card {background: linear-gradient(145deg,#131c2e,#0f1829);
           border:1px solid #22304a; border-radius:16px; padding:16px 18px;}
    .t {color:#8fa3c4; font-size:0.85rem;}
    .v {color:#e6edf7; font-size:1.7rem; font-weight:700;}
    .s {color:#06b6d4; font-size:0.85rem;}
    </style>""", unsafe_allow_html=True)

LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#e6edf7"), margin=dict(l=10, r=10, t=30, b=10))


def card(col, title, value, sub=""):
    """Render one KPI card."""
    col.markdown(f'<div class="card"><div class="t">{title}</div>'
                 f'<div class="v">{value}</div><div class="s">{sub}</div></div>',
                 unsafe_allow_html=True)


def ab_test(c_a, n_a, c_b, n_b, alpha):
    """Two-proportion z-test and CI of the difference (A = ad, B = control)."""
    p_a, p_b = c_a / n_a, c_b / n_b
    pooled = (c_a + c_b) / (n_a + n_b)
    se0 = np.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = (p_a - p_b) / se0
    p_value = 2 * (1 - norm.cdf(abs(z)))
    se = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    half = norm.ppf(1 - alpha / 2) * se
    return p_a, p_b, z, p_value, half


@st.cache_data
def load():
    return pd.read_csv("data/summary.csv")


summary = load()

st.title("Marketing A/B Test")
st.caption("Ad (treatment) vs PSA (control), 588,101 users. "
           "Dataset: Marketing A/B Testing (Kaggle).")

tab1, tab2, tab3 = st.tabs(["Result", "Segments", "Calculator"])

# ---------- Tab 1: overall result ----------
with tab1:
    totals = (summary[summary["segment"] == "Weekday"]
              .groupby("group")[["users", "conversions"]].sum())
    n_a, c_a = int(totals.loc["ad", "users"]), int(totals.loc["ad", "conversions"])
    n_b, c_b = int(totals.loc["psa", "users"]), int(totals.loc["psa", "conversions"])
    alpha = st.select_slider("Significance level", [0.01, 0.05, 0.10], value=0.05)
    p_a, p_b, z, p_val, half = ab_test(c_a, n_a, c_b, n_b, alpha)
    diff = p_a - p_b

    cols = st.columns(4)
    card(cols[0], "Conversion, ad", f"{p_a:.3%}", f"{c_a:,} of {n_a:,}")
    card(cols[1], "Conversion, control", f"{p_b:.3%}", f"{c_b:,} of {n_b:,}")
    card(cols[2], "Difference", f"{diff * 100:+.3f} pp", f"lift {diff / p_b:+.0%}")
    card(cols[3], "p-value", f"{p_val:.1e}",
         "significant" if p_val < alpha else "not significant")
    st.write("")
    st.write(f"**{1 - alpha:.0%} CI of the difference:** "
             f"[{(diff - half) * 100:.3f}, {(diff + half) * 100:.3f}] pp. "
             f"Extra purchases attributed to the ad: about {diff * n_a:,.0f}.")
    fig = go.Figure(go.Bar(
        x=["Control (PSA)", "Ad"], y=[p_b * 100, p_a * 100],
        marker_color=[ORANGE, BLUE],
        error_y=dict(type="data", array=[
            1.96 * np.sqrt(p_b * (1 - p_b) / n_b) * 100,
            1.96 * np.sqrt(p_a * (1 - p_a) / n_a) * 100])))
    fig.update_layout(height=340, yaxis_title="Conversion, %", **LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Tab 2: segments ----------
with tab2:
    name = st.radio("Segment by", ["Ads seen", "Weekday", "Hour"], horizontal=True)
    seg = summary[summary["segment"] == name]
    wide = seg.pivot(index="value", columns="group", values=["users", "conversions"])
    wide = wide.dropna()
    wide = wide[wide[("users", "psa")] >= 100]  # tiny control groups are too noisy
    order = (ADS := ["1-5", "6-10", "11-20", "21-50", "51-100", "100+"]) \
        if name == "Ads seen" else (DAY_ORDER if name == "Weekday" else None)
    wide = wide.reindex(order).dropna() if order else wide.sort_index(key=lambda s: s.astype(int))

    p_ad = wide[("conversions", "ad")] / wide[("users", "ad")]
    p_ps = wide[("conversions", "psa")] / wide[("users", "psa")]
    ci = 1.96 * np.sqrt(p_ad * (1 - p_ad) / wide[("users", "ad")]
                        + p_ps * (1 - p_ps) / wide[("users", "psa")])
    fig = go.Figure(go.Bar(x=wide.index, y=(p_ad - p_ps) * 100, marker_color=CYAN,
                           error_y=dict(type="data", array=ci * 100)))
    fig.add_hline(y=0, line_color=ORANGE)
    fig.update_layout(height=380, yaxis_title="Uplift (ad - psa), pp", **LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Whiskers are 95% intervals. Segments with fewer than 100 control "
               "users are hidden. Many segments mean many comparisons, so treat "
               "differences as hypotheses, not proof.")

# ---------- Tab 3: calculator ----------
with tab3:
    st.write("Enter your own experiment and see the verdict.")
    a, b = st.columns(2)
    n1 = a.number_input("Users, group A", 100, 50_000_000, 10_000, 100)
    k1 = a.number_input("Conversions, group A", 0, 50_000_000, 520, 10)
    n2 = b.number_input("Users, group B", 100, 50_000_000, 10_000, 100)
    k2 = b.number_input("Conversions, group B", 0, 50_000_000, 480, 10)
    al = st.select_slider("Significance level ", [0.01, 0.05, 0.10], value=0.05)
    if 0 < k1 < n1 and 0 < k2 < n2:
        pa, pb, zz, pv, hf = ab_test(k1, n1, k2, n2, al)
        cols = st.columns(3)
        card(cols[0], "A vs B", f"{(pa - pb) * 100:+.2f} pp", f"{pa:.2%} vs {pb:.2%}")
        card(cols[1], "p-value", f"{pv:.3f}", "significant" if pv < al else "not significant")
        card(cols[2], f"{1 - al:.0%} CI",
             f"[{(pa - pb - hf) * 100:.2f}, {(pa - pb + hf) * 100:.2f}] pp")
    else:
        st.warning("Conversions must be between 0 and the number of users.")