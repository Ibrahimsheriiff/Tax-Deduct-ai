
import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(page_title="Deloitte DeductAI", layout="wide")

# === Deloitte Branding and Styling ===
st.markdown("""
    <style>
    body {
        background-color: #f4f6f9;
    }
    .stButton > button {
        background-color: #86BC25;
        color: white;
        font-weight: bold;
        border-radius: 6px;
    }
    h1, h2, h3 {
        color: #0e4c92;
    }
    footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# === Sidebar with Deloitte logo and tips ===
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/88/Deloitte_Logo.png", width=150)
    st.markdown("### 💬 Need Help?")
    st.info("Upload a CSV or Excel file with at least 2 columns: description and amount.")

# === App Title and Upload Instructions ===
st.image("https://upload.wikimedia.org/wikipedia/commons/8/88/Deloitte_Logo.png", width=200)
st.title("🏢 Deloitte DeductAI – Intelligent Tax Analysis")
st.markdown("📥 Upload a client's financial document (PDF, CSV, or Excel) for AI-assisted deduction analysis and classification.")

# === User Inputs ===
industry = st.selectbox("🏭 Select industry:", [
    "Hospitality / Restaurant", "Technology / SaaS", "Construction",
    "Finance & Banking", "Retail", "Healthcare", "Other"
])

doc_type = st.selectbox("📄 Select document type:", [
    "Balance Sheet (PDF)", "Profit & Loss Statement (Excel/CSV)",
    "General Ledger Export (CSV)", "Expense Report (Excel)", "Other Financial Statement"
])

uploaded_file = st.file_uploader("📂 Upload document", type=["pdf", "csv", "xlsx", "xls"])

CATEGORY_RULES = {
    "revenue": ["revenue", "sales", "income"],
    "operating": ["rent", "wages", "utilities", "supplies", "subscription", "marketing", "software", "maintenance"],
    "depreciation": ["depreciation", "amortization"],
    "interest": ["interest", "loan cost", "bank charges"],
    "capital": ["asset purchase", "equipment", "capex", "furniture", "vehicle"]
}
DEDUCTIBLE_CATEGORIES = ["operating", "depreciation", "interest"]
INDUSTRY_SUGGESTIONS = {
    "Hospitality / Restaurant": ["Kitchen equipment", "POS systems", "Food wastage", "Delivery platform fees"],
    "Technology / SaaS": ["Cloud costs", "Laptop purchases", "Developer tools", "R&D expenses"],
    "Construction": ["Machinery", "Site fuel", "Work boots", "Scaffolding hire"]
}

def classify_expense(description):
    description = str(description).lower()
    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in description:
                return category
    return "other"

def extract_totals(df):
    revenue_total = 0
    categories = {k: 0 for k in CATEGORY_RULES.keys()}
    categories["other"] = 0
    breakdown = []

    for _, row in df.iterrows():
        desc = str(row[0])
        amt = row[1] if len(row) > 1 else 0
        if not isinstance(amt, (int, float)) or pd.isnull(amt):
            continue
        cat = classify_expense(desc)
        if cat == "revenue":
            revenue_total += amt
        else:
            categories[cat] += amt
            breakdown.append((desc, amt, cat))
    return revenue_total, categories, breakdown

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text = "".join([page.extract_text() or "" for page in pdf.pages])
            st.success("✅ PDF uploaded.")
            st.subheader("📑 Extracted Text:")
            st.text_area("Raw content from uploaded PDF", text[:3000], height=300, key="pdf_text_area")
            st.warning("⚠️ Classification and deduction only available for Excel/CSV.")
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")
    else:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file, engine="openpyxl")
            st.success("✅ Spreadsheet loaded.")
            st.dataframe(df.head(10))

            if df.shape[1] >= 2:
                st.subheader("🔍 Classification Summary")
                revenue_total, categories, breakdown = extract_totals(df)

                st.markdown("### 🤖 AI-Simulated Tax Advice")
                advice = []
                if categories["depreciation"] > 0:
                    advice.append("Depreciation detected — ensure assets follow Division 40 or 43.")
                if categories["interest"] > 0:
                    advice.append("Interest expenses may be deductible — ensure they're not capitalized.")
                if categories["capital"] > 0:
                    advice.append("Capital purchases found — check instant asset write-off eligibility.")
                if categories["operating"] > 0.5 * revenue_total:
                    advice.append("Operating costs exceed 50% of revenue — review for excess or discretionary spend.")
                if not advice:
                    advice.append("No major risks detected — standard deduction paths likely.")
                for line in advice:
                    st.write(f"🧠 {line}")

                st.metric("Total Revenue", f"${revenue_total:,.2f}")
                st.bar_chart(pd.Series(categories))

                st.markdown("### 🧾 Itemized Breakdown")
                result_df = pd.DataFrame(breakdown, columns=["Description", "Amount", "Category"])
                result_df["Deductible"] = result_df["Category"].apply(lambda x: "✅" if x in DEDUCTIBLE_CATEGORIES else "🚫")
                st.dataframe(result_df)

                st.download_button("📥 Download Summary (CSV)", result_df.to_csv(index=False), "deduction_summary.csv", "text/csv")

                st.markdown("### 💡 Industry-Specific Suggestions")
                for item in INDUSTRY_SUGGESTIONS.get(industry, []):
                    st.write(f"🔹 {item}")
            else:
                st.warning("File must have at least two columns: description and amount.")
        except Exception as e:
            st.error(f"Error reading file: {e}")
else:
    st.caption("Waiting for document upload...")

# === Footer Branding ===
st.markdown("""
<hr style="border: 0.5px solid #86BC25;" />
<center><small><em>Deloitte DeductAI — Smart Tax. Human Insight. Powered by AI.</em></small></center>
""", unsafe_allow_html=True)
