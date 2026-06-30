"""
generate_data.py
Generates a realistic synthetic retail transactions dataset for analysis.
Mimics an e-commerce/retail store's order history over 2 years.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_CUSTOMERS = 1200
N_ORDERS = 9000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)

categories = {
    "Electronics": ["Wireless Earbuds", "Smartphone Case", "Bluetooth Speaker", "Power Bank", "Smartwatch"],
    "Home & Kitchen": ["Non-stick Pan", "Air Fryer", "LED Lamp", "Storage Box", "Water Bottle"],
    "Fashion": ["Cotton T-Shirt", "Running Shoes", "Denim Jacket", "Backpack", "Sunglasses"],
    "Beauty & Personal Care": ["Face Wash", "Moisturizer", "Hair Serum", "Perfume", "Lip Balm"],
    "Groceries": ["Basmati Rice 5kg", "Cooking Oil 1L", "Green Tea", "Almonds 500g", "Protein Bar Pack"],
    "Books & Stationery": ["Notebook Set", "Sketch Pens", "Bestseller Novel", "Planner Diary", "Desk Organizer"],
}

cities_tier = {
    "Mumbai": "Tier 1", "Delhi": "Tier 1", "Bangalore": "Tier 1", "Kanpur": "Tier 2",
    "Pune": "Tier 1", "Lucknow": "Tier 2", "Jaipur": "Tier 2", "Indore": "Tier 2",
    "Patna": "Tier 2", "Bhopal": "Tier 2", "Nagpur": "Tier 3", "Ranchi": "Tier 3",
}

payment_methods = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]
order_status_pool = ["Delivered"] * 90 + ["Cancelled"] * 6 + ["Returned"] * 4

# --- Customers ---
customer_ids = [f"CUST{str(i).zfill(5)}" for i in range(1, N_CUSTOMERS + 1)]
customer_city = np.random.choice(list(cities_tier.keys()), N_CUSTOMERS)
customer_signup = [START_DATE + timedelta(days=int(np.random.uniform(0, 600))) for _ in range(N_CUSTOMERS)]
# Give each customer a "loyalty" weight so order frequency isn't uniform (more realistic)
customer_weight = np.random.gamma(shape=2.0, scale=1.0, size=N_CUSTOMERS)
customer_weight = customer_weight / customer_weight.sum()

customers_df = pd.DataFrame({
    "customer_id": customer_ids,
    "city": customer_city,
    "city_tier": [cities_tier[c] for c in customer_city],
    "signup_date": customer_signup,
})

# --- Orders / Order Items ---
rows = []
order_counter = 1
for _ in range(N_ORDERS):
    cust_idx = np.random.choice(N_CUSTOMERS, p=customer_weight)
    cust_id = customer_ids[cust_idx]
    signup = customer_signup[cust_idx]

    min_day = max(0, (signup - START_DATE).days)
    max_day = (END_DATE - START_DATE).days
    order_date = START_DATE + timedelta(days=int(np.random.uniform(min_day, max_day)))

    category = np.random.choice(list(categories.keys()), p=[0.27, 0.20, 0.20, 0.13, 0.12, 0.08])
    product = np.random.choice(categories[category])

    base_prices = {
        "Electronics": (499, 4999), "Home & Kitchen": (199, 3499), "Fashion": (299, 2499),
        "Beauty & Personal Care": (99, 1299), "Groceries": (49, 899), "Books & Stationery": (49, 799),
    }
    lo, hi = base_prices[category]
    unit_price = round(np.random.uniform(lo, hi), 2)
    quantity = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.45, 0.2, 0.1, 0.15, 0.07, 0.03])
    discount_pct = np.random.choice([0, 5, 10, 15, 20, 30], p=[0.35, 0.2, 0.2, 0.15, 0.07, 0.03])
    gross_amount = round(unit_price * quantity, 2)
    discount_amount = round(gross_amount * discount_pct / 100, 2)
    net_amount = round(gross_amount - discount_amount, 2)

    status = np.random.choice(order_status_pool)
    payment = np.random.choice(payment_methods, p=[0.42, 0.2, 0.15, 0.13, 0.10])

    rows.append({
        "order_id": f"ORD{str(order_counter).zfill(6)}",
        "customer_id": cust_id,
        "order_date": order_date.date(),
        "category": category,
        "product": product,
        "unit_price": unit_price,
        "quantity": quantity,
        "discount_pct": discount_pct,
        "gross_amount": gross_amount,
        "discount_amount": discount_amount,
        "net_amount": net_amount,
        "payment_method": payment,
        "order_status": status,
    })
    order_counter += 1

orders_df = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)

customers_df.to_csv("data/raw/customers.csv", index=False)
orders_df.to_csv("data/raw/orders.csv", index=False)

print(f"Generated {len(customers_df)} customers and {len(orders_df)} orders.")
print(orders_df.head())
