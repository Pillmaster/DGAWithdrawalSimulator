import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="🇳🇱 DGA Withdrawal Simulator — progressive profit tax & dividend tax (NL)", layout="wide")

st.title("🇳🇱 DGA Withdrawal Simulator — Progressive Profit Tax & Dividend Tax (NL)")

st.markdown("""
This tool simulates the capital development of a company for a DGA, including:
- annual returns  
- inflation-adjusted net withdrawals  
- progressive corporate profit tax  
- dividend tax on distributions  

All amounts are in euros (€).  
The first row shows the starting capital.
""")

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("Input Parameters")

current_year = datetime.date.today().year

start_capital = st.sidebar.number_input("Starting capital (€)", value=250000, step=10000, format="%d")
annual_return = st.sidebar.number_input("Average annual return (%)", value=4.0, step=0.1, format="%.1f") / 100
inflation = st.sidebar.number_input("Inflation (%)", value=2.0, step=0.1, format="%.1f") / 100
net_withdrawal = st.sidebar.number_input("Initial net withdrawal (€)", value=30000, step=5000, format="%d")

st.sidebar.subheader("Taxes")
tax_threshold = st.sidebar.number_input("Profit threshold for lower rate (€)", value=200000, step=50000, format="%d")
tax_low = st.sidebar.number_input("Tax below threshold (%)", value=19.0, step=0.1, format="%.1f") / 100
tax_high = st.sidebar.number_input("Tax above threshold (%)", value=25.8, step=0.1, format="%.1f") / 100
dividend_tax = st.sidebar.number_input("Dividend tax (%)", value=25.0, step=0.1, format="%.1f") / 100

years = st.sidebar.number_input("Projection period (years)", value=30, step=1)

# --------------------------
# Calculations
# --------------------------
data = []
capital = start_capital
capital_depleted = False

# Year 0
data.append({
    "Calendar Year": current_year,
    "Profit": 0,
    "Profit Tax": 0,
    "Dividend Tax": 0,
    "Gross Withdrawal": 0,
    "Net Withdrawal": 0,
    "End Capital": capital
})

for year in range(1, years + 1):
    cal_year = current_year + year
    profit = capital * annual_return
    
    # progressive tax
    if profit <= tax_threshold:
        profit_tax = profit * tax_low
    else:
        profit_tax = tax_threshold * tax_low + (profit - tax_threshold) * tax_high
    
    # inflation-adjusted net withdrawal
    adjusted_net_withdrawal = net_withdrawal * ((1 + inflation) ** (year - 1))
    gross_withdrawal = adjusted_net_withdrawal / (1 - dividend_tax)
    dividend_paid = gross_withdrawal * dividend_tax
    
    # update capital
    projected_capital = capital + profit - profit_tax - gross_withdrawal
    
    if projected_capital < 0:
        # Adjust last withdrawal so capital exactly zero
        gross_withdrawal += projected_capital  # projected_capital is negative
        adjusted_net_withdrawal = gross_withdrawal * (1 - dividend_tax)
        dividend_paid = gross_withdrawal * dividend_tax
        capital = 0
        capital_depleted = True
    else:
        capital = projected_capital
    
    data.append({
        "Calendar Year": cal_year,
        "Profit": profit,
        "Profit Tax": profit_tax,
        "Dividend Tax": dividend_paid,
        "Gross Withdrawal": gross_withdrawal,
        "Net Withdrawal": adjusted_net_withdrawal,
        "End Capital": capital
    })
    
    if capital_depleted:
        break

df = pd.DataFrame(data)

# --------------------------
# Results
# --------------------------
st.header("📊 Results Overview")

if capital_depleted:
    depleted_year = df.iloc[-1]["Calendar Year"]
    st.warning(f"💡 Capital depleted in year {int(depleted_year)}!")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Starting Capital", f"€ {start_capital:,.0f}")
col2.metric("End Capital", f"€ {capital:,.0f}")
col3.metric("Total Profit Tax", f"€ {df['Profit Tax'].sum():,.0f}")
col4.metric("Total Dividend Tax", f"€ {df['Dividend Tax'].sum():,.0f}")

# Table
st.subheader("Yearly Table")
st.dataframe(df.style.format({
    "Profit": "€ {:,.0f}",
    "Profit Tax": "€ {:,.0f}",
    "Dividend Tax": "€ {:,.0f}",
    "Gross Withdrawal": "€ {:,.0f}",
    "Net Withdrawal": "€ {:,.0f}",
    "End Capital": "€ {:,.0f}"
}), use_container_width=True)

# --------------------------
# Interactive Plotly Chart
# --------------------------
st.subheader("Capital Development Over Time (Interactive)")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Calendar Year"], y=df["End Capital"], mode='lines+markers', name="End Capital"))
fig.add_trace(go.Scatter(x=df["Calendar Year"], y=df["Profit"], mode='lines+markers', name="Profit"))
fig.add_trace(go.Scatter(x=df["Calendar Year"], y=df["Profit Tax"], mode='lines+markers', name="Profit Tax"))
fig.add_trace(go.Scatter(x=df["Calendar Year"], y=df["Net Withdrawal"], mode='lines+markers', name="Net Withdrawal"))

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Amount (€)",
    hovermode="x unified",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("© 2025 DGA Withdrawal Simulator – simulating DGA financial scenarios with progressive profit and dividend tax.")

