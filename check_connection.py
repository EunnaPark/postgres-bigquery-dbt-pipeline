from getpass import getpass
import psycopg

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
        cursor.execute("""
            SELECT order_id, customer_id, order_date, status, amount
            FROM test.orders
            WHERE order_id IN (910002, 910003, 910004)
            ORDER BY order_id;
        """)

        results = cursor.fetchall()

        for order in results:
            print(order)

        print("Stored orders:", len(results))