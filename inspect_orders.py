import pandas as pd

orders = pd.read_csv(
    "data/orders_practice.csv",
    dtype=str,
    keep_default_na=False
)

print(orders.to_string(index=False))
print("\nColumn data types:")
print(orders.dtypes)
print("\nRow count:", len(orders))


print("\nStatus before cleaning:")
print(orders["status"].map(repr))

orders["status"] = orders["status"].str.strip().str.lower()

print("\nStatus after cleaning:")
print(orders["status"].map(repr))

orders["parsed_order_date"] = pd.to_datetime(
    orders["order_date"],
    format="%Y-%m-%d",
    errors="coerce"
)

orders["parsed_amount"] = pd.to_numeric(
    orders["amount"],
    errors="coerce"
)

print("\nDate and amount conversion:")
print(
    orders[
        ["order_id", "order_date", "parsed_order_date", "amount", "parsed_amount"]
    ].to_string(index=False)
)

orders["rejection_reason"] = ""

missing_order_id = orders["order_id"].str.strip().eq("")
invalid_date = orders["parsed_order_date"].isna()
invalid_amount = orders["parsed_amount"].isna()

orders.loc[missing_order_id, "rejection_reason"] += "Missing order ID; "
orders.loc[invalid_date, "rejection_reason"] += "Invalid order date; "
orders.loc[invalid_amount, "rejection_reason"] += "Invalid amount; "



allowed_statuses = ["pending", "completed", "cancelled", "refunded"]

invalid_status = ~orders["status"].isin(allowed_statuses)
negative_amount = orders["parsed_amount"] < 0
zero_completed_amount = (
    orders["status"].eq("completed")
    & orders["parsed_amount"].eq(0)
)

orders.loc[invalid_status, "rejection_reason"] += "Invalid status; "
orders.loc[negative_amount, "rejection_reason"] += "Negative amount; "
orders.loc[zero_completed_amount, "rejection_reason"] += (
    "Completed order amount must be positive; "
)

orders["order_id"] = orders["order_id"].str.strip()

duplicate_order_id = (
    orders["order_id"].ne("")
    & orders["order_id"].duplicated(keep=False)
)

orders.loc[duplicate_order_id, "rejection_reason"] += (
    "Duplicate order ID in file; "
)

for column in ["order_id", "customer_id"]:
    values = orders[column].str.strip()
    orders[column] = values

    missing_id = values.eq("")
    valid_positive_integer = values.str.fullmatch(r"[0-9]+") & (
        pd.to_numeric(values, errors="coerce") > 0
    )
    invalid_id = ~missing_id & ~valid_positive_integer

    if column == "customer_id":
        orders.loc[missing_id, "rejection_reason"] += "Missing customer ID; "

    orders.loc[invalid_id, "rejection_reason"] += (
        f"Invalid {column}: positive integer required; "
    )


print("\nValidation results:")
print(
    orders[
        ["order_id", "order_date", "amount", "rejection_reason"]
    ].to_string(index=False)
)

passed_current_checks = orders["rejection_reason"].eq("")

valid_orders = orders.loc[passed_current_checks].copy()
rejected_orders = orders.loc[~passed_current_checks].copy()

print("\nRows passing current checks:", len(valid_orders))
print("Rejected rows:", len(rejected_orders))

rejected_orders.to_csv("data/rejected_orders.csv", index=False)

valid_orders.to_csv("data/validated_orders.csv", index=False)

print("\nRows passing current checks:")
print(valid_orders.to_string(index=False))




from decimal import Decimal

rows_to_load = []

for _, row in valid_orders.iterrows():
    order = (
        int(row["order_id"]),
        int(row["customer_id"]),
        row["parsed_order_date"].date(),
        row["status"],
        Decimal(row["amount"].strip())
    )
    rows_to_load.append(order)

print("\nRows prepared for PostgreSQL:")
for order in rows_to_load:
    print(order)



    from getpass import getpass
import psycopg

upsert_sql = """
INSERT INTO test.orders (
    order_id, customer_id, order_date, status, amount
)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (order_id) DO UPDATE SET
    customer_id = EXCLUDED.customer_id,
    order_date = EXCLUDED.order_date,
    status = EXCLUDED.status,
    amount = EXCLUDED.amount,
    updated_at = CURRENT_TIMESTAMP;
"""

password = getpass("PostgreSQL password: ")

with psycopg.connect(
    host="127.0.0.1",
    port=9473,
    dbname="portfolio",
    user="postgres",
    password=password,
    connect_timeout=15
) as connection:
    with connection.cursor() as cursor:
        cursor.executemany(upsert_sql, rows_to_load)

print(f"Load committed. Submitted orders: {len(rows_to_load)}")
