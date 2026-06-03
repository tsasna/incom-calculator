import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

st.set_page_config(page_title="工作收益计算器", layout="wide")
st.title("💰 工作收益计算器")

# 初始化数据结构
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        '日期', '总额', '到手金额', '时薪', '总时长', 'Minimo顾客数', '通勤报销'
    ])
    st.session_state.history['日期'] = pd.to_datetime(st.session_state.history['日期'])

# --- 1. 日历展示 ---
with st.expander("📅 点击查看/收起工作日历", expanded=False):
    calendar_events = []
    for _, row in st.session_state.history.iterrows():
        calendar_events.append({
            "title": f"¥{int(row['到手金额'])}",
            "start": row['日期'].strftime('%Y-%m-%d'),
            "backgroundColor": "#28a745"
        })
    cal_options = {"initialView": "dayGridMonth", "height": 450}
    state = calendar(events=calendar_events, options=cal_options)

# --- 2. 录入数据 ---
st.divider()
st.subheader("📊 今日数据录入")
col1, col2 = st.columns(2)

with col1:
    amounts = [st.number_input(f"单子 {i+1} (¥)", min_value=0, step=100, format="%d", key=f"amt_{i}") for i in range(10)]
    total_today = sum(amounts)
    st.write(f"### 今日总额 (SUM): ¥{int(total_today)}")

with col2:
    total_time = st.number_input("今日总出勤时长 (h)", min_value=0.0, step=0.5)
    minimo_count = st.number_input("Minimo顾客数量", min_value=0, step=1, format="%d")
    commute_fee = st.number_input("通勤报销金额 (¥)", min_value=0, step=50, format="%d")
    
    if st.button("结算并保存今日"):
        # 核心公式：到手 = (总额 / 2) - (330 * 顾客数) + (通勤费 if >= 4小时)
        daoshou = (total_today / 2) - (330 * minimo_count) + (commute_fee if total_time >= 4 else 0)
        shixin = daoshou / total_time if total_time > 0 else 0
        
        new_row = pd.DataFrame({
            '日期': [pd.Timestamp.now().normalize()],
            '总额': [int(total_today)],
            '到手金额': [int(daoshou)],
            '时薪': [int(shixin)],
            '总时长': [total_time],
            'Minimo顾客数': [int(minimo_count)],
            '通勤报销': [int(commute_fee)]
        })
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
        st.success("今日记录已保存！")
        st.rerun()

# --- 3. 统计汇总 ---
if not st.session_state.history.empty:
    st.divider()
    st.subheader("📈 本月累计统计")
    m_daoshou = st.session_state.history['到手金额'].sum()
    m_time = st.session_state.history['总时长'].sum()
    m_days = len(st.session_state.history)
    m_minimo = st.session_state.history['Minimo顾客数'].sum()
    m_avg_shixin = m_daoshou / m_time if m_time > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总到手金额 (JPY)", f"¥{int(m_daoshou)}")
    c2.metric("总出勤天数", f"{m_days} 天")
    c3.metric("平均时薪", f"¥{int(m_avg_shixin)}")
    c4.metric("总顾客数量", f"{int(m_minimo)} 人")
    
    st.write(f"**总出勤时间**: {m_time} 小时")
    
    if st.button("清空所有历史数据"):
        st.session_state.history = pd.DataFrame(columns=st.session_state.history.columns)
        st.rerun()
        