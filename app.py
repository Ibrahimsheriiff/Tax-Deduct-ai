import streamlit as st

# === Occupation-specific deductions ===
DEDUCTIONS = {
    "Factory Worker": {
        "Car travel between job sites or carrying bulky tools": {
            "deductible": True,
            "notes": "Only if tools are bulky, essential, and no secure storage at workplace."
        },
        "Steel-capped boots or protective gear": {
            "deductible": True,
            "notes": "Must be protective and specific to work safety."
        },
        "Overtime meals with allowance": {
            "deductible": True,
            "notes": "Only when paid under award or agreement and included in income."
        },
        "Renewal of special licenses (e.g. forklift)": {
            "deductible": True,
            "notes": "Initial license costs are not deductible. Renewals are."
        },
        "Tools and equipment <= $300": {
            "deductible": True,
            "notes": "Can be deducted immediately if used for work."
        },
        "Tools and equipment > $300": {
            "deductible": True,
            "notes": "Must be depreciated over time."
        },
        "Union fees or safety equipment": {
            "deductible": True,
            "notes": "Includes items like goggles or breathing masks."
        },
        "Normal commute to work": {
            "deductible": False,
            "notes": "Private travel, not deductible."
        },
        "Conventional work clothing": {
            "deductible": False,
            "notes": "Everyday clothing not deductible even if employer-required."
        },
        "Initial license costs": {
            "deductible": False,
            "notes": "Only renewals are deductible, not initial license acquisition."
        },
        "Meals during normal work hours": {
            "deductible": False,
            "notes": "Considered private expenses."
        },
        "Parking at work / public transport from home": {
            "deductible": False,
            "notes": "Commuting-related, not deductible."
        }
    },
    "IT Professional": {
        "Travel to alternate workplace or clients": {
            "deductible": True,
            "notes": "Travel for same job to clients or between offices is deductible."
        },
        "Work from home expenses": {
            "deductible": True,
            "notes": "Must follow ATO methods and keep records. No coffee/tea/milk."
        },
        "Self-education (related to current job)": {
            "deductible": True,
            "notes": "Must maintain or improve current work skills or income."
        },
        "Phone and internet (work use %)": {
            "deductible": True,
            "notes": "Claim only work-related portion with records."
        },
        "Tools and equipment <= $300": {
            "deductible": True,
            "notes": "Can be immediately deducted if used for work."
        },
        "Tools and equipment > $300": {
            "deductible": True,
            "notes": "Must be depreciated over time."
        },
        "Union or professional fees": {
            "deductible": True,
            "notes": "Memberships or associations for your profession."
        },
        "Commuting from home": {
            "deductible": False,
            "notes": "Normal commute not deductible, even for late hours."
        },
        "Employer-provided items": {
            "deductible": False,
            "notes": "No claim allowed if reimbursed or supplied by employer."
        },
        "Study for unrelated job": {
            "deductible": False,
            "notes": "You can't claim if you're studying to switch professions."
        },
        "Coffee, tea, general supplies": {
            "deductible": False,
            "notes": "Private household expenses are not deductible."
        },
        "Childcare, fines, or music services": {
            "deductible": False,
            "notes": "These are private expenses."
        }
    }
}

# === Tax logic ===
def calculate_income_tax(taxable_income):
    if taxable_income <= 18200:
        return 0
    elif taxable_income <= 45000:
        return (taxable_income - 18200) * 0.16
    elif taxable_income <= 135000:
        return 4288 + (taxable_income - 45000) * 0.30
    elif taxable_income <= 190000:
        return 31288 + (taxable_income - 135000) * 0.37
    else:
        return 51638 + (taxable_income - 190000) * 0.45

# === AI-Simulated Review Logic ===
def ai_deductions_review(occupation, income, claimed_items):
    high_risk = []
    suggestions = []
    audit_risk = "Low"
    notes = []

    thresholds = {
        "Self-education": 3000,
        "Tools and equipment > $300": 1000,
        "Phone and internet (work use %)": 1000
    }

    common_claims = {
        "Factory Worker": [
            "Steel-capped boots or protective gear",
            "Tools and equipment <= $300"
        ],
        "IT Professional": [
            "Phone and internet (work use %)",
            "Work from home expenses",
            "Self-education (related to current job)"
        ]
    }

    claimed_labels = [label for label, _ in claimed_items]

    for label, amount in claimed_items:
        if label in thresholds and amount > thresholds[label]:
            high_risk.append(f"⚠️ {label}: Claimed ${amount:.2f}, above typical threshold ${thresholds[label]}")

    for common in common_claims.get(occupation, []):
        if common not in claimed_labels:
            suggestions.append(f"➕ Consider claiming: {common}")

    total_claimed = sum(amount for _, amount in claimed_items)
    ratio = total_claimed / income if income > 0 else 0
    if ratio > 0.4:
        audit_risk = "High"
    elif ratio > 0.2:
        audit_risk = "Medium"

    summary = f"## 🧠 AI Deductions Review\n\n"
    if high_risk:
        summary += "**🚩 Flagged Unusual Claims:**\n" + "\n".join(high_risk) + "\n\n"
    else:
        summary += "✅ No unusually high claims detected.\n\n"

    if suggestions:
        summary += "**🔄 Suggested Missing Deductions:**\n" + "\n".join(suggestions) + "\n\n"

    summary += f"**🔎 Estimated Audit Risk Level:** `{audit_risk}`\n"

    if audit_risk != "Low":
        notes.append("📝 Consider asking user for receipts on higher claims.")

    return {
        "summary": summary,
        "audit_risk": audit_risk,
        "manager_notes": notes
    }

# === App UI ===
st.title("TEAM ONE TAX ADVISORY")
occupation = st.selectbox("Select your occupation:", list(DEDUCTIONS.keys()))
income = st.number_input("Enter your annual income ($):", min_value=0.0, step=1000.0)

st.subheader(f"Enter your claimed expenses for: {occupation}")
claimed_items = []
total_deductible = 0
deductions = DEDUCTIONS[occupation]

tabs = st.tabs(["Eligible Deductions", "Non-Deductible Items"])

with tabs[0]:
    for label, data in deductions.items():
        if data['deductible']:
            checked = st.checkbox(f"{label}", key=f"check_{occupation}_{label}")
            if checked:
                amount = st.number_input(f"Amount for: {label}", min_value=0.0, step=10.0, key=f"amount_{occupation}_{label}")
                claimed_items.append((label, amount))
                total_deductible += amount
            st.caption(f"ℹ️ {data['notes']}")

with tabs[1]:
    for label, data in deductions.items():
        if not data['deductible']:
            st.checkbox(f"{label} ❌", key=f"check_{occupation}_{label}", disabled=True)
            st.caption(f"🚫 {data['notes']}")

if st.button("Calculate Taxable Income"):
    taxable_income = max(0, income - total_deductible)
    st.success(f"Your estimated taxable income is: ${taxable_income:,.2f}")
    st.info(f"Total deductible claims: ${total_deductible:,.2f}")

    st.write("### Claimed Items and Values:")
    for label, amount in claimed_items:
        st.write(f"- {label}: ${amount:,.2f}")

    st.write("---")
    st.subheader("🧮 Estimated Tax Payable")
    include_medicare = st.checkbox("Include Medicare Levy (2%)", value=True)
    income_tax = calculate_income_tax(taxable_income)
    medicare_levy = taxable_income * 0.02 if include_medicare else 0
    total_tax = income_tax + medicare_levy

    st.write(f"Income Tax: ${income_tax:,.2f}")
    if include_medicare:
        st.write(f"Medicare Levy (2%): ${medicare_levy:,.2f}")
    st.success(f"Total Estimated Tax Payable: ${total_tax:,.2f}")

if st.button("🧠 Run AI Deductions Review"):
    with st.spinner("Analyzing deductions..."):
        review = ai_deductions_review(occupation, income, claimed_items)

    st.markdown(review["summary"])
    if review["manager_notes"]:
        st.warning("⚠️ Manager Notes:")
        for note in review["manager_notes"]:
            st.write(f"- {note}")

# === Sidebar FAQ ===
st.sidebar.title("🧠 Tax Help / FAQ")

with st.sidebar.expander("Can I claim work clothes?"):
    st.markdown("""
**In most cases, no.**

You can't claim everyday clothes (e.g. jeans, sneakers), even if required by your employer.  
You *can* claim **protective or occupation-specific clothing** such as:
- Steel-capped boots
- Hi-vis vests
- Clothing with a company logo
""")

with st.sidebar.expander("How is car expense calculated?"):
    st.markdown("""
**Two methods approved by ATO:**
- **Cents-per-kilometre**: Max 5,000 km, fixed rate per km
- **Logbook method**: Requires detailed records for 12 weeks

Only claim travel *between workplaces* or if carrying **bulky tools** with no workplace storage.  
Commuting from home to normal work is **not deductible**.
""")

with st.sidebar.expander("What about working from home?"):
    st.markdown("""
You can claim:
- Electricity, internet, phone (proportional)
- Depreciation of home office equipment

You **can’t** claim:
- Coffee, tea, snacks
- Items your employer reimbursed you for
""")

with st.sidebar.expander("Is self-education deductible?"):
    st.markdown("""
✅ Yes, **if** the course directly relates to your current job and helps:
- Improve your skills or
- Increase your income in your **current role**

❌ No, if the course prepares you for a **new profession**.
""")
