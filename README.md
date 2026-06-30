# 🛍️ Retail Sales & Customer Segmentation Analysis

End-to-end data analysis project on 2 years of retail transaction data — covering exploratory data analysis, RFM customer segmentation, and cohort retention analysis, with the same business logic implemented in both **Python** and **SQL**.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL%2FMySQL-orange)
![Status](https://img.shields.io/badge/Status-Complete-success)

---

## 📌 Project Overview

This project simulates a real-world data analyst task: given raw e-commerce order data, answer key business questions —

- How is revenue trending over time, and by category?
- Which customer segments are most valuable, and which are at risk of churning?
- How well does the business retain customers month over month?

The dataset is synthetically generated (`src/generate_data.py`) to mimic realistic retail behavior — non-uniform customer order frequency, seasonal variation, multiple payment methods, and a small share of cancelled/returned orders — so the analysis reflects the kind of messiness found in real transactional data.

## 🗂️ Repository Structure

```
retail-sales-customer-segmentation/
├── data/
│   ├── raw/                      # Raw generated transaction data
│   │   ├── customers.csv
│   │   └── orders.csv
│   └── processed/                # Outputs of the analysis pipeline
│       ├── cleaned_orders.csv
│       ├── rfm_segments.csv
│       ├── rfm_segment_summary.csv
│       └── cohort_retention.csv
├── notebooks/
│   └── retail_analysis.ipynb     # Main analysis notebook (start here)
├── sql/
│   ├── schema.sql                # Table definitions
│   └── analysis_queries.sql      # 6 business questions answered in SQL (CTEs + window functions)
├── src/
│   ├── generate_data.py          # Synthetic dataset generator
│   └── analysis.py               # Script version of the full pipeline (EDA + RFM + cohorts)
├── images/                       # Exported chart images used in this README
├── requirements.txt
└── README.md
```

## 🔍 Key Findings

| Area | Finding |
|---|---|
| **Revenue trend** | Net revenue shows a steady upward trend with seasonal peaks across the 24-month window |
| **Category mix** | Electronics and Home & Kitchen together drive the largest share of revenue |
| **City tiers** | Tier-1 cities lead in revenue, but Tier-2 cities contribute a meaningful and growing share |
| **Customer segments** | ~20% of customers fall into "At Risk" or "Lost/Hibernating" RFM segments — a clear target for win-back campaigns |
| **Retention** | The steepest drop-off happens between month 0 and month 1, pointing to an onboarding/retention opportunity |
| **Payments** | UPI is the dominant payment method, consistent with broader Indian e-commerce trends |

Full reasoning and recommendations are in the [notebook](notebooks/retail_analysis.ipynb).

## 📊 Visuals

**Monthly Revenue Trend**
![Monthly Revenue Trend](images/01_monthly_revenue_trend.png)

**Revenue by Category**
![Revenue by Category](images/02_revenue_by_category.png)

**Customer Segments (RFM)**
![RFM Segments](images/06_rfm_segment_distribution.png)

**Cohort Retention Heatmap**
![Cohort Retention](images/07_cohort_retention_heatmap.png)

## 🧠 Methodology

### RFM Segmentation
Customers are scored 1–5 on **Recency** (days since last order), **Frequency** (number of orders), and **Monetary** value (total spend) using quintile binning, then combined into a single RFM score used to bucket customers into 5 segments: **Champions, Loyal Customers, Potential Loyalists, At Risk, Lost/Hibernating**.

### Cohort Retention
Customers are grouped by the month of their first purchase. For each cohort, the % of customers still ordering in each subsequent month is calculated and visualized as a heatmap — a standard approach for diagnosing retention/churn patterns.

### SQL Implementation
The same business questions (monthly revenue growth, top customers by LTV, category return rates, RFM via window functions, city-tier revenue contribution, repeat purchase rate) are implemented in `sql/analysis_queries.sql` using **CTEs** for readability and **window functions** (`LAG`, `NTILE`, `SUM() OVER()`) instead of nested subqueries.

## ⚙️ How to Run

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/retail-sales-customer-segmentation.git
cd retail-sales-customer-segmentation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the dataset
python src/generate_data.py

# 4. Run the full analysis pipeline (charts saved to /images, processed data to /data/processed)
python src/analysis.py

# 5. Or explore interactively
jupyter notebook notebooks/retail_analysis.ipynb
```

For the SQL version, load `data/raw/customers.csv` and `data/raw/orders.csv` into a database using `sql/schema.sql`, then run the queries in `sql/analysis_queries.sql`.

## 🛠️ Tech Stack

- **Python**: pandas, numpy, matplotlib, seaborn
- **SQL**: PostgreSQL/MySQL-compatible syntax (CTEs, window functions)
- **Jupyter Notebook** for exploratory analysis and storytelling

## 👤 Author

**Himanshu** — B.Tech CSE student, aspiring Data Analyst.
[LinkedIn](#) · [GitHub](#)

---
*This project uses a synthetically generated dataset for demonstration purposes; no real customer data is used.*
