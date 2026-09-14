# User Guide — Student Retention & Welfare Efficacy Portal

Welcome to the User Guide for the **Student Retention & Welfare Efficacy Portal**. This guide is written for state education officers, district administrators, and data analysts to help you run the application, navigate all 7 modules, filter metrics, and query the AI Agent.

---

## 🚀 1. How to Launch the Web Portal

1. Open your terminal or command prompt.
2. Navigate to the project folder:
   ```bash
   cd C:\Users\mangi\Desktop\Datathon
   ```
3. Launch the web application:
   ```bash
   streamlit run dashboard/app.py
   ```
4. The dashboard will automatically open in your default web browser at `http://localhost:8501`.

---

## 🌐 2. Using the Website Navigation & Global Filters

### Website Top Navigation Bar
Located at the top of the screen, click any tab to open the corresponding module:
- **📊 Executive Command Center**: High-level statewide overview.
- **📅 Attendance Intelligence**: Attendance rate trends and proxy marking audits.
- **🍲 MDM Procurement Intelligence**: Mid-Day Meal supply volume and expenditure analytics.
- **🏫 Infrastructure & Amenities**: Five-point amenity audit across schools.
- **🎓 FLN Learning Outcomes**: Standardized assessment performance by grade and subject.
- **⚠️ Welfare & Retention Risk Tracker**: Priority action list of high-risk schools.
- **🤖 Real Gemini AI Agent**: Plain-English AI query interface powered by Gemini 3.6 Flash.

### Global Filter Controls
Directly below the top navigation bar, you can filter all metrics across the entire application:
- **Filter District Name**: Select a specific district (e.g., `Amritsar`, `Ludhiana`, `Moga`) or `All Districts`.
- **Filter School Type / Level**: Select a school level (`Primary`, `Upper Primary`, `Secondary`, `Higher Secondary`) or `All Types`.
- The **Active Filter Scope** box shows your current active scope.

---

## 🤖 3. How to Query the Gemini AI Agent

Click on the **🤖 Real Gemini AI Agent** tab to ask plain-English questions about state education data:

1. **Quick Prompt Buttons**: Click any of the 4 sample audit buttons (`👥 Enrollment by District`, `🚨 Sunday Attendance Anomalies`, `⚡ Electricity vs Test Scores`, `🍲 MDM Cost by Vendor`) to quickly load common questions.
2. **Custom Text Query**: Type any natural language question into the query text input box, such as:
   - *"Which district has the lowest average attendance rate?"*
   - *"Show total MDM expenditure by vendor."*
   - *"Compare test scores between schools with and without drinking water."*
3. Click **Run Live AI Query**.
4. The AI Agent will:
   - Translate your question into a DuckDB SQL query.
   - Execute the query against the governed warehouse.
   - Display a formal executive narrative summary.
   - Render a high-contrast Plotly chart.
   - Show the formally labeled data table.

---

## ⚠️ 4. Understanding the Welfare & Retention Risk Tracker

On the **⚠️ Welfare & Retention Risk Tracker** tab, schools are ranked by a composite risk score ($0 - 100$):
- **🔴 High Risk (Score $\ge 70$)**: Schools requiring immediate administrative intervention due to low attendance, low test scores, or high infrastructure deficits.
- **🟠 Moderate Risk (Score $40 - 69$)**: Schools requiring targeted departmental support.
- **🟢 Low Risk (Score $< 40$)**: Stable operational status.

Use the priority action table to filter by district and export data for field inspections.

---

## ❓ 5. Troubleshooting & FAQ

- **Database Lock Warning**: If you encounter a database lock error, ensure no other terminal window is writing to `education_warehouse.duckdb`. The dashboard runs in read-only mode (`read_only=True`) to prevent locks.
- **Rebuilding Database**: If raw data is updated, run `python -m src.ingestion` followed by `python -m src.analytics` to refresh the database.
