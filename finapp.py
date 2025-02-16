import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.title("💰 Personal Spending Tracker")

# Predefined categories and their limits
categories = ["Rent", "Groceries", "Transport", "Entertainment", "Subscriptions", "Other"]
default_limits = {"Rent": 1000, "Groceries": 300, "Transport": 150, "Entertainment": 200, "Subscriptions": 100, "Other": 250}
category_limits = {category: st.sidebar.number_input(f"Set Limit for {category} ($)", min_value=0, value=default_limits[category]) for category in categories}
overall_limit = st.sidebar.number_input("Set Overall Monthly Limit ($)", min_value=0, value=3000)

# Data storage for expenses
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Cost", "Name", "Category"])

# User input for spending
st.subheader("Add a New Expense")
col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
with col1:
    date = st.date_input("Date", datetime.today())
with col2:
    amount = st.number_input("Cost ($)", format="%.2f")
with col3:
    name = st.text_input("Name")
with col4:
    category = st.selectbox("Category", categories)
with col5:
    
    st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)  # Adds 30px of vertical space


    button = st.button("Add")
    

if button:
        new_entry = pd.DataFrame([[date, amount, name, category]], columns=["Date", "Cost", "Name", "Category"])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_entry], ignore_index=True)
        st.success("Expense Added!")

st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)  # Adds 30px of vertical space

# Spending Overview
st.subheader("📊 Spendings Overview")
st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)  # Adds 30px of vertical space

# Total spending progress bar (Full width)
total_spent = st.session_state.expenses["Cost"].sum()
progress_percentage = min(total_spent / overall_limit, 1.0) * 100
st.markdown(
    f"""
    <div style="background-color: #F0F2F6; border-radius: 10px; height: 40px; width: 100%; position: relative;">
        <div style="background-color: #4CAF50; width: {progress_percentage}%; height: 100%; border-radius: 10px;"></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)  # Adds 30px of vertical space

st.write(f"**Total Spent:** ${total_spent:.2f} / ${overall_limit}")


st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)  # Adds 30px of vertical space

st.write(f"#### By Categories:")
st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)  # Adds 30px of vertical space



category_spending = st.session_state.expenses.groupby("Category")["Cost"].sum().reset_index()
rows = []
for i, cat in enumerate(categories):
    spent = category_spending[category_spending["Category"] == cat]["Cost"].sum() if cat in category_spending["Category"].values else 0
    donut_fig = px.pie(values=[spent, max(0, category_limits[cat] - spent)], hole=0.5)
    
    # Reduce margins and adjust chart size for better fit
    donut_fig.update_traces(marker=dict(colors=["red" if spent >= category_limits[cat] else "green", "#F0F2F6"]), textinfo='none')
    donut_fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),  # Reduce margins
        height=150,  # Set a fixed height
        width=150,  # Set a fixed width
    )

    rows.append((cat, donut_fig, spent))
    
# Display the charts in a row with equal width for each
for i in range(0, len(rows), 3):
    row_cats = rows[i:i+3]
    cols = st.columns(len(row_cats))
    for col, (cat, fig, spent) in zip(cols, row_cats):
        with col:
            st.write(f"##### {cat}")
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"Spent: ${spent:.2f} / ${category_limits[cat]}")
            st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)  # Adds 30px of vertical space



# Warning Messages
st.subheader("⚠️ Budget Warnings")
if total_spent > overall_limit:
    st.error("🚨 You have exceeded your overall budget limit!")
for cat in categories:
    spent = st.session_state.expenses[st.session_state.expenses["Category"] == cat]["Cost"].sum()
    if spent > category_limits[cat]:
        st.warning(f"⚠️ You have exceeded the limit for {cat}!")

# Spending Log
st.subheader("📜 Spending Log")
st.markdown("<style>.dataframe { width: 100%; }</style>", unsafe_allow_html=True)
spending_log = st.data_editor(st.session_state.expenses, num_rows="dynamic")
st.session_state.expenses = spending_log

# Report Generation
st.subheader("📑 Report Generation")
start_date = st.date_input("Start Date", datetime.today())
end_date = st.date_input("End Date", datetime.today())
if st.button("📊 Generate Report"):
    report_data = st.session_state.expenses[(st.session_state.expenses["Date"] >= start_date) & (st.session_state.expenses["Date"] <= end_date)]
    if not report_data.empty:
        category_report = report_data.groupby("Category")["Cost"].sum().reset_index()
        report_fig = px.pie(category_report, names="Category", values="Cost", title="Spending Breakdown ($)")
        st.plotly_chart(report_fig)
    else:
        st.warning("No expenses found in the selected date range.")

st.write("---")
st.write("💡 *Track your spending and stay within your budget to improve financial wellness!*")
