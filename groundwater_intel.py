# ============================================================
# GROUNDWATER INTEL
# California Agricultural Well Analysis
# AGB 470 · Cal Poly SLO · 2026
# ============================================================
# Run with: streamlit run groundwater_intel.py
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Groundwater Intel",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
  /* Import fonts */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  /* Global */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Hide default streamlit menu and footer */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}

  /* Main background */
  .stApp { background: #f4f6f9; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #0a1628;
  }
  section[data-testid="stSidebar"] * {
    color: white !important;
  }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stSlider label {
    color: #7AADBE !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* Persona cards */
  .persona-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 28px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    height: 100%;
  }
  .persona-card:hover {
    border-color: #1b7f8e;
    box-shadow: 0 4px 20px rgba(27,127,142,0.15);
    transform: translateY(-2px);
  }
  .persona-card.selected {
    border-color: #1b7f8e;
    background: #f0f9fb;
  }
  .persona-icon { font-size: 2.5rem; margin-bottom: 12px; }
  .persona-title {
    font-size: 1.1rem; font-weight: 700;
    color: #0a1628; margin-bottom: 8px;
  }
  .persona-desc { font-size: 0.85rem; color: #6b7280; line-height: 1.5; }

  /* KPI cards */
  .kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    border-left: 4px solid #1b7f8e;
    box-shadow: 0 1px 8px rgba(0,0,0,0.07);
  }
  .kpi-card.red { border-color: #E24B4A; }
  .kpi-card.amber { border-color: #EF9F27; }
  .kpi-card.green { border-color: #2D9E6B; }
  .kpi-val { font-size: 1.8rem; font-weight: 700; color: #0a1628; }
  .kpi-lbl { font-size: 0.78rem; color: #6b7280; margin-top: 4px;
             text-transform: uppercase; letter-spacing: 0.05em; }
  .kpi-note { font-size: 0.75rem; color: #9ca3af; margin-top: 4px; font-style: italic; }

  /* Section headers */
  .section-header {
    font-size: 1.4rem; font-weight: 700;
    color: #0a1628; margin-bottom: 4px;
  }
  .section-sub {
    font-size: 0.9rem; color: #6b7280;
    margin-bottom: 20px; line-height: 1.6;
  }

  /* Story callout boxes */
  .callout {
    background: #f0f9fb;
    border-left: 4px solid #1b7f8e;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 0.9rem;
    line-height: 1.65;
    color: #374151;
  }
  .callout.red { border-color: #E24B4A; background: #fff5f5; }
  .callout.amber { border-color: #EF9F27; background: #fffbf0; }
  .callout.green { border-color: #2D9E6B; background: #f0faf5; }

  /* Nav tabs */
  .nav-tab {
    display: inline-block;
    padding: 8px 20px;
    margin-right: 8px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    background: white;
    border: 1px solid #e2e8f0;
    color: #374151;
  }
  .nav-tab.active {
    background: #0a1628;
    color: white;
    border-color: #0a1628;
  }
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ─────────────────────────────────────────────
LIVE_URL = (
    "https://data.cnra.ca.gov/dataset/647afc02-8954-426d-aabd-eff418d2652c"
    "/resource/8da7b93b-4e69-495d-9caa-335691a1896b/download/wellcompletionreports.csv"
)
LOCAL_FILE = "wellcompletionreports.csv"

@st.cache_data(show_spinner=False)
def load_data(use_live: bool = False) -> pd.DataFrame:
    """Load, clean, and filter the well completion dataset."""
    import os
    import requests
    from io import StringIO

    if use_live:
        try:
            st.toast("Downloading live data from California DWR...", icon="📡")
            response = requests.get(LIVE_URL, verify=False, timeout=300)
            df = pd.read_csv(StringIO(response.text), low_memory=False)
        except Exception as e:
            st.warning(f"Live download failed: {e}. Trying local file.")
            df = pd.read_csv(LOCAL_FILE, low_memory=False)
   else:
        import os
        if os.path.exists(LOCAL_FILE):
            df = pd.read_csv(LOCAL_FILE, low_memory=False)
        else:
            import requests
            from io import StringIO
            response = requests.get(LIVE_URL, verify=False, timeout=300)
            df = pd.read_csv(StringIO(response.text), low_memory=False)
        else:
            st.info("Local file not found — downloading from California DWR. "
                    "This takes 5–15 minutes...")
            response = requests.get(LIVE_URL, verify=False, timeout=300)
            df = pd.read_csv(StringIO(response.text), low_memory=False)

    # Date cleaning
    df["DATEWORKENDED"] = pd.to_datetime(df["DATEWORKENDED"], errors="coerce")
    df["YEAR"] = df["DATEWORKENDED"].dt.year
    df = df[(df["YEAR"] >= 1980) & (df["YEAR"] <= 2025)].copy()

    # Agriculture filter
    ag_filter = df["PLANNEDUSEFORMERUSE"].astype(str).str.contains(
        "Irrigation - Agriculture|Stock or Animal Watering",
        case=False, na=False
    )
    df = df[ag_filter].copy()

    # Cap outliers at 99th percentile
    for col in ["TOTALDRILLDEPTH", "TOTALCOMPLETEDDEPTH",
                "STATICWATERLEVEL", "WELLYIELD"]:
        q99 = df[col].quantile(0.99)
        df[col] = df[col].clip(upper=q99)

    # Fix longitude sign
    df.loc[df["DECIMALLONGITUDE"] > 0, "DECIMALLONGITUDE"] *= -1

    return df

    # Date cleaning
    df["DATEWORKENDED"] = pd.to_datetime(df["DATEWORKENDED"], errors="coerce")
    df["YEAR"] = df["DATEWORKENDED"].dt.year
    df = df[(df["YEAR"] >= 1980) & (df["YEAR"] <= 2025)].copy()

    # Agriculture filter
    ag_filter = df["PLANNEDUSEFORMERUSE"].astype(str).str.contains(
        "Irrigation - Agriculture|Stock or Animal Watering",
        case=False, na=False
    )
    df = df[ag_filter].copy()

    # Cap outliers at 99th percentile
    for col in ["TOTALDRILLDEPTH", "TOTALCOMPLETEDDEPTH",
                "STATICWATERLEVEL", "WELLYIELD"]:
        q99 = df[col].quantile(0.99)
        df[col] = df[col].clip(upper=q99)

    # Fix longitude sign if needed
    df.loc[df["DECIMALLONGITUDE"] > 0, "DECIMALLONGITUDE"] *= -1

    return df

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px'>
      <div style='font-size:2rem'>💧</div>
      <div style='font-size:1.1rem;font-weight:700;color:white'>Groundwater Intel</div>
      <div style='font-size:0.75rem;color:#7AADBE;margin-top:4px'>
        California Agricultural Wells<br>1980–2025
      </div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.1);margin:10px 0 20px'>
    """, unsafe_allow_html=True)

    # Persona switcher
    st.markdown("<div style='font-size:0.7rem;color:#7AADBE;text-transform:uppercase;"
                "letter-spacing:0.05em;margin-bottom:8px'>Your Role</div>",
                unsafe_allow_html=True)
    persona = st.selectbox(
        "persona",
        ["🌾 Farmer", "🏦 Lender", "💧 Water Manager", "📊 Student"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1);margin:16px 0'>",
                unsafe_allow_html=True)

    # Page navigation
    st.markdown("<div style='font-size:0.7rem;color:#7AADBE;text-transform:uppercase;"
                "letter-spacing:0.05em;margin-bottom:8px'>Navigate</div>",
                unsafe_allow_html=True)
    page = st.radio(
        "page",
        ["🏠 Home", "📖 My Story", "🗺️ Well Map",
         "🔍 County Deep Dive", "📋 Data Explorer", "⚗️ Methods"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1);margin:16px 0'>",
                unsafe_allow_html=True)

    # Data source toggle
    st.markdown("<div style='font-size:0.7rem;color:#7AADBE;text-transform:uppercase;"
                "letter-spacing:0.05em;margin-bottom:8px'>Data Source</div>",
                unsafe_allow_html=True)
    use_live = st.toggle("Pull live from DWR", value=False)
    if use_live:
        st.markdown("<div style='font-size:0.72rem;color:#EF9F27'>"
                    "⚠️ Live download takes 5–15 min</div>",
                    unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1);margin:16px 0'>",
                unsafe_allow_html=True)

    # Filters
    st.markdown("<div style='font-size:0.7rem;color:#7AADBE;text-transform:uppercase;"
                "letter-spacing:0.05em;margin-bottom:8px'>Filters</div>",
                unsafe_allow_html=True)

    year_range = st.slider("Year range", 1980, 2025, (1980, 2025))

    # Load data (after toggle so we know live vs local)
    with st.spinner("Loading Groundwater Intel data..."):
        df_full = load_data(use_live)

    all_counties = sorted(df_full["COUNTYNAME"].dropna().unique().tolist())
    county_filter = st.multiselect(
        "Counties (leave blank for all)",
        all_counties,
        placeholder="All counties"
    )

    depth_max = int(df_full["TOTALDRILLDEPTH"].max())
    depth_range = st.slider("Drill depth (ft)", 0, depth_max, (0, depth_max))

# ── APPLY FILTERS ────────────────────────────────────────────
df = df_full.copy()
df = df[(df["YEAR"] >= year_range[0]) & (df["YEAR"] <= year_range[1])]
if county_filter:
    df = df[df["COUNTYNAME"].isin(county_filter)]
df = df[
    (df["TOTALDRILLDEPTH"].isna()) |
    ((df["TOTALDRILLDEPTH"] >= depth_range[0]) &
     (df["TOTALDRILLDEPTH"] <= depth_range[1]))
]

# ── COMPUTED STATS ───────────────────────────────────────────
total_wells   = len(df)
median_yield  = df["WELLYIELD"].median()
median_depth  = df["TOTALDRILLDEPTH"].median()
yearly = df.groupby("YEAR").size().reset_index()
yearly.columns = ["Year", "Wells"]
yearly.columns = ["Year", "Wells"]
peak_row      = yearly.loc[yearly["Wells"].idxmax()]
peak_year     = int(peak_row["Year"])
peak_count    = int(peak_row["Wells"])

county_summary = df.groupby("COUNTYNAME").agg(
    Well_Count       =("WCRNUMBER",        "count"),
    Avg_Depth        =("TOTALDRILLDEPTH",  "mean"),
    Median_Yield     =("WELLYIELD",        "median"),
    Avg_Water_Table  =("STATICWATERLEVEL", "mean"),
).round(1).sort_values("Well_Count", ascending=False).reset_index()

# ══════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════

# ── HOME PAGE ─────────────────────────────────────────────────
if page == "🏠 Home":

    # Hero
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0a1628,#0d2b55,#1b7f8e);
                border-radius:16px;padding:48px 40px;margin-bottom:28px;
                text-align:center;color:white'>
      <div style='font-size:2.8rem;font-weight:700;line-height:1.2;margin-bottom:12px'>
        California Is Running<br>Out of <span style='color:#28b5c8'>Water.</span>
      </div>
      <div style='font-size:1.05rem;opacity:.85;max-width:680px;
                  margin:0 auto 8px;line-height:1.75'>
        An analysis of <strong>{total_wells:,} cleaned agriculture well records</strong>
        spanning 45 years reveals a state under serious groundwater stress —
        shaped by historic drought, a landmark policy response,
        and a <strong>50× productivity gap</strong> between California's
        best and worst counties.
      </div>
      <div style='font-size:0.8rem;opacity:0.5;margin-top:16px'>
        AGB 470 · Cal Poly SLO · May 2026 ·
        Source: California SWRCB Well Completion Reports
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, f"{total_wells:,}", "Cleaned records", "1.1M raw rows analyzed", "teal"),
        (k2, f"{int(median_yield):,} GPM", "Median well yield",
         "statewide ag average", "green"),
        (k3, f"{int(median_depth):,} ft", "Median drill depth",
         "trending deeper each decade", "amber"),
        (k4, str(peak_year), "Peak drilling year",
         f"{peak_count:,} wells in one year", "red"),
        (k5, f"{df['COUNTYNAME'].nunique()}", "Counties",
         "across California", "teal"),
    ]
    for col, val, lbl, note, color in kpis:
        with col:
            st.markdown(f"""
            <div class='kpi-card {color}'>
              <div class='kpi-val'>{val}</div>
              <div class='kpi-lbl'>{lbl}</div>
              <div class='kpi-note'>{note}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Persona selector
    st.markdown("""
    <div class='section-header'>Where would you like to start?</div>
    <div class='section-sub'>
      Choose your role and we'll build a personalized data story for you.
    </div>
    """, unsafe_allow_html=True)

    personas = [
        ("🌾", "Farmer",
         "Where should I drill? What yield can I expect? Which counties offer the best groundwater?"),
        ("🏦", "Lender",
         "Which counties carry the most groundwater risk? Where are SGMA restrictions tightest?"),
        ("💧", "Water Manager",
         "What does 45 years of drilling data tell us about drought response and policy impact?"),
        ("📊", "Student",
         "Walk me through the full data story — from raw CSV to every key finding."),
    ]

    c1, c2, c3, c4 = st.columns(4)
    for col, (icon, title, desc) in zip([c1,c2,c3,c4], personas):
        with col:
            st.markdown(f"""
            <div class='persona-card'>
              <div class='persona-icon'>{icon}</div>
              <div class='persona-title'>{title}</div>
              <div class='persona-desc'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start as {title}", key=f"persona_{title}",
                         use_container_width=True):
                st.session_state["persona_choice"] = f"{icon} {title}"
                st.rerun()

    # Quick preview chart
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='section-header'>The Story at a Glance</div>
    <div class='section-sub'>
      45 years of agricultural well completions — one clear narrative.
    </div>
    """, unsafe_allow_html=True)

    yearly_chart = df.groupby("YEAR").size().reset_index()
    yearly_chart.columns = ["Year", "Wells"]

    fig = go.Figure()
    fig.add_vrect(x0=2012, x1=2017, fillcolor="#E24B4A", opacity=0.07,
                  layer="below", line_width=0,
                  annotation_text="Drought 2012–2017",
                  annotation_position="top left",
                  annotation_font=dict(color="#E24B4A", size=11))
    fig.add_vrect(x0=2016, x1=2025, fillcolor="#2D9E6B", opacity=0.05,
                  layer="below", line_width=0,
                  annotation_text="SGMA Effect",
                  annotation_position="top right",
                  annotation_font=dict(color="#2D9E6B", size=11))
    fig.add_trace(go.Scatter(
        x=yearly_chart["Year"], y=yearly_chart["Wells"],
        mode="lines+markers",
        line=dict(color="#1F4E79", width=3),
        marker=dict(
            size=[10 if y == peak_year else 5 for y in yearly_chart["Year"]],
            color=["#E24B4A" if y == peak_year else "#1F4E79"
                   for y in yearly_chart["Year"]]
        ),
        hovertemplate="<b>%{x}</b><br>Wells: %{y:,}<extra></extra>",
        fill="tozeroy", fillcolor="rgba(31,78,121,0.06)"
    ))
    fig.add_annotation(
        x=peak_year, y=peak_count,
        text=f"  Peak: {peak_count:,} wells",
        showarrow=True, arrowhead=2,
        arrowcolor="#E24B4A", font=dict(color="#E24B4A", size=11),
        ax=-60, ay=-40
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, range=[1980, 2025]),
        yaxis=dict(gridcolor="#f0f0f0",
                   title="Agriculture Wells Completed"),
        hovermode="x unified",
        height=380,
        margin=dict(t=20, b=40, l=60, r=40),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='callout red'>
          <strong>🔴 The Drought Signal</strong><br>
          Well completions peaked at nearly 4× the baseline rate in 2015.
          Farmers turned underground when surface water deliveries were cut.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='callout green'>
          <strong>🟢 The SGMA Effect</strong><br>
          Post-2016 drilling has declined every year. California's first
          groundwater law is visibly changing behavior in real data.
        </div>
        """, unsafe_allow_html=True)

# ── PLACEHOLDER PAGES (we build these next) ──────────────────
elif page == "📖 My Story":

    # Detect persona
    raw = persona
    if "Farmer" in raw:       pkey = "farmer"
    elif "Lender" in raw:     pkey = "lender"
    elif "Water Manager" in raw: pkey = "water"
    else:                     pkey = "student"

    # ── FARMER STORY ─────────────────────────────────────────
    if pkey == "farmer":
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1a4731,#2d6a4f);
                    border-radius:16px;padding:36px;margin-bottom:24px;color:white'>
          <div style='font-size:0.8rem;opacity:0.6;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:8px'>Your Story</div>
          <div style='font-size:2rem;font-weight:700;margin-bottom:10px'>
            🌾 Where Should You Drill?
          </div>
          <div style='font-size:1rem;opacity:0.85;line-height:1.7;max-width:700px'>
            You're thinking about drilling a well — or evaluating whether your
            existing wells will survive SGMA restrictions. This view cuts straight
            to what matters: yield, depth, and which counties give you the best
            return on a $100K+ investment.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Chapter 1 — County yield ranking
        st.markdown("### 💧 Chapter 1 — Where the Water Actually Is")
        st.markdown("""
        <div class='section-sub'>
        Median well yield by county — sorted best to worst.
        Green means strong confined aquifer. Red means you're drilling
        for drought insurance, not primary supply.
        </div>
        """, unsafe_allow_html=True)

        yield_data = county_summary[
            county_summary["Median_Yield"].notna()
        ].sort_values("Median_Yield", ascending=False).head(15)

        def ycolor(v):
            if v >= 1000: return "#2D9E6B"
            if v >= 300:  return "#EF9F27"
            return "#E24B4A"

        fig_yield = go.Figure(go.Bar(
            x=yield_data["COUNTYNAME"],
            y=yield_data["Median_Yield"],
            marker_color=[ycolor(v) for v in yield_data["Median_Yield"]],
            hovertemplate="<b>%{x}</b><br>Median yield: %{y:,} GPM<extra></extra>",
            text=yield_data["Median_Yield"].apply(lambda x: f"{int(x):,} GPM"),
            textposition="outside"
        ))
        fig_yield.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="County", tickangle=-20),
            yaxis=dict(title="Median Yield (GPM)", gridcolor="#f0f0f0"),
            height=400, margin=dict(t=20,b=80,l=60,r=40),
            showlegend=False
        )
        st.plotly_chart(fig_yield, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='callout green'>
              <strong>🟢 Best bets</strong><br>
              Kern, Stanislaus, San Joaquin, and Merced all deliver
              1,000–2,000 GPM from confined alluvial aquifers.
              High yield, relatively predictable geology.
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='callout amber'>
              <strong>🟡 Mid-range</strong><br>
              Fresno and Madera deliver 350–525 GPM. Viable for
              most crops but watch the water table trend —
              both are showing overdraft signatures.
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class='callout red'>
              <strong>🔴 Drought insurance only</strong><br>
              San Diego averages 40 GPM at 933 ft depth.
              Riverside is similar. Wells here cost $100K+
              and serve as backup, not primary supply.
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Chapter 2 — Depth vs yield scatter
        st.markdown("### 🔩 Chapter 2 — Does Drilling Deeper Get You More Water?")
        st.markdown("""
        <div class='section-sub'>
        The short answer: it depends entirely on where you are.
        Kern drills 1,000 ft and gets 2,000 GPM.
        San Diego drills the same depth and gets 40 GPM.
        </div>
        """, unsafe_allow_html=True)

        top8 = county_summary.head(8)["COUNTYNAME"].tolist()
        scatter_df = df[df["COUNTYNAME"].isin(top8)][
            ["COUNTYNAME","TOTALDRILLDEPTH","WELLYIELD"]
        ].dropna()

        colors8 = px.colors.qualitative.Bold
        fig_sc = go.Figure()
        for i, county in enumerate(top8):
            sub = scatter_df[scatter_df["COUNTYNAME"]==county]
            fig_sc.add_trace(go.Scatter(
                x=sub["TOTALDRILLDEPTH"], y=sub["WELLYIELD"],
                mode="markers", name=county,
                marker=dict(color=colors8[i % len(colors8)],
                            size=5, opacity=0.4),
                hovertemplate=f"<b>{county}</b><br>"
                              "Depth: %{x:,} ft<br>"
                              "Yield: %{y:,} GPM<extra></extra>"
            ))
        fig_sc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Drill Depth (ft)", showgrid=False),
            yaxis=dict(title="Well Yield (GPM)", gridcolor="#f0f0f0"),
            height=420, margin=dict(t=20,b=50,l=60,r=20)
        )
        st.plotly_chart(fig_sc, use_container_width=True)

        st.markdown("---")

        # Chapter 3 — County picker
        st.markdown("### 📍 Chapter 3 — Pick Your County")
        st.markdown("""
        <div class='section-sub'>
        Select the county you're farming in or considering.
        We'll show you exactly what the data says about drilling there.
        </div>
        """, unsafe_allow_html=True)

        selected = st.selectbox(
            "Choose a county",
            sorted(df["COUNTYNAME"].dropna().unique()),
            key="farmer_county"
        )

        cdf = df[df["COUNTYNAME"]==selected]
        c_yield  = cdf["WELLYIELD"].median()
        c_depth  = cdf["TOTALDRILLDEPTH"].mean()
        c_swl    = cdf["STATICWATERLEVEL"].mean()
        c_wells  = len(cdf)
        c_peak   = int(cdf.groupby("YEAR").size().idxmax()) \
                   if len(cdf) > 0 else "—"

        m1,m2,m3,m4 = st.columns(4)
        for col, val, lbl, color in [
            (m1, f"{int(c_yield):,} GPM" if not pd.isna(c_yield) else "—",
             "Median yield", "green" if not pd.isna(c_yield) and c_yield>=1000
             else "amber" if not pd.isna(c_yield) and c_yield>=300 else "red"),
            (m2, f"{int(c_depth):,} ft" if not pd.isna(c_depth) else "—",
             "Avg drill depth", "teal"),
            (m3, f"{int(c_swl):,} ft" if not pd.isna(c_swl) else "—",
             "Avg water table", "teal"),
            (m4, f"{c_wells:,}", "Wells drilled", "teal"),
        ]:
            with col:
                st.markdown(f"""
                <div class='kpi-card {color}'>
                  <div class='kpi-val'>{val}</div>
                  <div class='kpi-lbl'>{lbl}</div>
                </div>""", unsafe_allow_html=True)

        # Depth trend for selected county
        st.markdown(f"<br>**Drilling depth trend in {selected} County**",
                    unsafe_allow_html=True)
        depth_trend = cdf.groupby("YEAR")["TOTALDRILLDEPTH"].median().reset_index()
        fig_dt = go.Figure(go.Scatter(
            x=depth_trend["YEAR"], y=depth_trend["TOTALDRILLDEPTH"],
            mode="lines+markers",
            line=dict(color="#854F0B", width=2.5),
            fill="tozeroy", fillcolor="rgba(133,79,11,0.07)",
            hovertemplate="<b>%{x}</b><br>Median depth: %{y:,.0f} ft<extra></extra>"
        ))
        fig_dt.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Year", showgrid=False),
            yaxis=dict(title="Median Drill Depth (ft)", gridcolor="#f0f0f0"),
            height=300, margin=dict(t=10,b=40,l=60,r=20)
        )
        st.plotly_chart(fig_dt, use_container_width=True)

    # ── LENDER STORY ─────────────────────────────────────────
    elif pkey == "lender":
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1a2e4a,#2e4a6e);
                    border-radius:16px;padding:36px;margin-bottom:24px;color:white'>
          <div style='font-size:0.8rem;opacity:0.6;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:8px'>Your Story</div>
          <div style='font-size:2rem;font-weight:700;margin-bottom:10px'>
            🏦 Groundwater Risk Assessment
          </div>
          <div style='font-size:1rem;opacity:0.85;line-height:1.7;max-width:700px'>
            Water access is now a material credit risk factor.
            Farms in overdrafted basins face SGMA curtailments that could
            reduce irrigated acreage and crop revenue by 2040.
            Here's what the well completion data tells you about county-level risk.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ⚠️ Chapter 1 — The Overdraft Signal")
        st.markdown("""
        <div class='section-sub'>
        High well density + low yield = overdraft signature.
        Counties drilling intensively but getting less water per well
        are showing classic aquifer depletion patterns.
        </div>""", unsafe_allow_html=True)

        risk_df = county_summary[
            county_summary["Median_Yield"].notna() &
            county_summary["Well_Count"].notna()
        ].head(20).copy()
        risk_df["Risk_Score"] = (
            (risk_df["Well_Count"] / risk_df["Well_Count"].max()) * 50 +
            (1 - risk_df["Median_Yield"] / risk_df["Median_Yield"].max()) * 50
        ).round(1)
        risk_df = risk_df.sort_values("Risk_Score", ascending=False)

        fig_risk = go.Figure(go.Bar(
            x=risk_df["COUNTYNAME"],
            y=risk_df["Risk_Score"],
            marker_color=[
                "#E24B4A" if s >= 60 else
                "#EF9F27" if s >= 40 else "#2D9E6B"
                for s in risk_df["Risk_Score"]
            ],
            hovertemplate="<b>%{x}</b><br>Risk score: %{y:.1f}/100<extra></extra>",
            text=risk_df["Risk_Score"].apply(lambda x: f"{x:.0f}"),
            textposition="outside"
        ))
        fig_risk.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="County", tickangle=-20),
            yaxis=dict(title="Overdraft Risk Score (0–100)",
                       gridcolor="#f0f0f0"),
            height=400, margin=dict(t=20,b=80,l=60,r=40)
        )
        st.plotly_chart(fig_risk, use_container_width=True)

        st.markdown("""
        <div class='callout red'>
          <strong>🔴 Risk score methodology</strong><br>
          Score combines well density (50%) and inverse yield (50%).
          High density + low yield = high score = highest overdraft risk.
          Tulare and Fresno consistently score highest — exactly the counties
          with the most permanent crop exposure and SGMA critical designations.
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📉 Chapter 2 — SGMA Impact Timeline")
        st.markdown("""
        <div class='section-sub'>
        Drilling declined sharply after 2016. Critical basins must reach
        sustainability by 2040 — with 25–35% pumping reductions required.
        </div>""", unsafe_allow_html=True)

        yearly2 = df.groupby("YEAR").size().reset_index()
        yearly2.columns = ["Year","Wells"]
        fig_sgma = go.Figure()
        fig_sgma.add_vrect(x0=2014,x1=2025,
            fillcolor="#2D9E6B", opacity=0.06,
            layer="below", line_width=0,
            annotation_text="SGMA Era (2014→)",
            annotation_position="top left",
            annotation_font=dict(color="#2D9E6B",size=11))
        fig_sgma.add_trace(go.Scatter(
            x=yearly2["Year"], y=yearly2["Wells"],
            mode="lines+markers",
            line=dict(color="#1F4E79",width=2.5),
            fill="tozeroy",fillcolor="rgba(31,78,121,0.07)",
            hovertemplate="<b>%{x}</b><br>Wells: %{y:,}<extra></extra>"
        ))
        fig_sgma.update_layout(
            plot_bgcolor="white",paper_bgcolor="white",
            xaxis=dict(showgrid=False,range=[1980,2025]),
            yaxis=dict(gridcolor="#f0f0f0",title="Wells Completed"),
            height=350,margin=dict(t=20,b=40,l=60,r=20)
        )
        st.plotly_chart(fig_sgma, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🏦 Chapter 3 — County Risk Table")
        st.markdown("""
        <div class='section-sub'>
        Key metrics for lending decisions. Sort by any column.
        </div>""", unsafe_allow_html=True)

        display_df = risk_df[[
            "COUNTYNAME","Well_Count","Median_Yield",
            "Avg_Depth","Risk_Score"
        ]].copy()
        display_df.columns = [
            "County","Well Count","Median Yield (GPM)",
            "Avg Depth (ft)","Risk Score"
        ]
        display_df["Risk Level"] = display_df["Risk Score"].apply(
            lambda x: "🔴 Critical" if x >= 60
            else "🟡 High" if x >= 40 else "🟢 Lower"
        )
        st.dataframe(display_df, use_container_width=True, height=400)

    # ── WATER MANAGER STORY ───────────────────────────────────
    elif pkey == "water":
        st.markdown("""
        <div style='background:linear-gradient(135deg,#0a2e3a,#1b7f8e);
                    border-radius:16px;padding:36px;margin-bottom:24px;color:white'>
          <div style='font-size:0.8rem;opacity:0.6;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:8px'>Your Story</div>
          <div style='font-size:2rem;font-weight:700;margin-bottom:10px'>
            💧 45 Years of Drought & Policy Response
          </div>
          <div style='font-size:1rem;opacity:0.85;line-height:1.7;max-width:700px'>
            The well completion record is one of the most direct measures of
            groundwater pressure available. Here's what 45 years of data
            tells us about how California responds to drought —
            and whether SGMA is working.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📈 Chapter 1 — The Drought Response")
        yearly3 = df.groupby("YEAR").size().reset_index()
        yearly3.columns = ["Year","Wells"]

        fig_wm = go.Figure()
        fig_wm.add_vrect(x0=2012,x1=2017,
            fillcolor="#E24B4A",opacity=0.08,layer="below",line_width=0,
            annotation_text="Drought 2012–2017",
            annotation_position="top left",
            annotation_font=dict(color="#E24B4A",size=11))
        fig_wm.add_vrect(x0=2016,x1=2025,
            fillcolor="#2D9E6B",opacity=0.05,layer="below",line_width=0,
            annotation_text="SGMA Effect",
            annotation_position="top right",
            annotation_font=dict(color="#2D9E6B",size=11))
        fig_wm.add_trace(go.Scatter(
            x=yearly3["Year"],y=yearly3["Wells"],
            mode="lines+markers",
            line=dict(color="#1F4E79",width=3),
            marker=dict(
                size=[10 if y==peak_year else 5 for y in yearly3["Year"]],
                color=["#E24B4A" if y==peak_year else "#1F4E79"
                       for y in yearly3["Year"]]
            ),
            fill="tozeroy",fillcolor="rgba(31,78,121,0.07)",
            hovertemplate="<b>%{x}</b><br>Wells: %{y:,}<extra></extra>"
        ))
        fig_wm.update_layout(
            plot_bgcolor="white",paper_bgcolor="white",
            xaxis=dict(showgrid=False,range=[1980,2025]),
            yaxis=dict(gridcolor="#f0f0f0",title="Wells Completed"),
            height=380,margin=dict(t=20,b=40,l=60,r=20)
        )
        st.plotly_chart(fig_wm, use_container_width=True)

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='callout red'>
              <strong>🔴 Drought surge</strong><br>
              2010 to 2015: well completions went from ~870 to 3,377 —
              a 4× increase in 5 years tracking directly with surface
              water delivery cuts across the state.
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='callout green'>
              <strong>🟢 SGMA working</strong><br>
              Post-2016 decline is consistent and measurable.
              California's first groundwater law is changing
              drilling behavior at scale across all basin types.
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📊 Chapter 2 — Depth Trend Over Time")
        st.markdown("""
        <div class='section-sub'>
        Median drill depth has increased steadily since 1980.
        Farmers are chasing a water table that keeps dropping.
        </div>""", unsafe_allow_html=True)

        depth_yr = df.groupby("YEAR")["TOTALDRILLDEPTH"].median().reset_index()
        fig_depth = go.Figure(go.Scatter(
            x=depth_yr["YEAR"],y=depth_yr["TOTALDRILLDEPTH"],
            mode="lines+markers",
            line=dict(color="#854F0B",width=2.5),
            fill="tozeroy",fillcolor="rgba(133,79,11,0.08)",
            hovertemplate="<b>%{x}</b><br>Median depth: %{y:,.0f} ft<extra></extra>"
        ))
        fig_depth.update_layout(
            plot_bgcolor="white",paper_bgcolor="white",
            xaxis=dict(title="Year",showgrid=False,range=[1980,2025]),
            yaxis=dict(title="Median Drill Depth (ft)",gridcolor="#f0f0f0"),
            height=350,margin=dict(t=10,b=40,l=60,r=20)
        )
        st.plotly_chart(fig_depth, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🗺️ Chapter 3 — Regional Pressure Map")
        top_c = county_summary.head(15)
        fig_bar = go.Figure(go.Bar(
            x=top_c["Well_Count"][::-1],
            y=top_c["COUNTYNAME"][::-1],
            orientation="h",
            marker_color=[
                "#E24B4A" if n > 3000 else
                "#EF9F27" if n > 1500 else "#2E75B6"
                for n in top_c["Well_Count"][::-1]
            ],
            hovertemplate="<b>%{y}</b><br>Wells: %{x:,}<extra></extra>"
        ))
        fig_bar.update_layout(
            plot_bgcolor="white",paper_bgcolor="white",
            xaxis=dict(title="Agriculture Wells",showgrid=False),
            yaxis=dict(title=""),
            height=450,margin=dict(t=10,b=40,l=120,r=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("---")
        st.markdown("### ⚡ Chapter 4 — Before, During & After the Drought")
        st.markdown("""
        <div class='section-sub'>
        Three eras of California groundwater. The numbers tell the story
        better than any paragraph could.
        </div>""", unsafe_allow_html=True)

        # Calculate averages for three periods
        pre_drought = df[df["YEAR"].between(2000,2011)]
        during_drought = df[df["YEAR"].between(2012,2016)]
        post_sgma = df[df["YEAR"].between(2017,2025)]

        pre_avg    = len(pre_drought) / 12
        during_avg = len(during_drought) / 5
        post_avg   = len(post_sgma) / 9

        periods = ["Pre-Drought\n(2000–2011)", 
                   "During Drought\n(2012–2016)", 
                   "Post-SGMA\n(2017–2025)"]
        values = [pre_avg, during_avg, post_avg]
        colors = ["#2E75B6", "#E24B4A", "#2D9E6B"]
        pct_change_drought = ((during_avg - pre_avg) / pre_avg * 100)
        pct_change_sgma    = ((post_avg - during_avg) / during_avg * 100)

        fig_era = go.Figure()
        fig_era.add_trace(go.Bar(
            x=periods,
            y=values,
            marker_color=colors,
            text=[f"{v:,.0f}/yr" for v in values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Avg wells/year: %{y:,.0f}<extra></extra>",
            width=0.5
        ))

        # Arrows showing change
        fig_era.add_annotation(
            x=1, y=max(values)*0.85,
            text=f"▲ +{pct_change_drought:.0f}% during drought",
            showarrow=False,
            font=dict(color="#E24B4A", size=12, family="Arial"),
            bgcolor="rgba(226,75,74,0.1)",
            bordercolor="#E24B4A",
            borderwidth=1,
            borderpad=6
        )
        fig_era.add_annotation(
            x=2, y=max(values)*0.65,
            text=f"▼ {pct_change_sgma:.0f}% after SGMA",
            showarrow=False,
            font=dict(color="#2D9E6B", size=12, family="Arial"),
            bgcolor="rgba(45,158,107,0.1)",
            bordercolor="#2D9E6B",
            borderwidth=1,
            borderpad=6
        )

        fig_era.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont=dict(size=12)),
            yaxis=dict(
                title="Average Wells Completed Per Year",
                gridcolor="#f0f0f0"
            ),
            height=420,
            margin=dict(t=20,b=40,l=70,r=40),
            showlegend=False
        )
        st.plotly_chart(fig_era, use_container_width=True)

        # Three stat cards below
        e1, e2, e3 = st.columns(3)
        with e1:
            st.markdown(f"""
            <div class='kpi-card'>
              <div class='kpi-val'>{pre_avg:,.0f}/yr</div>
              <div class='kpi-lbl'>Pre-drought baseline</div>
              <div class='kpi-note'>2000–2011 average</div>
            </div>""", unsafe_allow_html=True)
        with e2:
            st.markdown(f"""
            <div class='kpi-card red'>
              <div class='kpi-val'>{during_avg:,.0f}/yr</div>
              <div class='kpi-lbl'>During drought peak</div>
              <div class='kpi-note'>+{pct_change_drought:.0f}% above baseline</div>
            </div>""", unsafe_allow_html=True)
        with e3:
            st.markdown(f"""
            <div class='kpi-card green'>
              <div class='kpi-val'>{post_avg:,.0f}/yr</div>
              <div class='kpi-lbl'>Post-SGMA decline</div>
              <div class='kpi-note'>{pct_change_sgma:.0f}% from drought peak</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class='callout green' style='margin-top:16px'>
          <strong>Why this matters</strong><br>
          This isn't just a chart — it's evidence that policy works.
          California passed SGMA in 2014 and drilling dropped measurably
          and consistently every year after. The before/during/after
          framing makes the causal story impossible to ignore.
        </div>""", unsafe_allow_html=True)

    # ── STUDENT STORY ─────────────────────────────────────────
    else:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1a1a2e,#2d2d5e);
                    border-radius:16px;padding:36px;margin-bottom:24px;color:white'>
          <div style='font-size:0.8rem;opacity:0.6;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:8px'>Your Story</div>
          <div style='font-size:2rem;font-weight:700;margin-bottom:10px'>
            📊 The Full Data Story
          </div>
          <div style='font-size:1rem;opacity:0.85;line-height:1.7;max-width:700px'>
            From a 1.1 million row CSV that Excel couldn't open, to a cleaned,
            filtered, analyzed dataset that tells a clear story about
            California's groundwater future. Here's everything we found.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # The pipeline
        st.markdown("### 🔧 Chapter 1 — How We Built This")
        s1,s2,s3,s4 = st.columns(4)
        for col, num, title, desc, color in [
            (s1,"1","Downloaded\nthe data",
             "1.1M row CSV from California DWR — too large for Excel","#1b7f8e"),
            (s2,"2","Python\n+ VS Code",
             "Wrote a script using pandas to read, clean, and filter","#2D9E6B"),
            (s3,"3","Cleaned\nto 58,646",
             "Removed bad dates, outliers, filtered to ag/animal wells","#EF9F27"),
            (s4,"4","Built this\napp","Streamlit dashboard with live data and interactive maps","#E24B4A"),
        ]:
            with col:
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:20px;
                            border-top:4px solid {color};text-align:center;
                            box-shadow:0 1px 8px rgba(0,0,0,0.07)'>
                  <div style='font-size:1.8rem;font-weight:700;color:{color}'>{num}</div>
                  <div style='font-size:0.9rem;font-weight:600;color:#0a1628;
                              margin:8px 0;white-space:pre-line'>{title}</div>
                  <div style='font-size:0.8rem;color:#6b7280;line-height:1.5'>{desc}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📖 Chapter 2 — The Three Key Findings")

        st.markdown("""
        <div class='callout red'>
          <strong>Finding 1 — The Drought Tripled Drilling</strong><br>
          California's 2012–2017 drought forced well completions from ~870/year
          to 3,377 in 2015 — nearly a 4× surge. When surface water was cut,
          farmers had one option: drill deeper.
        </div>
        <div class='callout green' style='margin-top:10px'>
          <strong>Finding 2 — SGMA Is Working</strong><br>
          Post-2016 drilling has declined every year. California's first
          groundwater law (signed 2014) is measurably changing behavior.
          You can literally see a policy working in the data.
        </div>
        <div class='callout amber' style='margin-top:10px'>
          <strong>Finding 3 — The 50× Yield Gap</strong><br>
          Kern County drills 1,017 ft and gets 2,000 GPM.
          San Diego drills 933 ft and gets 40 GPM.
          Same depth — 50× different output. The answer is geology,
          and it means California cannot have a one-size-fits-all water policy.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📊 Chapter 3 — All the Charts")

        # All charts
        yearly4 = df.groupby("YEAR").size().reset_index()
        yearly4.columns = ["Year","Wells"]
        fig_s1 = go.Figure(go.Scatter(
            x=yearly4["Year"],y=yearly4["Wells"],
            mode="lines+markers",line=dict(color="#1F4E79",width=2.5),
            fill="tozeroy",fillcolor="rgba(31,78,121,0.08)",
            hovertemplate="<b>%{x}</b><br>Wells: %{y:,}<extra></extra>"
        ))
        fig_s1.update_layout(
            plot_bgcolor="white",paper_bgcolor="white",
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#f0f0f0",title="Wells"),
            height=300,margin=dict(t=10,b=40,l=60,r=20),
            title="Drilling Trend 1980–2025"
        )

        top10 = county_summary.head(10)
        fig_s2 = go.Figure(go.Bar(
            x=top10["Well_Count"][::-1],
            y=top10["COUNTYNAME"][::-1],
            orientation="h",
            marker_color="#2E75B6",
            hovertemplate="<b>%{y}</b><br>Wells: %{x:,}<extra></extra>"
        ))
        fig_s2.update_layout(
            plot_bgcolor="white",paper_bgcolor="white",
            xaxis=dict(showgrid=False),yaxis=dict(title=""),
            height=300,margin=dict(t=10,b=40,l=120,r=20),
            title="Top 10 Counties by Well Count"
        )

        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(fig_s1, use_container_width=True)
        with c2: st.plotly_chart(fig_s2, use_container_width=True)

        # Box plot
        box_counties = ["Tulare","Fresno","Kern","San Diego",
                        "Merced","Riverside","Kings","Madera"]
        box_df2 = df[df["COUNTYNAME"].isin(box_counties)][
            ["COUNTYNAME","TOTALDRILLDEPTH"]].dropna()
        ordered = (box_df2.groupby("COUNTYNAME")["TOTALDRILLDEPTH"]
                   .median().sort_values(ascending=False).index.tolist())
        fig_box = go.Figure()
        for county in ordered:
            data = box_df2[box_df2["COUNTYNAME"]==county]["TOTALDRILLDEPTH"]
            color = "#E24B4A" if county in ["Kern","San Diego","Tulare","Fresno"] \
                    else "#2E75B6"
            fig_box.add_trace(go.Box(
                y=data, name=county,
                marker_color=color, line_color=color, boxmean=True
            ))
        fig_box.update_layout(
            plot_bgcolor="white",paper_bgcolor="white",
            yaxis=dict(title="Drill Depth (ft)",gridcolor="#f0f0f0"),
            height=400,margin=dict(t=10,b=40,l=60,r=20),
            showlegend=False,
            title="Drill Depth Distribution by County"
        )
        st.plotly_chart(fig_box, use_container_width=True)

elif page == "🗺️ Well Map":
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0a1628,#1b7f8e);
                border-radius:16px;padding:36px;margin-bottom:24px;color:white'>
      <div style='font-size:0.8rem;opacity:0.6;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:8px'>Section 3</div>
      <div style='font-size:2rem;font-weight:700;margin-bottom:10px'>
        🗺️ 56,000 Wells Mapped Across California
      </div>
      <div style='font-size:1rem;opacity:0.85;line-height:1.7;max-width:700px'>
        Every dot is a real agriculture well with GPS coordinates from the
        state database. The heatmap shows where drilling is most concentrated.
        Switch to bubble view to compare well yields by location.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Map type selector
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        map_type = st.radio(
            "Map view",
            ["🔥 Heatmap", "🔵 Yield bubbles", "📍 County choropleth"],
            key="map_type"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        sample_size = st.slider(
            "Sample size", 1000, 10000, 5000, 500,
            help="More points = slower but more detail"
        )

    # Prepare map data
    map_df = df[
        df["DECIMALLATITUDE"].notna() &
        df["DECIMALLONGITUDE"].notna()
    ][["COUNTYNAME","YEAR","TOTALDRILLDEPTH",
       "WELLYIELD","PLANNEDUSEFORMERUSE",
       "DECIMALLATITUDE","DECIMALLONGITUDE"]].copy()

    # Fix longitude
    map_df.loc[map_df["DECIMALLONGITUDE"] > 0, "DECIMALLONGITUDE"] *= -1

    # Filter to valid CA coordinates
    map_df = map_df[
        (map_df["DECIMALLATITUDE"].between(32, 42)) &
        (map_df["DECIMALLONGITUDE"].between(-125, -114))
    ]

    sample = map_df.sample(
        min(sample_size, len(map_df)), random_state=42
    )

    st.markdown(f"<div style='font-size:0.8rem;color:#6b7280;margin-bottom:12px'>"
                f"Showing {len(sample):,} of {len(map_df):,} wells "
                f"with valid GPS coordinates</div>",
                unsafe_allow_html=True)

    # ── HEATMAP ───────────────────────────────────────────────
    if map_type == "🔥 Heatmap":
        st.markdown("""
        <div class='callout'>
          <strong>How to read this map</strong><br>
          Red/orange = highest well density. The Central Valley corridor
          from Tulare to Fresno glows brightest — confirming it as
          California's agricultural groundwater epicenter.
          Zoom in with your scroll wheel for more detail.
        </div>""", unsafe_allow_html=True)

        fig = go.Figure(go.Densitymapbox(
            lat=sample["DECIMALLATITUDE"],
            lon=sample["DECIMALLONGITUDE"],
            radius=8,
            colorscale=[
                [0.0, "rgba(31,78,121,0)"],
                [0.2, "#1F4E79"],
                [0.5, "#EF9F27"],
                [1.0, "#E24B4A"]
            ],
            showscale=True,
            colorbar=dict(title="Density", thickness=12),
            hovertemplate=(
                "Lat: %{lat:.3f}<br>"
                "Lon: %{lon:.3f}<extra></extra>"
            )
        ))
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=36.7, lon=-119.5),
                zoom=5
            ),
            margin=dict(t=0,b=0,l=0,r=0),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── YIELD BUBBLES ─────────────────────────────────────────
    elif map_type == "🔵 Yield bubbles":
        st.markdown("""
        <div class='callout green'>
          <strong>How to read this map</strong><br>
          Each bubble is a well. Size = yield (bigger = more water).
          Color = productivity tier: green ≥1,000 GPM,
          orange 300–999 GPM, red &lt;300 GPM.
          Hover over any bubble for full details.
        </div>""", unsafe_allow_html=True)

        bubble_df = sample.dropna(subset=["WELLYIELD"]).copy()
        bubble_df["color"] = bubble_df["WELLYIELD"].apply(
            lambda x: "#2D9E6B" if x >= 1000
            else "#EF9F27" if x >= 300 else "#E24B4A"
        )
        bubble_df["size"] = (
            bubble_df["WELLYIELD"] / bubble_df["WELLYIELD"].max() * 20 + 4
        ).clip(4, 24)

        fig = go.Figure(go.Scattermapbox(
            lat=bubble_df["DECIMALLATITUDE"],
            lon=bubble_df["DECIMALLONGITUDE"],
            mode="markers",
            marker=dict(
                size=bubble_df["size"],
                color=bubble_df["color"],
                opacity=0.6
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Year: %{customdata[1]}<br>"
                "Yield: %{customdata[2]:,} GPM<br>"
                "Depth: %{customdata[3]:,} ft<extra></extra>"
            ),
            customdata=bubble_df[[
                "COUNTYNAME","YEAR","WELLYIELD","TOTALDRILLDEPTH"
            ]].fillna(0).values
        ))
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=36.7, lon=-119.5),
                zoom=5
            ),
            margin=dict(t=0,b=0,l=0,r=0),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── COUNTY CHOROPLETH ─────────────────────────────────────
    else:
        st.markdown("""
        <div class='callout amber'>
          <strong>How to read this map</strong><br>
          Color intensity shows well count by county.
          Darker = more agriculture wells.
          Hover for county stats. Use the metric selector to
          switch between well count, yield, and depth.
        </div>""", unsafe_allow_html=True)

        metric_choice = st.selectbox(
            "Color by",
            ["Well Count", "Median Yield (GPM)", "Avg Drill Depth (ft)"],
            key="choropleth_metric"
        )

        metric_map = {
            "Well Count": "Well_Count",
            "Median Yield (GPM)": "Median_Yield",
            "Avg Drill Depth (ft)": "Avg_Depth"
        }
        col_name = metric_map[metric_choice]

        import urllib.request
        import json as json_lib

        # Load California counties GeoJSON
        geojson_url = (
            "https://raw.githubusercontent.com/codeforamerica/"
            "click_that_hood/master/public/data/california-counties.geojson"
        )
        try:
            import requests
            response = requests.get(geojson_url, verify=False)
            ca_geojson = json_lib.loads(response.text)  

            # Match county names
            choro_df = county_summary[[
                "COUNTYNAME","Well_Count","Median_Yield","Avg_Depth"
            ]].copy()
            choro_df.columns = [
                "County","Well Count","Median Yield (GPM)","Avg Drill Depth (ft)"
            ]

            fig = px.choropleth_mapbox(
                choro_df,
                geojson=ca_geojson,
                locations="County",
                featureidkey="properties.name",
                color=metric_choice,
                color_continuous_scale="Blues",
                mapbox_style="carto-positron",
                zoom=5,
                center=dict(lat=36.7, lon=-119.5),
                opacity=0.7,
                hover_data={
                    "County":True,
                    "Well Count":True,
                    "Median Yield (GPM)":True,
                    "Avg Drill Depth (ft)":True
                }
            )
            fig.update_layout(
                margin=dict(t=0,b=0,l=0,r=0),
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.warning(f"Could not load county boundaries: {e}")
            st.info("Try the Heatmap or Yield Bubbles view instead — "
                    "those work without an internet connection.")

    # Map stats below
    st.markdown("---")
    st.markdown("### 📊 Map Statistics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Wells with GPS", f"{len(map_df):,}")
    with c2:
        st.metric("Coverage", f"{len(map_df)/len(df)*100:.0f}%")
    with c3:
        st.metric("Northernmost county",
                  df.loc[df["DECIMALLATITUDE"].idxmax(), "COUNTYNAME"]
                  if df["DECIMALLATITUDE"].notna().any() else "—")
    with c4:
        st.metric("Southernmost county",
                  df.loc[df["DECIMALLATITUDE"].idxmin(), "COUNTYNAME"]
                  if df["DECIMALLATITUDE"].notna().any() else "—")

elif page == "🔍 County Deep Dive":
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a2e1a,#2d6a4f);
                border-radius:16px;padding:36px;margin-bottom:24px;color:white'>
      <div style='font-size:0.8rem;opacity:0.6;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:8px'>Section 4</div>
      <div style='font-size:2rem;font-weight:700;margin-bottom:10px'>
        🔍 County Deep Dive
      </div>
      <div style='font-size:1rem;opacity:0.85;line-height:1.7;max-width:700px'>
        Select any California county to see its complete groundwater profile —
        drilling trends, yield distribution, depth analysis, and a plain-English
        interpretation of what the data means.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # County selector
    all_c = sorted(df["COUNTYNAME"].dropna().unique().tolist())
    selected_county = st.selectbox(
        "Choose a county to explore",
        all_c, key="deep_dive_county",
        index=all_c.index("Fresno") if "Fresno" in all_c else 0
    )

    cdf = df[df["COUNTYNAME"] == selected_county].copy()

    if len(cdf) == 0:
        st.warning("No data available for this county.")
    else:
        # ── KPI ROW ───────────────────────────────────────────
        c_wells  = len(cdf)
        c_yield  = cdf["WELLYIELD"].median()
        c_depth  = cdf["TOTALDRILLDEPTH"].mean()
        c_swl    = cdf["STATICWATERLEVEL"].mean()
        c_peak   = int(cdf.groupby("YEAR").size().idxmax())
        state_yield = df["WELLYIELD"].median()
        state_depth = df["TOTALDRILLDEPTH"].mean()

        k1,k2,k3,k4,k5 = st.columns(5)
        metrics = [
            (k1, f"{c_wells:,}", "Total wells",
             f"{'Top 5' if c_wells > 2000 else 'Active'} county", "teal"),
            (k2, f"{int(c_yield):,} GPM" if not pd.isna(c_yield) else "—",
             "Median yield",
             f"State median: {int(state_yield):,} GPM",
             "green" if not pd.isna(c_yield) and c_yield >= state_yield else "red"),
            (k3, f"{int(c_depth):,} ft" if not pd.isna(c_depth) else "—",
             "Avg drill depth",
             f"State avg: {int(state_depth):,} ft",
             "amber" if not pd.isna(c_depth) and c_depth > state_depth else "teal"),
            (k4, f"{int(c_swl):,} ft" if not pd.isna(c_swl) else "—",
             "Avg water table", "depth below surface", "teal"),
            (k5, str(c_peak), "Most active year",
             "peak drilling year", "teal"),
        ]
        for col, val, lbl, note, color in metrics:
            with col:
                st.markdown(f"""
                <div class='kpi-card {color}'>
                  <div class='kpi-val'>{val}</div>
                  <div class='kpi-lbl'>{lbl}</div>
                  <div class='kpi-note'>{note}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── BUSINESS INTERPRETATION ───────────────────────────
        if not pd.isna(c_yield) and not pd.isna(c_depth):
            if c_yield >= 1000 and c_depth < 600:
                interp = (f"✅ **Strong investment profile.** {selected_county} "
                          f"delivers {int(c_yield):,} GPM at a moderate average "
                          f"depth of {int(c_depth):,} ft. Productive confined "
                          f"aquifer geology with reasonable drilling costs.")
                interp_color = "#f0faf5"
                interp_border = "#2D9E6B"
            elif c_yield >= 1000 and c_depth >= 600:
                interp = (f"⚠️ **High yield, high cost.** {selected_county} "
                          f"achieves {int(c_yield):,} GPM but requires deep "
                          f"drilling to {int(c_depth):,} ft average. Productive "
                          f"today but high capital cost and long-term depletion risk.")
                interp_color = "#fffbf0"
                interp_border = "#EF9F27"
            elif c_yield < 300 and c_wells > 1500:
                interp = (f"🔴 **Overdraft signal.** {selected_county} has "
                          f"{c_wells:,} wells but only {int(c_yield):,} GPM "
                          f"median yield. High density + low yield = classic "
                          f"aquifer depletion. Each new well competes with "
                          f"existing ones for diminishing water.")
                interp_color = "#fff5f5"
                interp_border = "#E24B4A"
            else:
                interp = (f"📊 **Mid-range county.** {selected_county} shows "
                          f"{int(c_yield):,} GPM median yield at {int(c_depth):,} "
                          f"ft average depth. Monitor water table trends and "
                          f"SGMA basin designations for long-term planning.")
                interp_color = "#f0f9fb"
                interp_border = "#1b7f8e"

            st.markdown(f"""
            <div style='background:{interp_color};border-left:4px solid {interp_border};
                        border-radius:0 8px 8px 0;padding:16px 20px;
                        margin-bottom:20px;font-size:0.95rem;line-height:1.7'>
              {interp}
            </div>""", unsafe_allow_html=True)

        # ── TWO CHARTS SIDE BY SIDE ───────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Drilling trend — {selected_county} County**")
            yearly_c = cdf.groupby("YEAR").size().reset_index()
            yearly_c.columns = ["Year","Wells"]
            fig_ct = go.Figure(go.Bar(
                x=yearly_c["Year"], y=yearly_c["Wells"],
                marker_color="#1F4E79",
                hovertemplate="<b>%{x}</b><br>Wells: %{y:,}<extra></extra>"
            ))
            fig_ct.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#f0f0f0", title="Wells"),
                height=320, margin=dict(t=10,b=40,l=50,r=20)
            )
            st.plotly_chart(fig_ct, use_container_width=True)

        with col2:
            st.markdown(f"**Well yield distribution — {selected_county} County**")
            yield_data = cdf["WELLYIELD"].dropna()
            if len(yield_data) > 0:
                fig_yh = go.Figure(go.Histogram(
                    x=yield_data,
                    nbinsx=30,
                    marker_color="#2D9E6B",
                    opacity=0.8,
                    hovertemplate="Yield: %{x:,} GPM<br>Count: %{y}<extra></extra>"
                ))
                fig_yh.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    xaxis=dict(title="Well Yield (GPM)", showgrid=False),
                    yaxis=dict(title="Number of wells", gridcolor="#f0f0f0"),
                    height=320, margin=dict(t=10,b=40,l=50,r=20)
                )
                st.plotly_chart(fig_yh, use_container_width=True)
            else:
                st.info("No yield data available for this county.")

        # ── DEPTH TREND ───────────────────────────────────────
        st.markdown(f"**Median drill depth over time — {selected_county} County**")
        depth_trend_c = cdf.groupby("YEAR")["TOTALDRILLDEPTH"].median().reset_index()
        fig_dtc = go.Figure(go.Scatter(
            x=depth_trend_c["YEAR"],
            y=depth_trend_c["TOTALDRILLDEPTH"],
            mode="lines+markers",
            line=dict(color="#854F0B", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(133,79,11,0.08)",
            hovertemplate="<b>%{x}</b><br>Median depth: %{y:,.0f} ft<extra></extra>"
        ))
        # Add state average reference line
        state_avg_depth = df.groupby("YEAR")["TOTALDRILLDEPTH"].median()
        fig_dtc.add_trace(go.Scatter(
            x=state_avg_depth.index,
            y=state_avg_depth.values,
            mode="lines",
            line=dict(color="#6b7280", width=1.5, dash="dot"),
            name="State median",
            hovertemplate="State median: %{y:,.0f} ft<extra></extra>"
        ))
        fig_dtc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Year", showgrid=False, range=[1980,2025]),
            yaxis=dict(title="Median Drill Depth (ft)", gridcolor="#f0f0f0"),
            height=350, margin=dict(t=10,b=40,l=60,r=20),
            legend=dict(x=0.02, y=0.98)
        )
        st.plotly_chart(fig_dtc, use_container_width=True)
        # ── BOX & WHISKER ─────────────────────────────────────
        st.markdown("### 📦 Drill Depth Distribution — Top Counties vs State")
        st.markdown("""
        <div class='section-sub'>
        Box shows the middle 50% of wells. Line inside = median.
        Dots above = outliers. Compare this county against its neighbors.
        </div>""", unsafe_allow_html=True)

        box_counties_list = county_summary.head(8)["COUNTYNAME"].tolist()
        if selected_county not in box_counties_list:
            box_counties_list[-1] = selected_county

        box_plot_df = df[df["COUNTYNAME"].isin(box_counties_list)][
            ["COUNTYNAME","TOTALDRILLDEPTH"]
        ].dropna()

        ordered_box = (box_plot_df.groupby("COUNTYNAME")["TOTALDRILLDEPTH"]
                       .median().sort_values(ascending=False).index.tolist())

        fig_bw = go.Figure()
        for county in ordered_box:
            data = box_plot_df[
                box_plot_df["COUNTYNAME"]==county
            ]["TOTALDRILLDEPTH"]
            is_selected = county == selected_county
            color = "#28b5c8" if is_selected else "#2E75B6"
            fig_bw.add_trace(go.Box(
                y=data,
                name=county,
                marker_color=color,
                line_color=color,
                boxmean=True,
                marker=dict(
                    outliercolor=color,
                    size=3,
                    opacity=0.4
                ),
                hovertemplate=(
                    f"<b>{county}</b><br>"
                    "Depth: %{y:,} ft<extra></extra>"
                )
            ))
        fig_bw.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(
                title="Total Drill Depth (ft)",
                gridcolor="#f0f0f0"
            ),
            xaxis=dict(title="County"),
            height=420,
            margin=dict(t=10,b=60,l=60,r=20),
            showlegend=False,
            annotations=[dict(
                x=selected_county,
                y=box_plot_df[
                    box_plot_df["COUNTYNAME"]==selected_county
                ]["TOTALDRILLDEPTH"].median(),
                text="← Selected",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#28b5c8",
                font=dict(color="#28b5c8", size=11),
                ax=60, ay=-30
            )]
        )
        st.plotly_chart(fig_bw, use_container_width=True)
        st.markdown("""
        <div class='callout'>
          <strong>How to read this chart</strong><br>
          The box shows where the middle 50% of wells fall for each county.
          The line inside is the median depth. The dots above are outliers —
          individual wells that drilled to unusual depths. A tall box means
          huge variation in drilling depth across that county.
          The highlighted county is the one you selected above.
        </div>""", unsafe_allow_html=True)

        # ── COMPARISON TABLE ──────────────────────────────────
        st.markdown("### How does this county compare?")
        compare = county_summary.head(15)[[
            "COUNTYNAME","Well_Count","Median_Yield","Avg_Depth"
        ]].copy()
        compare.columns = ["County","Wells","Median Yield (GPM)","Avg Depth (ft)"]
        compare["Selected"] = compare["County"].apply(
            lambda x: "⭐ You" if x == selected_county else ""
        )
        st.dataframe(
            compare.set_index("County"),
            use_container_width=True,
            height=400
        )

elif page == "📋 Data Explorer":
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a1a2e,#2d2d5e);
                border-radius:16px;padding:36px;margin-bottom:24px;color:white'>
      <div style='font-size:0.8rem;opacity:0.6;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:8px'>Section 5</div>
      <div style='font-size:2rem;font-weight:700;margin-bottom:10px'>
        📋 Data Explorer
      </div>
      <div style='font-size:1rem;opacity:0.85;line-height:1.7;max-width:700px'>
        Filter, search, and explore the cleaned dataset.
        Use the controls below to narrow down to exactly the wells you care about.
        Download any filtered view as a CSV.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FILTERS ROW ───────────────────────────────────────────
    st.markdown("### 🎛️ Filter the Data")
    f1, f2, f3 = st.columns(3)

    with f1:
        county_opts = ["All counties"] + sorted(
            df["COUNTYNAME"].dropna().unique().tolist()
        )
        selected_c = st.selectbox("County", county_opts, key="exp_county")

    with f2:
        use_opts = ["All uses"] + sorted(
            df["PLANNEDUSEFORMERUSE"].dropna().unique().tolist()
        )
        selected_use = st.selectbox("Well use type", use_opts, key="exp_use")

    with f3:
        year_opts = ["All years"] + sorted(
            df["YEAR"].dropna().astype(int).unique().tolist(), reverse=True
        )
        selected_year = st.selectbox("Year", year_opts, key="exp_year")

    f4, f5 = st.columns(2)
    with f4:
        yield_min, yield_max = st.slider(
            "Well yield range (GPM)",
            0, int(df["WELLYIELD"].max()),
            (0, int(df["WELLYIELD"].max())),
            key="exp_yield"
        )
    with f5:
        depth_min_e, depth_max_e = st.slider(
            "Drill depth range (ft)",
            0, int(df["TOTALDRILLDEPTH"].max()),
            (0, int(df["TOTALDRILLDEPTH"].max())),
            key="exp_depth"
        )

    # ── APPLY FILTERS ─────────────────────────────────────────
    exp_df = df.copy()
    if selected_c != "All counties":
        exp_df = exp_df[exp_df["COUNTYNAME"] == selected_c]
    if selected_use != "All uses":
        exp_df = exp_df[exp_df["PLANNEDUSEFORMERUSE"] == selected_use]
    if selected_year != "All years":
        exp_df = exp_df[exp_df["YEAR"] == int(selected_year)]
    exp_df = exp_df[
        (exp_df["WELLYIELD"].isna()) |
        (exp_df["WELLYIELD"].between(yield_min, yield_max))
    ]
    exp_df = exp_df[
        (exp_df["TOTALDRILLDEPTH"].isna()) |
        (exp_df["TOTALDRILLDEPTH"].between(depth_min_e, depth_max_e))
    ]

    # ── RESULTS SUMMARY ───────────────────────────────────────
    st.markdown("---")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Records matching filters", f"{len(exp_df):,}")
    with r2:
        st.metric("Counties represented",
                  str(exp_df["COUNTYNAME"].nunique()))
    with r3:
        med_y = exp_df["WELLYIELD"].median()
        st.metric("Median yield",
                  f"{int(med_y):,} GPM" if not pd.isna(med_y) else "—")
    with r4:
        med_d = exp_df["TOTALDRILLDEPTH"].median()
        st.metric("Median depth",
                  f"{int(med_d):,} ft" if not pd.isna(med_d) else "—")

    st.markdown("---")

    # ── QUICK CHARTS ──────────────────────────────────────────
    if len(exp_df) > 0:
        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown("**Records by county (top 10)**")
            top_c = exp_df["COUNTYNAME"].value_counts().head(10).reset_index()
            top_c.columns = ["County","Count"]
            fig_ec = go.Figure(go.Bar(
                x=top_c["Count"][::-1],
                y=top_c["County"][::-1],
                orientation="h",
                marker_color="#1F4E79",
                hovertemplate="<b>%{y}</b><br>%{x:,} records<extra></extra>"
            ))
            fig_ec.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(title=""),
                height=320, margin=dict(t=10,b=30,l=120,r=20)
            )
            st.plotly_chart(fig_ec, use_container_width=True)

        with ch2:
            st.markdown("**Records by year**")
            yr_c = exp_df.groupby("YEAR").size().reset_index()
            yr_c.columns = ["Year","Count"]
            fig_ey = go.Figure(go.Scatter(
                x=yr_c["Year"], y=yr_c["Count"],
                mode="lines",
                line=dict(color="#2D9E6B", width=2),
                fill="tozeroy",
                fillcolor="rgba(45,158,107,0.1)",
                hovertemplate="<b>%{x}</b><br>%{y:,} records<extra></extra>"
            ))
            fig_ey.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#f0f0f0", title="Records"),
                height=320, margin=dict(t=10,b=30,l=50,r=20)
            )
            st.plotly_chart(fig_ey, use_container_width=True)

    # ── DATA TABLE ────────────────────────────────────────────
    st.markdown("### 📄 Records")
    display_cols = [
        "COUNTYNAME","YEAR","PLANNEDUSEFORMERUSE",
        "TOTALDRILLDEPTH","WELLYIELD",
        "STATICWATERLEVEL","CITY"
    ]
    display_df = exp_df[display_cols].copy()
    display_df.columns = [
        "County","Year","Use Type",
        "Drill Depth (ft)","Yield (GPM)",
        "Water Table (ft)","City"
    ]
    display_df = display_df.head(500)

    st.markdown(f"<div style='font-size:0.8rem;color:#6b7280;margin-bottom:8px'>"
                f"Showing first 500 of {len(exp_df):,} matching records</div>",
                unsafe_allow_html=True)

    st.dataframe(display_df, use_container_width=True, height=400)

    # ── DOWNLOAD ──────────────────────────────────────────────
    st.markdown("### 💾 Download")
    csv_data = exp_df[display_cols].copy()
    csv_data.columns = [
        "County","Year","Use Type",
        "Drill Depth (ft)","Yield (GPM)",
        "Water Table (ft)","City"
    ]
    csv_string = csv_data.to_csv(index=False)

    st.download_button(
        label=f"⬇️ Download filtered dataset ({len(exp_df):,} records) as CSV",
        data=csv_string,
        file_name="groundwater_intel_filtered.csv",
        mime="text/csv"
    )
    st.markdown("""
    <div style='font-size:0.78rem;color:#9ca3af;margin-top:8px'>
      Downloaded file contains all columns from the cleaned dataset
      matching your current filter selections.
    </div>""", unsafe_allow_html=True)

elif page == "⚗️ Methods":
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0a1628,#0d2b55);
                border-radius:16px;padding:36px;margin-bottom:24px;color:white'>
      <div style='font-size:0.8rem;opacity:0.6;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:8px'>Section 6</div>
      <div style='font-size:2rem;font-weight:700;margin-bottom:10px'>
        ⚗️ Methods & Data Quality
      </div>
      <div style='font-size:1rem;opacity:0.85;line-height:1.7;max-width:700px'>
        How we built this analysis — from a 1.1 million row government
        database to a cleaned, filtered, interactive dashboard.
        Every cleaning decision is documented here.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── THE PIPELINE ──────────────────────────────────────────
    st.markdown("### 🔧 The Data Pipeline")

    steps = [
        ("1", "Source Data", "#1b7f8e",
         "California SWRCB",
         "Downloaded the Well Completion Reports CSV from the California "
         "Natural Resources Agency open data portal. The file contains "
         "every well completion report filed in California since records began.",
         "1,103,910 rows · 45 columns"),
        ("2", "Agriculture Filter", "#2D9E6B",
         "pandas · Python",
         "Filtered to rows where PLANNEDUSEFORMERUSE contains "
         "'Irrigation - Agriculture' or 'Stock or Animal Watering'. "
         "This isolates wells drilled specifically for agricultural purposes "
         "from the broader dataset which includes domestic, industrial, "
         "and monitoring wells.",
         "102,327 rows retained"),
        ("3", "Date Cleaning", "#EF9F27",
         "pandas · datetime",
         "Converted DATEWORKENDED to proper datetime format. Removed records "
         "outside 1980–2025. This eliminated 742 records with year 1776 "
         "(a clear placeholder/default value), records dated to 9999, "
         "and future dates that represent data entry errors.",
         "58,646 analysis-ready rows"),
        ("4", "Outlier Capping", "#E24B4A",
         "numpy · quantiles",
         "Capped extreme values at the 99th percentile for TOTALDRILLDEPTH, "
         "TOTALCOMPLETEDDEPTH, STATICWATERLEVEL, and WELLYIELD. One record "
         "showed a drill depth of 824,824 ft — 156 miles underground — "
         "which would have destroyed every average and chart in the analysis.",
         "99th percentile caps applied"),
        ("5", "Coordinate Fix", "#854F0B",
         "pandas · GPS",
         "Some longitude values were stored as positive numbers when they "
         "should be negative (California is in the western hemisphere). "
         "Fixed by multiplying positive longitude values by -1. "
         "Filtered to valid California coordinate bounds.",
         "56,652 wells with valid GPS"),
    ]

    for num, title, color, tool, desc, result in steps:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"""
            <div style='background:{color};border-radius:12px;padding:20px;
                        text-align:center;color:white;height:100%'>
              <div style='font-size:2rem;font-weight:700'>{num}</div>
              <div style='font-size:0.85rem;font-weight:600;margin-top:4px'>
                {title}
              </div>
              <div style='font-size:0.75rem;opacity:0.8;margin-top:4px'>
                {tool}
              </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style='background:white;border-radius:12px;padding:20px;
                        border-left:4px solid {color};
                        box-shadow:0 1px 8px rgba(0,0,0,0.06);height:100%'>
              <div style='font-size:0.95rem;color:#374151;
                          line-height:1.7;margin-bottom:10px'>
                {desc}
              </div>
              <div style='font-size:0.8rem;font-weight:600;
                          color:{color};background:{color}18;
                          display:inline-block;padding:4px 12px;
                          border-radius:20px'>
                ✓ {result}
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── DATA QUALITY ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚠️ Data Quality & Limitations")

    limitations = [
        ("WELLYIELD missing ~65%",
         "Well yield is the most analytically important column but is "
         "missing for roughly 65% of records. Drillers are not always "
         "required to conduct pump tests, so many completions have no "
         "yield data. All yield statistics use only available data — "
         "sample sizes are smaller than total record counts.",
         "#E24B4A"),
        ("TOTALDRILLDEPTH missing ~80%",
         "Drill depth is missing for approximately 80% of records. "
         "This is common for older records and for well types where "
         "depth was not consistently recorded. Depth averages and trends "
         "reflect available data only and may not represent the full population.",
         "#EF9F27"),
        ("RECEIVEDDATE not used for trends",
         "RECEIVEDDATE (when the report was submitted) was intentionally "
         "excluded from time-trend analysis. Investigation revealed that "
         "88,000+ records show a 2025 received date — consistent with a "
         "bulk digitization upload of historical paper records. "
         "DATEWORKENDED (when the actual work was completed) is used instead.",
         "#1b7f8e"),
        ("GPS coordinate accuracy",
         "The majority of well completion reports have been spatially "
         "registered to the center of the 1×1 mile Public Land Survey System "
         "section — not the exact well location. GPS coordinates are "
         "approximate and suitable for county-level mapping but not "
         "for precise site analysis.",
         "#854F0B"),
        ("Interpretation caution",
         "Median values are used throughout (not means) to reduce distortion "
         "from remaining outliers. County-level statistics reflect available "
         "data only. Yield and depth comparisons should account for underlying "
         "geology — not just regulation or farming practice.",
         "#6b7280"),
    ]

    for title, desc, color in limitations:
        st.markdown(f"""
        <div style='background:white;border-radius:12px;padding:20px 24px;
                    border-left:4px solid {color};
                    box-shadow:0 1px 8px rgba(0,0,0,0.06);margin-bottom:12px'>
          <div style='font-size:0.95rem;font-weight:600;color:#0a1628;
                      margin-bottom:6px'>{title}</div>
          <div style='font-size:0.88rem;color:#555;line-height:1.7'>{desc}</div>
        </div>""", unsafe_allow_html=True)

    # ── DATASET SNAPSHOT ──────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Dataset Snapshot")

    snap_col1, snap_col2 = st.columns(2)
    with snap_col1:
        st.markdown("""
        <div style='background:white;border-radius:12px;padding:24px;
                    box-shadow:0 1px 8px rgba(0,0,0,0.06)'>
          <div style='font-size:1rem;font-weight:700;color:#0a1628;
                      margin-bottom:16px'>Record counts at each stage</div>
        """, unsafe_allow_html=True)

        stages = [
            ("Original dataset", "1,103,910", "#6b7280"),
            ("After ag filter", "102,327", "#1b7f8e"),
            ("After date cleaning", "58,646", "#2D9E6B"),
            ("With GPS coordinates", "56,652", "#2D9E6B"),
            ("With yield data", f"{df['WELLYIELD'].notna().sum():,}", "#EF9F27"),
            ("With depth data",
             f"{df['TOTALDRILLDEPTH'].notna().sum():,}", "#EF9F27"),
        ]
        for label, value, color in stages:
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;
                        align-items:center;padding:8px 0;
                        border-bottom:1px solid #f0f0f0'>
              <span style='font-size:0.88rem;color:#374151'>{label}</span>
              <span style='font-size:0.95rem;font-weight:700;
                           color:{color}'>{value}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with snap_col2:
        st.markdown("""
        <div style='background:white;border-radius:12px;padding:24px;
                    box-shadow:0 1px 8px rgba(0,0,0,0.06)'>
          <div style='font-size:1rem;font-weight:700;color:#0a1628;
                      margin-bottom:16px'>Tools & technologies</div>
        """, unsafe_allow_html=True)

        tools = [
            ("Python 3.14", "Core programming language", "#1b7f8e"),
            ("pandas", "Data loading, cleaning, filtering", "#2D9E6B"),
            ("Streamlit", "Interactive web dashboard", "#E24B4A"),
            ("Plotly", "Interactive charts and maps", "#EF9F27"),
            ("VS Code", "Development environment", "#854F0B"),
            ("California DWR", "Live data source (OSWCR)", "#6b7280"),
        ]
        for tool, desc, color in tools:
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;
                        align-items:center;padding:8px 0;
                        border-bottom:1px solid #f0f0f0'>
              <div>
                <span style='font-size:0.9rem;font-weight:600;
                             color:#0a1628'>{tool}</span>
                <span style='font-size:0.78rem;color:#9ca3af;
                             margin-left:8px'>{desc}</span>
              </div>
              <div style='width:10px;height:10px;border-radius:50%;
                          background:{color};flex-shrink:0'></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── CITATION ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style='background:#f8fafc;border-radius:12px;padding:20px 24px;
                border:1px solid #e2e8f0;font-size:0.85rem;color:#555;
                line-height:1.7'>
      <strong style='color:#0a1628'>Data Citation</strong><br>
      California Department of Water Resources (DWR). Online System for
      Well Completion Reports (OSWCR). California Natural Resources Agency
      Open Data Portal. Retrieved May 2026.<br>
      URL: data.cnra.ca.gov/dataset/well-completion-reports<br><br>
      <strong style='color:#0a1628'>Project</strong><br>
      AGB 470 · Agribusiness Management · Cal Poly San Luis Obispo · May 2026<br>
      Built with Python, pandas, Streamlit, and Plotly.
    </div>
    """, unsafe_allow_html=True)
