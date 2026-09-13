import re
import duckdb
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from src.analytics import DB_PATH

DEFAULT_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

FORMAL_COLUMN_LABELS = {
    'district': 'District Name',
    'block': 'Block Name',
    'school_id': 'School Identifier',
    'school_name': 'School Name',
    'school_type': 'School Type / Level',
    'medium': 'Instruction Medium',
    'total_enrolled_students': 'Total Student Enrollment',
    'month': 'Academic Month',
    'attendance_date': 'Attendance Date',
    'procurement_date': 'Procurement Date',
    'assessment_date': 'Assessment Date',
    'last_inspection_date': 'Last Inspection Date',
    'grade': 'Grade / Class Level',
    'subject': 'Academic Subject',
    'total_students': 'Enrolled Class Students',
    'present_students': 'Present Student Count',
    'attendance_rate': 'Average Daily Attendance Rate (%)',
    'avg_attendance': 'Average Daily Attendance Rate (%)',
    'avg_attendance_rate': 'Average Daily Attendance Rate (%)',
    'proxy_anomaly_rate': 'Proxy Attendance Anomaly Rate (%)',
    'proxy_anomaly_rate_pct': 'Proxy Attendance Anomaly Rate (%)',
    'proxy_anomaly_records': 'Proxy Anomaly Record Count',
    'impossible_records': 'Impossible Attendance Record Count',
    'teacher_present': 'Teacher Attendance Status',
    'marked_by': 'Attendance Marking Authority',
    'data_quality_status': 'Data Quality Audit Status',
    'vendor_name': 'MDM Supplier Entity Name',
    'grain_type': 'Food Grain Commodity',
    'quantity_kg': 'Procurement Quantity (KG)',
    'total_quantity_kg': 'Total Procurement Quantity (KG)',
    'total_cost': 'Total Procurement Expenditure (₹)',
    'total_cost_rs': 'Total Procurement Expenditure (₹)',
    'cost_per_kg': 'Unit Cost Efficiency (₹/KG)',
    'payment_status': 'Supplier Payment Status',
    'electricity_status': 'Electricity Facility Status',
    'has_electricity': 'Electricity Availability Status',
    'has_drinking_water': 'Drinking Water Availability Status',
    'has_functional_toilet': 'Functional Toilet Availability Status',
    'has_boundary_wall': 'Boundary Wall Security Status',
    'has_playground': 'Playground Facility Status',
    'infrastructure_score': 'Infrastructure Health Score (%)',
    'infrastructure_deficit_pct': 'Infrastructure Deficit Index (%)',
    'avg_infra_deficit': 'Infrastructure Deficit Index (%)',
    'deficit': 'Infrastructure Deficit Index (%)',
    'grading_scale_raw': 'Ingested FLN Grading Scale',
    'avg_score_raw': 'Raw Score Record',
    'score_percentage': 'Standardized FLN Score (%)',
    'avg_fln_score': 'Average FLN Test Score (%)',
    'fln_score': 'Average FLN Test Score (%)',
    'assessment_count': 'Total Assessments Evaluated',
    'welfare_risk_score': 'Welfare & Retention Risk Index (0-100)',
    'welfare_risk_category': 'Welfare Risk Classification',
    'school_count': 'School Count',
    'total_schools': 'Total Reporting Schools',
    'total_records': 'Total Transaction Records',
    'sunday_anomaly_count': 'Sunday Proxy Marking Record Count'
}

def format_formal_label(col_name):
    if not col_name:
        return ""
    clean_k = str(col_name).strip().lower()
    if clean_k in FORMAL_COLUMN_LABELS:
        return FORMAL_COLUMN_LABELS[clean_k]
    return str(col_name).replace('_', ' ').strip().title()

DATABASE_SCHEMA_CONTEXT = """
Database Schema & Governed Analytical Views in DuckDB:

1. vw_district_summary:
   - district (VARCHAR): District Name (Amritsar, Bathinda, Ferozepur, Jalandhar, Ludhiana, Moga, Patiala, Sangrur)
   - total_schools (BIGINT): Count of schools
   - total_enrolled_students (DOUBLE): Sum of enrolled students
   - avg_attendance_rate (DOUBLE): District average daily attendance %
   - proxy_anomaly_rate (DOUBLE): District proxy attendance anomaly %
   - avg_infrastructure_score (DOUBLE): District infrastructure score %
   - avg_infrastructure_deficit (DOUBLE): District infrastructure deficit %
   - avg_fln_score (DOUBLE): District average FLN test score %
   - total_mdm_quantity_kg (DOUBLE): District total MDM food grain procurement in KG
   - total_mdm_cost (DOUBLE): District total MDM expenditure in INR (₹)

2. vw_school_attendance_daily:
   - record_id, school_id, school_name, district, block, school_type
   - attendance_date (VARCHAR / DATE): Date of attendance YYYY-MM-DD
   - grade, total_students, present_students, attendance_rate, teacher_present, marked_by
   - is_impossible_attendance (BOOLEAN): TRUE if present > total
   - is_proxy_attendance (BOOLEAN): TRUE if 100% attendance recorded on Sunday/holiday
   - is_weekend (BOOLEAN), data_quality_status (VARCHAR)

3. vw_school_attendance_monthly:
   - district, month (YYYY-MM), total_records, avg_attendance_rate, proxy_anomaly_records, impossible_records, proxy_anomaly_rate_pct

4. vw_school_mdm_summary:
   - procurement_id, school_id, school_name, district, block, procurement_date
   - vendor_name (VARCHAR): Standardized supplier name (Kumar Enterprises, Singh Agro Group, Sharma Traders, Goyal Mills)
   - grain_type (VARCHAR): Commodity (Rice, Wheat, Pulses, Oil)
   - quantity_kg (DOUBLE): Net volume in KG
   - total_cost (DOUBLE): Expenditure in ₹
   - cost_per_kg (DOUBLE): Unit cost ₹/KG
   - payment_status (VARCHAR): Paid, Pending, Unknown

5. vw_school_infrastructure_summary:
   - school_id, school_name, district, block, last_inspection_date
   - has_electricity (BOOLEAN), has_drinking_water (BOOLEAN), has_functional_toilet (BOOLEAN), has_boundary_wall (BOOLEAN), has_playground (BOOLEAN)
   - infrastructure_score (DOUBLE), infrastructure_deficit_pct (DOUBLE), inspector_name, remarks

6. vw_school_test_summary / fact_test_scores:
   - assessment_id, school_id, school_name, district, block, assessment_date, grade, subject (Mathematics, English, Hindi, Punjabi, EVS, Science), grading_scale_raw, avg_score_raw, score_percentage (DOUBLE)

7. fact_welfare_risk:
   - school_id, school_name, district, block, total_enrolled_students, avg_attendance_rate, proxy_anomaly_rate, infrastructure_deficit_pct, infrastructure_score, avg_fln_score, total_mdm_kg, welfare_risk_score (DOUBLE 0-100), welfare_risk_category (High Risk, Moderate Risk, Low Risk)
"""


class RealDynamicAIAgent:
    """
    Enterprise Real AI Agent powered by Gemini Generative AI.
    Converts free-form natural language into live DuckDB SQL queries, executes queries live,
    selects Plotly visualizations, and generates executive narratives.
    """
    def __init__(self, db_path=DB_PATH, conn=None, api_key=None):
        self.db_path = db_path
        self.conn = conn
        self.api_key = api_key or DEFAULT_GEMINI_API_KEY
        self._setup_gemini()

    def _setup_gemini(self):
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-3.6-flash')
            self.has_llm = True
        except Exception:
            try:
                self.model = genai.GenerativeModel('gemini-flash-latest')
                self.has_llm = True
            except Exception:
                self.has_llm = False

    def _get_conn(self):
        if self.conn is not None:
            return self.conn, False
        return duckdb.connect(self.db_path, read_only=True), True

    def _execute_sql(self, sql_query):
        conn, should_close = self._get_conn()
        try:
            df = conn.execute(sql_query).df()
            if should_close:
                conn.close()
            return df, None
        except Exception as e:
            if should_close:
                conn.close()
            return None, str(e)

    def process_query(self, user_query):
        """
        Processes natural language question using Gemini LLM Text-to-SQL engine + DuckDB live execution.
        """
        raw_q = user_query.strip()
        sql_query = None
        df = None
        err = None
        intent_type = 'BAR_RANKING'

        # Attempt 1: Gemini LLM Text-to-SQL Generation
        if self.has_llm:
            sql_query = self._llm_text_to_sql(raw_q)
            if sql_query:
                df, err = self._execute_sql(sql_query)

                # Self-correction if SQL error occurs
                if err is not None and sql_query:
                    sql_query_corrected = self._llm_correct_sql(raw_q, sql_query, err)
                    if sql_query_corrected:
                        df_corr, err_corr = self._execute_sql(sql_query_corrected)
                        if err_corr is None and df_corr is not None:
                            sql_query = sql_query_corrected
                            df = df_corr
                            err = None

        # Attempt 2: Fallback to NLP SQL Query Planner if LLM unavailable or SQL failed
        if df is None or len(df) == 0 or err is not None:
            sql_query, intent_type = self._fallback_dynamic_sql(raw_q)
            df, err = self._execute_sql(sql_query)

        if df is None or len(df) == 0:
            return {
                'status': 'UNSUPPORTED',
                'query': user_query,
                'chart': None,
                'summary': f"I analyzed your question: **'{user_query}'**, but could not locate matching records in the governed database. Please try asking about attendance trends, district performance, infrastructure amenities, meal procurement costs, or school welfare risks.",
                'data': None,
                'sql': sql_query
            }

        # Format DataFrame Column Headers Formally
        formatted_df = df.copy()
        formatted_df.columns = [format_formal_label(c) for c in formatted_df.columns]

        # Dynamic Plotly Visualization Selection
        chart, chart_type = self._create_dynamic_plotly_chart(df, intent_type, raw_q)

        # Dynamic LLM Narrative Summary Generation
        summary = self._generate_llm_executive_summary(raw_q, sql_query, df)

        return {
            'status': 'SUCCESS',
            'query': user_query,
            'chart_type': chart_type,
            'chart': chart,
            'summary': summary,
            'data': formatted_df,
            'sql': sql_query
        }

    def _llm_text_to_sql(self, user_query):
        prompt = f"""
You are the Lead Data Engineer & Database Architect for the State Education Department.
Convert the following natural language user question into a single valid executable DuckDB SQL query.

{DATABASE_SCHEMA_CONTEXT}

Instructions:
1. Output ONLY the raw executable DuckDB SQL query inside a markdown code block: ```sql <QUERY> ```.
2. Do not use any tables or columns not defined in the schema.
3. Use appropriate aggregated functions (AVG, SUM, COUNT), GROUP BY, ORDER BY, and LIMIT where appropriate.
4. Keep queries efficient and clean.

User Question: "{user_query}"
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                return match.group(1).strip()
            # If no code block, return raw stripped text if starts with SELECT
            if text.upper().startswith('SELECT'):
                return text
        except Exception:
            pass
        return None

    def _llm_correct_sql(self, user_query, broken_sql, error_msg):
        prompt = f"""
The following DuckDB SQL query generated an error:
Broken SQL: {broken_sql}
Error Message: {error_msg}

{DATABASE_SCHEMA_CONTEXT}

User Question: "{user_query}"

Please return ONLY the corrected, executable DuckDB SQL query inside a ```sql <QUERY> ``` block.
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
        return None

    def _generate_llm_executive_summary(self, user_query, sql_query, df):
        """Generates dynamic executive textual analysis via Gemini LLM based on actual DuckDB query results."""
        if self.has_llm and len(df) > 0:
            sample_data = df.head(15).to_string(index=False)
            prompt = f"""
You are the Chief Data Officer presenting analytics to the State Education Minister.
Analyze the following SQL query result data to answer the user's question concisely, formally, and professionally.

User Question: "{user_query}"
SQL Query Executed: {sql_query}
Data Result (Sample):
{sample_data}

Instructions:
1. Provide a clear, formal executive summary using bullet points where appropriate.
2. Highlight key numerical facts, highest/lowest performing entities, totals, or state averages.
3. Do not invent numbers or facts outside the provided data.
4. Keep the response formal, title-cased, and structured.
"""
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                pass

        # Fallback Rule-Based Executive Summary
        n_rows = len(df)
        cols = list(df.columns)
        num_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
        cat_cols = [c for c in cols if df[c].dtype == 'object' or str(df[c].dtype).startswith('str')]

        summary_parts = [f"**Executive Data Analysis**: Processed **{n_rows} reporting entities** from the State Education Department's governed database."]

        if num_cols and cat_cols:
            n_col = num_cols[0]
            c_col = cat_cols[0]

            max_idx = df[n_col].idxmax()
            min_idx = df[n_col].idxmin()

            max_entity = df.loc[max_idx, c_col]
            max_val = df.loc[max_idx, n_col]

            min_entity = df.loc[min_idx, c_col]
            min_val = df.loc[min_idx, n_col]

            avg_val = df[n_col].mean()

            n_label = format_formal_label(n_col)
            summary_parts.append(
                f"- **Highest Metric**: **{max_entity}** recorded the highest {n_label} at **{max_val:,.2f}**.\n"
                f"- **Lowest Metric**: **{min_entity}** recorded the lowest {n_label} at **{min_val:,.2f}**.\n"
                f"- **Ecosystem Average**: State-wide average across all evaluated entities stands at **{avg_val:,.2f}**."
            )
        return "\n\n".join(summary_parts)

    def _fallback_dynamic_sql(self, query_text):
        q = query_text.lower()
        districts = ['amritsar', 'bathinda', 'ferozepur', 'jalandhar', 'ludhiana', 'moga', 'patiala', 'sangrur']
        matched_dist = None
        for d in districts:
            if d in q:
                matched_dist = d.title()
                break

        limit_match = re.search(r'top\s+(\d+)|first\s+(\d+)|limit\s+(\d+)', q)
        limit_n = 10
        if limit_match:
            limit_n = int(limit_match.group(1) or limit_match.group(2) or limit_match.group(3))

        if 'monthly' in q or 'trend' in q or ('attendance' in q and ('time' in q or 'month' in q)):
            where = f"WHERE district = '{matched_dist}'" if matched_dist else "WHERE month IS NOT NULL"
            sql = f"SELECT month, AVG(avg_attendance_rate) AS avg_attendance_rate FROM vw_school_attendance_monthly {where} GROUP BY month ORDER BY month"
            return sql, 'TIME_SERIES'
        elif 'sunday' in q or 'proxy' in q or 'anomaly' in q:
            where_clause = "WHERE is_proxy_attendance = TRUE"
            if matched_dist:
                where_clause += f" AND district = '{matched_dist}'"
            sql = f"SELECT school_id, school_name, district, attendance_date, present_students, total_students, marked_by FROM vw_school_attendance_daily {where_clause} ORDER BY attendance_date DESC LIMIT {limit_n}"
            return sql, 'TABLE_LIST'
        elif 'test' in q or 'score' in q or 'fln' in q:
            if 'electricity' in q:
                sql = "SELECT CASE WHEN i.has_electricity THEN 'Functional Electricity' ELSE 'No Functional Electricity' END AS electricity_status, AVG(t.score_percentage) AS avg_fln_score FROM vw_school_test_summary t JOIN dim_infrastructure_current i ON t.school_id = i.school_id WHERE i.has_electricity IS NOT NULL GROUP BY electricity_status"
                return sql, 'COMPARISON_BAR'
            sql = "SELECT district, AVG(avg_fln_score) AS avg_fln_score FROM vw_district_summary WHERE district IS NOT NULL GROUP BY district ORDER BY avg_fln_score ASC"
            return sql, 'BAR_RANKING'
        elif 'mdm' in q or 'vendor' in q or 'cost' in q or 'meal' in q:
            sql = f"SELECT vendor_name, SUM(total_cost) AS total_cost_rs, SUM(quantity_kg) AS total_quantity_kg FROM vw_school_mdm_summary WHERE vendor_name IS NOT NULL GROUP BY vendor_name ORDER BY total_cost_rs DESC LIMIT {limit_n}"
            return sql, 'BAR_RANKING'
        elif 'risk' in q or 'welfare' in q:
            sql = f"SELECT school_id, school_name, district, block, welfare_risk_score, welfare_risk_category, avg_attendance_rate, avg_fln_score, infrastructure_deficit_pct FROM fact_welfare_risk ORDER BY welfare_risk_score DESC LIMIT {limit_n}"
            return sql, 'TABLE_LIST'
        else:
            sql = "SELECT district, AVG(avg_attendance_rate) AS avg_attendance_rate, AVG(avg_fln_score) AS avg_fln_score FROM vw_district_summary WHERE district IS NOT NULL GROUP BY district ORDER BY avg_attendance_rate DESC"
            return sql, 'BAR_RANKING'

    def _create_dynamic_plotly_chart(self, df, intent_type, user_query):
        cols = list(df.columns)
        if len(cols) == 0 or len(df) == 0:
            return None, 'table'

        cat_cols = [c for c in cols if df[c].dtype == 'object' or str(df[c].dtype).startswith('str')]
        num_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]

        x_col = cat_cols[0] if cat_cols else cols[0]
        y_col = num_cols[0] if num_cols else (cols[1] if len(cols) > 1 else cols[0])

        x_label = format_formal_label(x_col)
        y_label = format_formal_label(y_col)

        # Helper for dynamic comparative Y-axis range scaling & labels
        def apply_comparative_scaling(fig, y_series, is_horizontal=False, is_line=False):
            if y_series is not None and not y_series.empty:
                vals = y_series.dropna().tolist()
                if vals:
                    min_v, max_v = min(vals), max(vals)
                    diff = max_v - min_v
                    padding = max(diff * 0.25, max_v * 0.05) if diff > 0 else (max_v * 0.1 if max_v != 0 else 1.0)
                    lower_b = max(0, min_v - padding) if min_v >= 0 else min_v - padding
                    upper_b = max_v + padding
                    
                    if not is_line:
                        fmt = '%{y:.1f}%' if any(k in str(y_series.name).lower() for k in ['rate', 'score', 'pct', 'percent']) else '%{y:,.1f}'
                        if is_horizontal:
                            fmt_h = '%{x:.1f}%' if any(k in str(y_series.name).lower() for k in ['rate', 'score', 'pct', 'percent']) else '%{x:,.1f}'
                            fig.update_traces(texttemplate=fmt_h, textposition='outside', cliponaxis=False)
                            fig.update_layout(xaxis=dict(range=[lower_b, upper_b]))
                        else:
                            fig.update_traces(texttemplate=fmt, textposition='outside', cliponaxis=False)
                            fig.update_layout(yaxis=dict(range=[lower_b, upper_b]))
                    else:
                        fig.update_layout(yaxis=dict(range=[lower_b, upper_b]))
            return fig

        # 1. Time Series Line Chart
        if intent_type == 'TIME_SERIES' or any('month' in c.lower() or 'date' in c.lower() for c in cols):
            time_col = [c for c in cols if 'month' in c.lower() or 'date' in c.lower()][0]
            val_col = num_cols[0] if num_cols else cols[1]

            fig = px.line(
                df, x=time_col, y=val_col,
                title=f"Academic Timeline Analysis: {format_formal_label(val_col)}",
                labels={time_col: format_formal_label(time_col), val_col: format_formal_label(val_col)},
                markers=True
            )
            fig.update_traces(line_color='#38bdf8', line_width=3, marker=dict(size=8, color='#0284c7'), hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>')
            fig = apply_comparative_scaling(fig, df[val_col], is_line=True)
            fig.update_layout(
                template='plotly_dark',
                margin=dict(l=50, r=40, t=90, b=50),
                title=dict(font=dict(size=14, color="#f8fafc"), x=0.0, xanchor='left', y=0.98, yanchor='top'),
                legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1.0, title_text="")
            )
            return fig, 'line'

        # 2. Pie / Donut Chart
        elif intent_type == 'PIE_CHART' or (len(df) <= 8 and len(cat_cols) >= 1 and len(num_cols) >= 1 and 'grain' in user_query.lower()):
            fig = px.pie(
                df, names=x_col, values=y_col,
                title=f"Distribution Breakdown: {y_label} by {x_label}",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(template='plotly_dark', margin=dict(l=40, r=40, t=60, b=40))
            return fig, 'pie'

        # 3. Bar Chart (Rankings & Comparisons)
        elif len(cat_cols) >= 1 and len(num_cols) >= 1:
            sample_str_len = df[x_col].astype(str).str.len().max()
            if sample_str_len > 15 or len(df) > 12:
                fig = px.bar(
                    df, x=y_col, y=x_col, orientation='h',
                    title=f"Comparative Audit Ranking: {y_label} by {x_label}",
                    labels={x_col: x_label, y_col: y_label},
                    color=y_col, color_continuous_scale='Blues'
                )
                fig = apply_comparative_scaling(fig, df[y_col], is_horizontal=True)
            else:
                fig = px.bar(
                    df, x=x_col, y=y_col,
                    title=f"Comparative Audit Analysis: {y_label} by {x_label}",
                    labels={x_col: x_label, y_col: y_label},
                    color=y_col, color_continuous_scale='Viridis'
                )
                fig = apply_comparative_scaling(fig, df[y_col], is_horizontal=False)
            fig.update_layout(template='plotly_dark', margin=dict(l=40, r=40, t=60, b=40))
            return fig, 'bar'

        # 4. Scatter Plot (2 Numeric Columns)
        elif len(num_cols) >= 2:
            num_x, num_y = num_cols[0], num_cols[1]
            try:
                fig = px.scatter(
                    df, x=num_x, y=num_y,
                    title=f"Correlation Assessment: {format_formal_label(num_y)} vs {format_formal_label(num_x)}",
                    labels={num_x: format_formal_label(num_x), num_y: format_formal_label(num_y)},
                    trendline='ols', color=cat_cols[0] if cat_cols else None
                )
            except Exception:
                fig = px.scatter(
                    df, x=num_x, y=num_y,
                    title=f"Correlation Assessment: {format_formal_label(num_y)} vs {format_formal_label(num_x)}",
                    labels={num_x: format_formal_label(num_x), num_y: format_formal_label(num_y)},
                    color=cat_cols[0] if cat_cols else None
                )
            fig.update_traces(marker=dict(size=10))
            fig.update_layout(template='plotly_dark', margin=dict(l=40, r=40, t=60, b=40))
            return fig, 'scatter'

        # Fallback to Table
        return None, 'table'
