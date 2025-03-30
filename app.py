import streamlit as st
import pandas as pd
import plotly.express as px

# Define tax brackets (Example for a progressive tax system)
def calculate_tax(income, deductions, tax_credits, filing_status):
    tax_brackets = {
        "single": [(10000, 0.1), (30000, 0.15), (70000, 0.2), (float('inf'), 0.25)],
        "married": [(20000, 0.1), (60000, 0.15), (120000, 0.2), (float('inf'), 0.25)]
    }
    
    taxable_income = max(0, income - deductions)
    tax_due = 0
    prev_limit = 0
    
    for bracket in tax_brackets[filing_status]:
        limit, rate = bracket
        if taxable_income > prev_limit:
            taxable_amount = min(taxable_income, limit) - prev_limit
            tax_due += taxable_amount * rate
            prev_limit = limit
    
    tax_due = max(0, tax_due - tax_credits)
    return taxable_income, tax_due

# Streamlit UI
st.title("🏦 Tax Estimator App")
st.sidebar.header("User Input")

# User Inputs
income = st.sidebar.number_input("Enter Your Yearly Income ($):", min_value=0, value=50000, step=1000)
deductions = st.sidebar.number_input("Enter Total Deductions ($):", min_value=0, value=5000, step=500)
tax_credits = st.sidebar.number_input("Enter Tax Credits ($):", min_value=0, value=1000, step=100)
filing_status = st.sidebar.selectbox("Select Your Filing Status:", ["single", "married"])

if st.sidebar.button("Calculate Tax"):
    taxable_income, tax_due = calculate_tax(income, deductions, tax_credits, filing_status)
    st.subheader("💰 Tax Summary")
    st.write(f"**Taxable Income:** ${taxable_income:,.2f}")
    st.write(f"**Estimated Tax Due:** ${tax_due:,.2f}")
    
    # Visualization
    tax_data = pd.DataFrame({"Category": ["Income After Tax", "Tax Paid"], "Amount": [income - tax_due, tax_due]})
    fig = px.pie(tax_data, values="Amount", names="Category", title="Tax Breakdown", hole=0.3)
    st.plotly_chart(fig)

    bar_data = pd.DataFrame({"Category": ["Total Income", "Taxable Income", "Tax Due"], "Amount": [income, taxable_income, tax_due]})
    fig2 = px.bar(bar_data, x="Category", y="Amount", title="Income vs. Tax Due", text_auto=True)
    st.plotly_chart(fig2)

# Footer
st.write("\n\n Developed for AF3005 – Programming for Finance | Instructor: Dr. Usama Arshad")


