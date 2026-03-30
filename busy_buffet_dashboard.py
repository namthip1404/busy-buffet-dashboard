import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# Page config
# =========================================================
st.set_page_config(
    page_title="Busy Buffet Dashboard",
    page_icon="🍽️",
    layout="wide"
)

# =========================================================
# Load data
# =========================================================
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
# Sidebar
# =========================================================
st.sidebar.title("Busy Buffet")
st.sidebar.caption("Aster Hotel & Residence")

date_options = sorted(df["date"].dt.date.dropna().unique())
selected_dates = st.sidebar.multiselect(
    "Select Dates",
    options=date_options,
    default=date_options
)
if selected_dates:
    df = df[df["date"].dt.date.isin(selected_dates)]

guest_options = sorted(df["guest_type"].dropna().unique())
selected_guest = st.sidebar.multiselect(
    "Guest Type",
    options=guest_options,
    default=guest_options
)
if selected_guest:
    df = df[df["guest_type"].isin(selected_guest)]

st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("""
- Overview  
- Customer Mix  
- Peak Hour Bottleneck  
- Service Inequality  
- Dining Time is NOT the Issue  
- Price vs Revenue Reality  
- Recommendation  
""")

# =========================================================
# Title
# =========================================================
st.title("🍽️ Busy Buffet — Hotel Amber 85")
st.caption("Operational Bottleneck Analysis")

# =========================================================
# KPI
# =========================================================
total_groups = len(df)
total_pax = df["party_size"].sum()
walkaways = df["is_walkaway"].sum()
avg_wait = df["wait_min"].mean()
avg_meal = df["meal_min"].mean()
total_revenue = df["revenue"].sum()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Groups", f"{int(total_groups)}")
c2.metric("Pax Served", f"{int(total_pax)}")
c3.metric("Walkaways", f"{int(walkaways)}")
c4.metric("Avg Wait", f"{avg_wait:.0f} min" if pd.notna(avg_wait) else "N/A")
c5.metric("Avg Meal", f"{avg_meal:.0f} min" if pd.notna(avg_meal) else "N/A")
c6.metric("Revenue", f"{total_revenue:,.0f}")

st.markdown("---")

# =========================================================
# Row 1
# =========================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Customer Mix")
    mix = df["guest_type"].value_counts().reset_index()
    mix.columns = ["guest_type", "count"]

    fig_mix = px.pie(
        mix,
        names="guest_type",
        values="count",
        hole=0.55,
        color="guest_type",
        color_discrete_map={
            "In-House": "#5B8DEF",
            "Walk-In": "#FF8C42"
        }
    )
    fig_mix.update_layout(
        template="plotly_dark",
        title="Guest Type Distribution",
        height=420
    )
    st.plotly_chart(fig_mix, use_container_width=True)
    st.caption("ดูสัดส่วนลูกค้าหลักของร้าน ถ้า Walk-In เยอะ แปลว่าโปรโมชันดึง demand เข้ามาจริง")

with col2:
    st.subheader("Peak Hour Bottleneck")
    peak_df = df.groupby("meal_hour").size().reset_index(name="groups")

    fig_peak = px.bar(
        peak_df,
        x="meal_hour",
        y="groups",
        text="groups",
        color_discrete_sequence=["#5B8DEF"]
    )
    fig_peak.update_traces(textposition="outside")
    fig_peak.update_layout(
        template="plotly_dark",
        title="Customer Volume by Hour",
        xaxis_title="Hour",
        yaxis_title="Groups",
        height=420
    )
    st.plotly_chart(fig_peak, use_container_width=True)
    st.caption("ลูกค้ากระจุกตัวในบางชั่วโมง ทำให้เกิด bottleneck ชัดเจน")

# =========================================================
# Row 2
# =========================================================
col3, col4 = st.columns(2)

with col3:
    st.subheader("Service Inequality")
    wait_guest = df.groupby("guest_type", as_index=False)["wait_min"].mean().dropna()

    fig_wait = px.bar(
        wait_guest,
        x="guest_type",
        y="wait_min",
        text="wait_min",
        color="guest_type",
        color_discrete_map={
            "In-House": "#5B8DEF",
            "Walk-In": "#FF8C42"
        }
    )
    fig_wait.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_wait.update_layout(
        template="plotly_dark",
        title="Average Wait Time by Guest Type",
        xaxis_title="Guest Type",
        yaxis_title="Minutes",
        showlegend=False,
        height=420
    )
    st.plotly_chart(fig_wait, use_container_width=True)
    st.caption("ถ้า Walk-In รอเฉลี่ยนานกว่า แปลว่าประสบการณ์ของสองกลุ่มไม่เท่ากัน")

with col4:
    st.subheader("Dining Time is NOT the Issue")
    meal_df = df[df["meal_min"].notna()].copy()

    fig_meal = px.histogram(
        meal_df,
        x="meal_min",
        nbins=30,
        color_discrete_sequence=["#5B8DEF"]
    )
    fig_meal.add_vline(x=90, line_dash="dash", line_color="#FF5A5F")
    fig_meal.update_layout(
        template="plotly_dark",
        title="Meal Duration Distribution",
        xaxis_title="Meal Duration (minutes)",
        yaxis_title="Count",
        height=420
    )
    st.plotly_chart(fig_meal, use_container_width=True)
    st.caption("ถ้าลูกค้าส่วนใหญ่กินเสร็จภายในเวลาสั้นพอ ปัญหาไม่ได้มาจากการนั่งนาน")

# =========================================================
# Row 3
# =========================================================
st.subheader("Price vs Revenue Reality")

rev_daytype = df.groupby("day_type", as_index=False)["revenue"].sum()

fig_rev = px.bar(
    rev_daytype,
    x="day_type",
    y="revenue",
    text="revenue",
    color="day_type",
    color_discrete_map={
        "Weekday": "#5B8DEF",
        "Weekend": "#FF8C42"
    }
)
fig_rev.update_traces(texttemplate="%{text:.0f}", textposition="outside")
fig_rev.update_layout(
    template="plotly_dark",
    title="Revenue by Day Type",
    xaxis_title="Day Type",
    yaxis_title="Revenue",
    showlegend=False,
    height=420
)
st.plotly_chart(fig_rev, use_container_width=True)
st.caption("weekday ราคา 159 และ weekend ราคา 199 อยู่แล้ว จึงควรดูว่าช่วงที่ราคาสูงกว่าสร้างรายได้ได้ดีแค่ไหน")

# =========================================================
# Recommendation
# =========================================================
st.markdown("---")
st.subheader("🔥 Recommendation")

st.markdown("""
### Recommended Action: Priority seating for In-House guests during peak hours only

**Why this works**
- ปัญหาหลักคือ demand กระจุกในช่วง peak hour
- Walk-In เข้ามาจำนวนมากจากโปรโมชัน และทำให้เกิดแรงกดดันต่อโต๊ะ
- Walk-In รอนานกว่า จึงสะท้อนถึง queue pressure ที่ชัดกว่า
- ลูกค้าส่วนใหญ่ไม่ได้กินนานผิดปกติ ดังนั้น root cause ไม่ใช่ meal duration

**Why this is better than the other actions**
- ลดเวลาในการกิน: กระทบลูกค้าปกติ ทั้งที่คนส่วนใหญ่ไม่ได้กินนานเกินไป
- ขึ้นราคาเป็น 259 ทุกวัน: อาจเพิ่มรายได้ แต่ไม่ได้แก้ bottleneck โดยตรง
- ข้ามคิวให้ In-House ทั้งวัน: แรงเกินไป ควรใช้เฉพาะช่วง peak จะเหมาะกว่า

**Business takeaway**
- แก้เฉพาะช่วง peak จะมีประสิทธิภาพกว่าการเปลี่ยน policy ทั้งระบบ
""")