import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# หน้าตาเบื้องต้น
# =========================================================
st.set_page_config(
    page_title="Busy Buffet Dashboard",
    layout="wide"
)

# =========================================================
# ตกแต่ง CSS
# =========================================================
st.markdown("""
<style>
.insight-box {
    background-color: #1a2a3a;
    border-left: 4px solid #5B8DEF;
    padding: 12px 16px;
    border-radius: 6px;
    margin-top: 8px;
    font-size: 0.9rem;
    line-height: 1.6;
}
.confirm-box {
    background-color: #0d2b1a;
    border-left: 4px solid #2ecc71;
    padding: 12px 16px;
    border-radius: 6px;
    margin-top: 8px;
    font-size: 0.9rem;
    line-height: 1.6;
}
.disprove-box {
    background-color: #2b1a0d;
    border-left: 4px solid #FF8C42;
    padding: 12px 16px;
    border-radius: 6px;
    margin-top: 8px;
    font-size: 0.9rem;
    line-height: 1.6;
}
.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("busy_buffet_clean.csv")
    datetime_cols = ["date", "queue_start_dt", "queue_end_dt", "meal_start_dt", "meal_end_dt"]
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df["meal_hour"] = df["meal_start_dt"].dt.hour
    df["day_type"] = df["is_weekend"].map({True: "Weekend", False: "Weekday"})
    df["revenue"] = df["party_size"] * df["price"]
    return df

df = load_data()

# =========================================================
# Sidebar / กรองข้อมูล
# =========================================================
st.sidebar.title("Busy Buffet")
st.sidebar.caption("Careers Atmind Group")

date_options = sorted(df["date"].dt.date.dropna().unique())
selected_dates = st.sidebar.multiselect("Select Dates", options=date_options, default=date_options)
if selected_dates:
    df = df[df["date"].dt.date.isin(selected_dates)]

guest_options = sorted(df["guest_type"].dropna().unique())
selected_guest = st.sidebar.multiselect("Guest Type", options=guest_options, default=guest_options)
if selected_guest:
    df = df[df["guest_type"].isin(selected_guest)]

st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("""
- [Overview](#overview)
- [Task 1: Staff Comments](#task-1-staff-comments)
- [Task 2: Why Actions Won't Work](#task-2-why-actions-won-t-work)
- [Task 3: Recommendation](#task-3-recommendation)
""")

# =========================================================
# Title
# =========================================================
st.title("Busy Buffet")

# =========================================================
# KPI ด้านบน
# =========================================================
total_groups = len(df)
total_pax    = df["party_size"].sum()
walkaways    = df["is_walkaway"].sum()
avg_wait     = df["wait_min"].mean()
avg_meal     = df["meal_min"].mean()
total_revenue = df["revenue"].sum()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Groups",  f"{int(total_groups):,}")
c2.metric("Pax Served",    f"{int(total_pax):,}")
c3.metric("Walkaways",     f"{int(walkaways)}")
c4.metric("Avg Wait",      f"{avg_wait:.0f} min"  if pd.notna(avg_wait) else "N/A")
c5.metric("Avg Meal",      f"{avg_meal:.0f} min"  if pd.notna(avg_meal) else "N/A")
c6.metric("Revenue (฿)",   f"{total_revenue:,.0f}")

st.markdown("---")

# =========================================================
# SECTION: TASK 1 — STAFF COMMENTS
# =========================================================
st.markdown('<p class="section-label">Task 1 — Verify Staff Comments</p>', unsafe_allow_html=True)
st.header("Staff Comments — True or False?")
st.markdown("""
ทีมงาน ให้ความเห็น 3 ข้อเกี่ยวกับปัญหาที่เกิดขึ้น
จะใช้ข้อมูลจริงพิสูจน์ว่าแต่ละข้อเป็นความจริงหรือไม่
""")

# ── Comment 1: In-House รอ + Walk-In ออกจากคิว ──
st.subheader("Comment 1: In-House ต้องรอโต๊ะ, Walk-In รอนานแล้วออกจากคิว")

col1, col2 = st.columns(2)

with col1:
    # Wait time comparison
    wait_guest = df.groupby("guest_type", as_index=False)["wait_min"].mean().dropna()
    fig_wait = px.bar(
        wait_guest, x="guest_type", y="wait_min", text="wait_min",
        color="guest_type",
        color_discrete_map={"In-House": "#5B8DEF", "Walk-In": "#FF8C42"}
    )
    fig_wait.update_traces(texttemplate="%{text:.1f} min", textposition="outside")
    fig_wait.update_layout(
        template="plotly_dark", title="Average Wait Time by Guest Type",
        xaxis_title="Guest Type", yaxis_title="Minutes", showlegend=False, height=380
    )
    st.plotly_chart(fig_wait, use_container_width=True)

with col2:
    # Walkaway count by guest type
    wa_df = df.groupby("guest_type")["is_walkaway"].sum().reset_index()
    wa_df.columns = ["guest_type", "walkaways"]
    fig_wa = px.bar(
        wa_df, x="guest_type", y="walkaways", text="walkaways",
        color="guest_type",
        color_discrete_map={"In-House": "#5B8DEF", "Walk-In": "#FF8C42"}
    )
    fig_wa.update_traces(textposition="outside")
    fig_wa.update_layout(
        template="plotly_dark", title="Walk-Away Count by Guest Type",
        xaxis_title="Guest Type", yaxis_title="Groups", showlegend=False, height=380
    )
    st.plotly_chart(fig_wa, use_container_width=True)

total_wa   = int(df["is_walkaway"].sum())
wi_wa      = int(df[df["guest_type"] == "Walk-In"]["is_walkaway"].sum())
ih_wa      = int(df[df["guest_type"] == "In-House"]["is_walkaway"].sum())
wi_wait    = df[df["guest_type"] == "Walk-In"]["wait_min"].mean()
ih_wait    = df[df["guest_type"] == "In-House"]["wait_min"].mean()

st.markdown(f"""
<div class="confirm-box">
✅ <strong>DATA SUGGESTS — ทั้ง In-House และ Walk-In ได้รับผลกระทบจาก queue</strong><br><br>

<strong>What we see:</strong><br>
• Walk-In wait = <strong>{wi_wait:.1f} min</strong> vs In-House = <strong>{ih_wait:.1f} min</strong><br>
• Total walkaways = <strong>{total_wa}</strong> กลุ่ม ({wi_wa} Walk-In, {ih_wa} In-House)<br><br>

<strong>Interpretation:</strong><br>
• Walk-In มี wait time สูงกว่าโดยเฉลี่ย แสดงว่ากลุ่มนี้ได้รับผลกระทบจาก queue มากกว่า<br><br>

<strong>Implication:</strong><br>
• Queue มีผลต่อทั้งสองกลุ่ม และนำไปสู่การสูญเสียรายได้ (lost revenue)<br>
• แม้ In-House จะรอสั้นกว่า แต่การที่ลูกค้าต้องรอในโรงแรมตัวเอง อาจกระทบ service experience
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Comment 2: ลูกค้าเยอะต่อเนื่องทุกวัน
st.subheader("Comment 2: ลูกค้าเยอะต่อเนื่องทุกวัน")

daily = df[df["had_meal"] == True].groupby("date").agg(
    pax=("party_size", "sum"),
    groups=("service_no", "count")
).reset_index()
daily["date_str"] = daily["date"].dt.strftime("%b %d (%a)")

col3, col4 = st.columns(2)
with col3:
    fig_daily_pax = px.bar(
        daily, x="date_str", y="pax", text="pax",
        color_discrete_sequence=["#5B8DEF"]
    )
    fig_daily_pax.update_traces(textposition="outside")
    fig_daily_pax.update_layout(
        template="plotly_dark", title="Total Pax Served per Day",
        xaxis_title="Date", yaxis_title="Pax", height=380
    )
    st.plotly_chart(fig_daily_pax, use_container_width=True)

with col4:
    fig_daily_grp = px.bar(
        daily, x="date_str", y="groups", text="groups",
        color_discrete_sequence=["#FF8C42"]
    )
    fig_daily_grp.update_traces(textposition="outside")
    fig_daily_grp.update_layout(
        template="plotly_dark", title="Total Groups per Day",
        xaxis_title="Date", yaxis_title="Groups", height=380
    )
    st.plotly_chart(fig_daily_grp, use_container_width=True)

avg_pax_day    = daily["pax"].mean()
min_pax_day    = daily["pax"].min()
max_pax_day    = daily["pax"].max()

st.markdown(f"""
<div class="confirm-box">
✅ <strong>จากข้อมูล — ร้านมีลูกค้าเยอะทุกวัน และแทบไม่มีวันที่ลูกค้าน้อย</strong><br><br>

<strong>What we see:</strong><br>
• Pax ต่อวันอยู่ที่ <strong>{int(min_pax_day)}–{int(max_pax_day)} คน</strong> (เฉลี่ย <strong>{avg_pax_day:.0f} คน/วัน</strong>)<br>
• ทั้ง weekday และ weekend มีจำนวนลูกค้าใกล้เคียงกัน<br><br>

<strong>Interpretation:</strong><br>
• ร้านมี demand สูงต่อเนื่อง ไม่ได้พีคแค่บางวัน<br><br>

<strong>So what?</strong><br>
• ถ้าไม่จัดการเพิ่ม อาจทำให้ staff เหนื่อยสะสม และระบบไม่ยั่งยืน
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Comment 3: Walk-In นั่งทั้งวัน ──
st.subheader("Comment 3: Walk-In นั่งทั้งวัน ทำให้หาที่นั่ง In-House ไม่ได้")

meal_df = df[df["meal_min"].notna() & (df["meal_min"] > 0)].copy()

# Single focused chart: Median meal duration by guest type
med_df = meal_df.groupby("guest_type", as_index=False)["meal_min"].median()
med_df.columns = ["guest_type", "median_meal"]
fig_med = px.bar(
    med_df, x="guest_type", y="median_meal", text="median_meal",
    color="guest_type",
    color_discrete_map={"In-House": "#5B8DEF", "Walk-In": "#FF8C42"}
)
fig_med.update_traces(texttemplate="%{text:.0f} min", textposition="outside")
fig_med.update_layout(
    template="plotly_dark", title="Median Meal Duration by Guest Type",
    xaxis_title="Guest Type", yaxis_title="Minutes", showlegend=False, height=380
)
st.plotly_chart(fig_med, use_container_width=True)

ih_med = meal_df[meal_df["guest_type"] == "In-House"]["meal_min"].median()
wi_med = meal_df[meal_df["guest_type"] == "Walk-In"]["meal_min"].median()
wi_over90 = (meal_df[meal_df["guest_type"] == "Walk-In"]["meal_min"] > 90).mean() * 100
ih_over90 = (meal_df[meal_df["guest_type"] == "In-House"]["meal_min"] > 90).mean() * 100

st.markdown(f"""
<div class="confirm-box">
✅ <strong>จากข้อมูล — ลูกค้า Walk-In นั่งนานกว่าลูกค้า In-House </strong><br><br>

<strong>What we see:</strong><br>
• Median meal time: Walk-In = <strong>{wi_med:.0f} min</strong> vs In-House = <strong>{ih_med:.0f} min</strong><br>
• ประมาณ <strong>{wi_over90:.1f}%</strong> ของ Walk-In นั่งเกิน 90 นาที<br><br>

<strong>Interpretation:</strong><br>
• Walk-In มีแนวโน้มนั่งนานกว่าเล็กน้อย<br>
• แต่ลูกค้าส่วนใหญ่ยังอยู่ในช่วงเวลาปกติ ไม่ได้นั่งนานผิดปกติ<br><br>

<strong>So what?</strong><br>
• ปัญหาหลักไม่ได้อยู่ที่ “คนนั่งนาน” แต่คือ “ลูกค้าเข้ามาพร้อมกันเยอะเกิน”<br>
• ดังนั้น ถ้าแก้แค่เรื่องลดเวลานั่ง อาจไม่ช่วยแก้ปัญหาได้จริง
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# SECTION: TASK 2 — DISPROVE ACTIONS
# =========================================================
st.markdown('<p class="section-label">Task 2 — วิเคราะห์ข้อจำกัดของแต่ละแนวทาง</p>', unsafe_allow_html=True)
st.header("3 Actions — ทำไมแต่ละวิธีอาจแก้ปัญหาได้ไม่เต็มที่?")
st.markdown("ผู้บริหารเสนอ 3 แนวทางในการแก้ปัญหา แต่เมื่อดูจากข้อมูล แต่ละวิธียังมีข้อจำกัดและอาจจะยังไม่ตอบโจทย์")

# ── Action 1: ลดเวลานั่ง ──
st.subheader("Action 1: ลดเวลานั่งจาก 5 ชม.")

col7, col8 = st.columns(2)
with col7:
    bins_labels = ["<60m","60–90m","90–120m","120–180m","180–240m",">240m"]
    bins_vals   = [0, 60, 90, 120, 180, 240, 1000]
    meal_df2 = meal_df.copy()
    meal_df2["dur_bin"] = pd.cut(meal_df2["meal_min"], bins=bins_vals, labels=bins_labels, right=False)
    bin_counts = meal_df2["dur_bin"].value_counts().reindex(bins_labels, fill_value=0).reset_index()
    bin_counts.columns = ["Duration", "Groups"]
    fig_bins = px.bar(
        bin_counts, x="Duration", y="Groups", text="Groups",
        color_discrete_sequence=["#5B8DEF"]
    )
    fig_bins.update_traces(textposition="outside")
    fig_bins.update_layout(
        template="plotly_dark", title="Meal Duration Buckets",
        xaxis_title="Duration Range", height=380
    )
    st.plotly_chart(fig_bins, use_container_width=True)

with col8:
    import numpy as np
    all_dur = meal_df["meal_min"].dropna()
    x_vals  = np.linspace(0, 300, 200)
    cdf     = [(all_dur <= x).mean() * 100 for x in x_vals]
    import plotly.graph_objects as go
    fig_cdf = go.Figure()
    fig_cdf.add_trace(go.Scatter(x=x_vals, y=cdf, mode="lines",
                                  line=dict(color="#5B8DEF", width=2), name="CDF"))
    for limit, color, label in [(120,"#FF8C42","2hr limit"),(180,"#FF5A5F","3hr limit")]:
        pct = (all_dur <= limit).mean() * 100
        fig_cdf.add_vline(x=limit, line_dash="dash", line_color=color,
                          annotation_text=f"{label} ({pct:.0f}% left already)",
                          annotation_position="bottom right")
    fig_cdf.update_layout(
        template="plotly_dark", title="Cumulative % Guests Left by Time",
        xaxis_title="Minutes", yaxis_title="% Guests Already Left", height=380
    )
    st.plotly_chart(fig_cdf, use_container_width=True)

pct_over2hr = (meal_df["meal_min"] > 120).mean() * 100
pct_over3hr = (meal_df["meal_min"] > 180).mean() * 100

st.markdown(f"""
<div class="disprove-box">
⚠️ <strong>LIMITED IMPACT — การจำกัดเวลาอาจช่วยได้ไม่มาก</strong><br><br>

<strong>What we see:</strong><br>
• ลูกค้าที่นั่งเกิน 2 ชม. มีเพียง <strong>{pct_over2hr:.1f}%</strong> และเกิน 3 ชม. มีเพียง <strong>{pct_over3hr:.1f}%</strong><br>
• ลูกค้าส่วนใหญ่ออกก่อนถึง time limit อยู่แล้ว<br><br>

<strong>Interpretation:</strong><br>
• ปัญหาไม่ได้อยู่ที่ คนนั่งนาน แต่เป็นช่วง peak ที่ลูกค้าเข้ามาพร้อมกันเยอะ<br><br>

<strong>So what?</strong><br>
• การตั้ง time limit อาจไม่ได้ช่วยเพิ่มการหมุนโต๊ะมากนัก<br>
• อาจทำให้ลูกค้าที่กินตามปกติรู้สึกไม่ดี และกระทบ experience โดยไม่จำเป็น
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Action 2: ขึ้นราคา ──
st.subheader("Action 2: ขึ้นราคาทุกวันเป็น ฿259")

col9, col10 = st.columns(2)
with col9:
    rev_daytype = df.groupby("day_type", as_index=False)["revenue"].sum()
    fig_rev2 = px.bar(
        rev_daytype, x="day_type", y="revenue", text="revenue",
        color="day_type",
        color_discrete_map={"Weekday": "#5B8DEF", "Weekend": "#FF8C42"}
    )
    fig_rev2.update_traces(texttemplate="฿%{text:,.0f}", textposition="outside")
    fig_rev2.update_layout(
        template="plotly_dark", title="Revenue by Day Type (Current Pricing)",
        xaxis_title="Day Type", yaxis_title="Revenue (฿)", showlegend=False, height=380
    )
    st.plotly_chart(fig_rev2, use_container_width=True)

with col10:
    total_pax_val = df[df["had_meal"] == True]["party_size"].sum()
    current_rev   = total_pax_val * 170
    scenarios = {
        "Current\n(฿159/199)": current_rev,
        "฿259\n(-0%)":         total_pax_val * 259,
        "฿259\n(-10%)":        total_pax_val * 0.9 * 259,
        "฿259\n(-20%)":        total_pax_val * 0.8 * 259,
        "฿259\n(-30%)":        total_pax_val * 0.7 * 259,
    }
    scen_df = pd.DataFrame({"Scenario": list(scenarios.keys()), "Revenue": list(scenarios.values())})
    scen_df["color"] = scen_df["Revenue"].apply(
        lambda v: "#2ecc71" if v > current_rev else ("#FF5A5F" if v < current_rev else "#5B8DEF")
    )
    fig_scen = px.bar(
        scen_df, x="Scenario", y="Revenue", text="Revenue",
        color="Scenario",
        color_discrete_sequence=["#5B8DEF","#2ecc71","#FF8C42","#FF5A5F","#c0392b"]
    )
    fig_scen.update_traces(texttemplate="฿%{text:,.0f}", textposition="outside")
    fig_scen.update_layout(
        template="plotly_dark", title="Revenue Simulation — ฿259 at Different Demand Drops",
        xaxis_title="Scenario", yaxis_title="Revenue (฿)", showlegend=False, height=380
    )
    st.plotly_chart(fig_scen, use_container_width=True)

st.markdown(f"""
<div class="disprove-box">
⚠️ <strong>LIMITED IMPACT — การขึ้นราคาอาจไม่ช่วยแก้ปัญหาหลัก</strong><br><br>

<strong>What we see:</strong><br>
• Weekend ราคา ฿199 แต่ demand ยังสูง<br>
• หากขึ้นเป็น ฿259 รายได้จะเพิ่มก็ต่อเมื่อ demand ไม่ลดมาก<br>
• ถ้า demand ลดลง ~20–30% รายได้อาจใกล้เคียงหรือต่ำกว่าเดิม<br><br>

<strong>Interpretation:</strong><br>
• ลูกค้ายังตอบสนองต่อราคาไม่มากในช่วงนี้ <br>
• แต่ปัญหาหลักไม่ได้อยู่ที่ราคา<br><br>

<strong>So what?</strong><br>
• การขึ้นราคาไม่ได้ลดจำนวนของลูกค้าที่เข้ามาพร้อมกัน<br>
• และไม่ได้ช่วยให้ลูกค้า In-House ได้นั่งเร็วขึ้น<br>
• อาจกระทบความรู้สึกของ In-House guest ที่ต้องจ่ายเพิ่ม
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Action 3: Queue skip ──
st.subheader("Action 3: ให้ In-House แซงคิว")

col11, col12 = st.columns(2)
with col11:
    ih_df = df[df["guest_type"] == "In-House"]
    waited = int(ih_df["had_queue"].sum())
    direct = int((~ih_df["had_queue"]).sum())
    pie_df = pd.DataFrame({"Status": ["Waited in Queue", "Direct Seat"], "Count": [waited, direct]})
    fig_pie2 = px.pie(
        pie_df, names="Status", values="Count", hole=0.4,
        color="Status",
        color_discrete_map={"Waited in Queue": "#FF5A5F", "Direct Seat": "#2ecc71"}
    )
    fig_pie2.update_layout(
        template="plotly_dark", title="In-House: Queued vs Direct Seat", height=380
    )
    st.plotly_chart(fig_pie2, use_container_width=True)

with col12:
    peak_df2 = df.groupby(["meal_hour", "guest_type"]).size().reset_index(name="groups")
    fig_peak2 = px.bar(
        peak_df2, x="meal_hour", y="groups", color="guest_type",
        barmode="stack", text="groups",
        color_discrete_map={"In-House": "#5B8DEF", "Walk-In": "#FF8C42"}
    )
    fig_peak2.update_traces(textposition="inside")
    fig_peak2.update_layout(
        template="plotly_dark", title="Guest Volume by Hour (Stacked)",
        xaxis_title="Hour", yaxis_title="Groups", height=380
    )
    st.plotly_chart(fig_peak2, use_container_width=True)

ih_waited_pct = waited / len(ih_df) * 100 if len(ih_df) > 0 else 0

st.markdown(f"""
<div class="disprove-box">
⚠️ <strong>LIMITED IMPACT — การให้แซงคิวตลอดเวลาอาจไม่จำเป็น</strong><br><br>

<strong>What we see:</strong><br>
• มี In-House เพียง <strong>{ih_waited_pct:.1f}%</strong> ที่ต้องรอคิว<br>
• แปลว่าอีก <strong>{100-ih_waited_pct:.1f}%</strong> สามารถนั่งได้เลย<br><br>

<strong>Interpretation:</strong><br>
• ปัญหาไม่ได้เกิดตลอดเวลา แต่เกิดเฉพาะบางช่วง (เช่น peak hour)<br>
• การแซงคิวตลอดวันจึงอาจเกินความจำเป็น<br><br>

<strong>So what?</strong><br>
• การข้ามคิวอาเหมือนเป็นการเปลี่ยนคนรอจาก In-House → Walk-In ซึ่งอาจกิดปัญหาการเดินหนีไปเพิ่มมากขึ้น<br>
• แนวทางที่เหมาะสมคือใช้ queue skip เฉพาะช่วง peak hour
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# SECTION: TASK 3 — RECOMMENDATION
# =========================================================
st.markdown('<p class="section-label">Task 3 — Best Solution</p>', unsafe_allow_html=True)
st.header("Recommendation")
st.markdown("### Recommended Action: Priority seating for In-House guests **during peak hours only**")

col13, col14 = st.columns(2)
with col13:
    peak_df3 = df.groupby(["meal_hour", "guest_type"]).size().reset_index(name="groups")
    fig_peak3 = px.bar(
        peak_df3, x="meal_hour", y="groups", color="guest_type",
        barmode="group", text="groups",
        color_discrete_map={"In-House": "#5B8DEF", "Walk-In": "#FF8C42"}
    )
    fig_peak3.update_traces(textposition="outside")
    fig_peak3.update_layout(
        template="plotly_dark",
        title="Peak Hour: When Do In-House Guests Arrive?",
        xaxis_title="Hour of Day", yaxis_title="Groups", height=400
    )
    st.markdown("""
    <div class="insight-box">
    <strong>สรุปจากกราฟ:</strong><br><br>

    • ช่วงที่ลูกค้า In-House มาเยอะ จะเป็นช่วงที่ร้านคนแน่นที่สุด<br>
    • ช่วงนี้อาจต้องจัดโต๊ะให้ In-House ก่อน เพื่อลดการรอคิว<br>
    • แต่ช่วงอื่น ๆ Walk-In ยังสามารถเข้ามานั่งได้ตามปกติ
    </div>
    """, unsafe_allow_html=True)

with col14:
    import plotly.graph_objects as go

    total_tables = 20
    turnover     = 2.5
    ih_demand    = df[df["guest_type"] == "In-House"]["service_no"].count() / df["date"].nunique()

    # Chart 1: In-House arrivals by hour — ดูว่าช่วงไหนคนมาเยอะสุด (peak)
    ih_hourly = (
        df[df["guest_type"] == "In-House"]
        .groupby("meal_hour")
        .size()
        .reset_index(name="groups")
    )
    ih_hourly["is_peak"] = ih_hourly["meal_hour"].between(7, 10)
    fig_peak_ih = go.Figure(go.Bar(
        x=ih_hourly["meal_hour"].astype(str) + ":00",
        y=ih_hourly["groups"],
        marker_color=["#5B8DEF" if p else "#3a4a5a" for p in ih_hourly["is_peak"]],
        text=ih_hourly["groups"],
        textposition="outside"
    ))
    fig_peak_ih.update_layout(
        template="plotly_dark",
        title="In-House Arrivals by Hour (peak = highlighted)",
        xaxis_title="Hour", yaxis_title="Groups", height=230,
        showlegend=False,
        margin=dict(t=40, b=20)
    )
    st.plotly_chart(fig_peak_ih, use_container_width=True)

   # Chart 2: เปรียบเทียบจำนวนลูกค้ากับจำนวนโต๊ะที่ควรกันไว้
    peak_groups    = ih_hourly[ih_hourly["is_peak"]]["groups"].sum()
    reserve_30_cap = 0.30 * total_tables * turnover

    fig_compare = go.Figure(go.Bar(
        x=["In-House demand\n(peak 07–10)", "Reserved capacity\n 30% of tables"],
        y=[peak_groups, reserve_30_cap],
        marker_color=["#5B8DEF", "#2ecc71"],
        text=[f"{peak_groups:.0f} กลุ่ม", f"{reserve_30_cap:.0f} กลุ่ม"],
        textposition="outside"
    ))
    fig_compare.update_layout(
        template="plotly_dark",
        title="Peak Demand vs Reserved 30% Capacity",
        yaxis_title="Groups", height=230,
        showlegend=False,
        margin=dict(t=40, b=20)
    )
    st.plotly_chart(fig_compare, use_container_width=True)

# Summary
st.markdown("""
<div class="confirm-box">
✅ <strong>RECOMMENDED APPROACH — แก้ปัญหาได้ และกระทบลูกค้าน้อย</strong><br><br>

<strong>What we do:</strong><br>
• กันโต๊ะประมาณ <strong>30% (≈6 โต๊ะ)</strong> เฉพาะช่วงคนเยอะ (07:00–10:00)<br>
• พิจารณาลดเวลาใช้โต๊ะลงเล็กน้อย (time limit) ให้สอดคล้องกับพฤติกรรมลูกค้า<br><br>

<strong>Why this works:</strong><br>
• จากข้อมูล ลูกค้าส่วนใหญ่ออกจากร้านก่อนครบเวลาที่กำหนดอยู่แล้ว<br>
• การลดเวลาเล็กน้อยจึงอาจช่วยเพิ่มการหมุนโต๊ะ โดยไม่กระทบลูกค้าส่วนใหญ่<br>
• ไม่ต้องขึ้นราคา และยังควบคุมประสบการณ์ลูกค้าได้<br><br>

<strong>So what:</strong><br>
• ช่วยให้มีโต๊ะว่างเร็วขึ้นในช่วงพีค<br>
• เพิ่มโอกาสรองรับลูกค้าได้มากขึ้น โดยไม่ต้องเพิ่มโต๊ะ
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Busy Buffet Analysis | Data Analytics Test 2026")
