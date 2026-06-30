"""
analysis.py
End-to-end analysis pipeline:
1. Load & clean raw transaction data
2. Exploratory Data Analysis (revenue trends, category performance, payment mix)
3. RFM (Recency, Frequency, Monetary) customer segmentation
4. Cohort retention analysis
5. Save processed datasets + chart images for the README / report
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 110

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
IMAGES = ROOT / "images"

# ---------------------------------------------------------------
# 1. Load & clean
# ---------------------------------------------------------------
orders = pd.read_csv(DATA_RAW / "orders.csv", parse_dates=["order_date"])
customers = pd.read_csv(DATA_RAW / "customers.csv", parse_dates=["signup_date"])

# Keep only successfully delivered orders for revenue analysis
delivered = orders[orders["order_status"] == "Delivered"].copy()

print(f"Total orders: {len(orders):,} | Delivered: {len(delivered):,} "
      f"({len(delivered)/len(orders):.1%})")

df = delivered.merge(customers, on="customer_id", how="left")
df["order_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()

# ---------------------------------------------------------------
# 2. EDA
# ---------------------------------------------------------------

# --- Monthly revenue trend ---
monthly_rev = df.groupby("order_month")["net_amount"].sum().reset_index()
plt.figure(figsize=(10, 5))
sns.lineplot(data=monthly_rev, x="order_month", y="net_amount", marker="o")
plt.title("Monthly Net Revenue Trend (2024–2025)")
plt.ylabel("Net Revenue (₹)")
plt.xlabel("Month")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(IMAGES / "01_monthly_revenue_trend.png")
plt.close()

# --- Revenue by category ---
cat_rev = df.groupby("category")["net_amount"].sum().sort_values(ascending=False).reset_index()
plt.figure(figsize=(9, 5))
sns.barplot(data=cat_rev, x="net_amount", y="category", hue="category", legend=False)
plt.title("Total Revenue by Product Category")
plt.xlabel("Net Revenue (₹)")
plt.ylabel("")
plt.tight_layout()
plt.savefig(IMAGES / "02_revenue_by_category.png")
plt.close()

# --- Order status breakdown (incl. cancelled/returned) ---
status_counts = orders["order_status"].value_counts(normalize=True).reset_index()
status_counts.columns = ["order_status", "pct"]
plt.figure(figsize=(6, 6))
plt.pie(status_counts["pct"], labels=status_counts["order_status"], autopct="%1.1f%%",
        startangle=90, colors=sns.color_palette("muted"))
plt.title("Order Status Breakdown")
plt.tight_layout()
plt.savefig(IMAGES / "03_order_status_breakdown.png")
plt.close()

# --- Payment method mix ---
pay_counts = df["payment_method"].value_counts().reset_index()
pay_counts.columns = ["payment_method", "orders"]
plt.figure(figsize=(8, 5))
sns.barplot(data=pay_counts, x="orders", y="payment_method", hue="payment_method", legend=False)
plt.title("Orders by Payment Method")
plt.xlabel("Number of Orders")
plt.ylabel("")
plt.tight_layout()
plt.savefig(IMAGES / "04_payment_method_mix.png")
plt.close()

# --- Revenue by city tier ---
tier_rev = df.groupby("city_tier")["net_amount"].sum().sort_values(ascending=False).reset_index()
plt.figure(figsize=(7, 5))
sns.barplot(data=tier_rev, x="city_tier", y="net_amount", hue="city_tier", legend=False)
plt.title("Revenue by City Tier")
plt.ylabel("Net Revenue (₹)")
plt.xlabel("")
plt.tight_layout()
plt.savefig(IMAGES / "05_revenue_by_city_tier.png")
plt.close()

# ---------------------------------------------------------------
# 3. RFM Segmentation
# ---------------------------------------------------------------
snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

rfm = df.groupby("customer_id").agg(
    recency=("order_date", lambda x: (snapshot_date - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("net_amount", "sum"),
).reset_index()

# Score 1 (worst) - 5 (best) using quintiles
rfm["R_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]


def segment_customer(row):
    if row["RFM_score"] >= 13:
        return "Champions"
    elif row["RFM_score"] >= 10:
        return "Loyal Customers"
    elif row["RFM_score"] >= 7:
        return "Potential Loyalists"
    elif row["RFM_score"] >= 5:
        return "At Risk"
    else:
        return "Lost / Hibernating"


rfm["segment"] = rfm.apply(segment_customer, axis=1)
rfm.to_csv(DATA_PROCESSED / "rfm_segments.csv", index=False)

seg_summary = rfm.groupby("segment").agg(
    customers=("customer_id", "count"),
    avg_recency=("recency", "mean"),
    avg_frequency=("frequency", "mean"),
    avg_monetary=("monetary", "mean"),
).sort_values("avg_monetary", ascending=False)
seg_summary.to_csv(DATA_PROCESSED / "rfm_segment_summary.csv")

print("\nRFM Segment Summary:")
print(seg_summary.round(1))

plt.figure(figsize=(9, 5))
seg_counts = rfm["segment"].value_counts().reset_index()
seg_counts.columns = ["segment", "customers"]
sns.barplot(data=seg_counts, x="customers", y="segment", hue="segment", legend=False,
            order=seg_counts.sort_values("customers", ascending=False)["segment"])
plt.title("Customer Count by RFM Segment")
plt.xlabel("Number of Customers")
plt.ylabel("")
plt.tight_layout()
plt.savefig(IMAGES / "06_rfm_segment_distribution.png")
plt.close()

# ---------------------------------------------------------------
# 4. Cohort Retention Analysis
# ---------------------------------------------------------------
df["cohort_month"] = df.groupby("customer_id")["order_month"].transform("min")
df["cohort_index"] = (
    (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12
    + (df["order_month"].dt.month - df["cohort_month"].dt.month)
)

cohort_data = df.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().reset_index()
cohort_pivot = cohort_data.pivot(index="cohort_month", columns="cohort_index", values="customer_id")
cohort_size = cohort_pivot.iloc[:, 0]
retention = cohort_pivot.divide(cohort_size, axis=0).round(3)
retention.to_csv(DATA_PROCESSED / "cohort_retention.csv")

plt.figure(figsize=(12, 7))
sns.heatmap(retention.iloc[:, :12], annot=True, fmt=".0%", cmap="Blues", vmin=0, vmax=0.5)
plt.title("Monthly Cohort Retention Heatmap")
plt.xlabel("Months Since First Purchase")
plt.ylabel("Cohort Month")
plt.tight_layout()
plt.savefig(IMAGES / "07_cohort_retention_heatmap.png")
plt.close()

# ---------------------------------------------------------------
# 5. Save cleaned master dataset
# ---------------------------------------------------------------
df.to_csv(DATA_PROCESSED / "cleaned_orders.csv", index=False)

print("\nAnalysis complete. Charts saved to /images, processed data saved to /data/processed.")
