from decimal import Decimal
from fastapi import HTTPException
from psycopg.rows import dict_row

def get_check_with_items(cur, check_number):
    cur.execute(
        """
        SELECT c.check_number, c.print_date, c.sum_total, c.vat,
               c.id_employee, e.empl_surname, e.empl_name,
               c.card_number, cc.cust_surname
        FROM "check" c
        JOIN employee e ON e.id_employee = c.id_employee
        LEFT JOIN customer_card cc ON cc.card_number = c.card_number
        WHERE c.check_number = %s
        """,
        (check_number,),
    )
    check = cur.fetchone()
    if check is None:
        return None
    cur.execute(
        """
        SELECT s.UPC, p.product_name, s.product_number, s.selling_price,
               s.product_number * s.selling_price AS line_total
        FROM sale s
        JOIN store_product sp ON sp.UPC = s.UPC
        JOIN product p ON p.id_product = sp.id_product
        WHERE s.check_number = %s
        ORDER BY p.product_name
        """,
        (check_number,),
    )
    check["items"] = cur.fetchall()
    return check

def _attach_items(cur, checks):
    if not checks:
        return checks
    numbers = [c["check_number"] for c in checks]
    cur.execute(
        """
        SELECT s.check_number, p.product_name, s.product_number, s.selling_price,
               s.product_number * s.selling_price AS line_total
        FROM sale s
        JOIN store_product sp ON sp.UPC = s.UPC
        JOIN product p ON p.id_product = sp.id_product
        WHERE s.check_number = ANY(%s)
        ORDER BY p.product_name
        """,
        (numbers,),
    )
    by_check = {}
    for item in cur.fetchall():
        by_check.setdefault(item["check_number"], []).append(item)
    for c in checks:
        c["items"] = by_check.get(c["check_number"], [])
    return checks

def get_checks_by_cashier(cur, id_employee, date_from, date_to):
    cur.execute(
        """
        SELECT check_number, print_date, sum_total, vat, id_employee, card_number
        FROM "check"
        WHERE id_employee = %s
          AND (%s::date IS NULL OR print_date::date >= %s)
          AND (%s::date IS NULL OR print_date::date <= %s)
        ORDER BY print_date
        """,
        (id_employee, date_from, date_from, date_to, date_to),
    )
    return _attach_items(cur, cur.fetchall())

def sum_checks_by_cashier(cur, id_employee, date_from, date_to):
    cur.execute(
        """
        SELECT COALESCE(SUM(sum_total), 0) AS total
        FROM "check"
        WHERE id_employee = %s
          AND (%s::date IS NULL OR print_date::date >= %s)
          AND (%s::date IS NULL OR print_date::date <= %s)
        """,
        (id_employee, date_from, date_from, date_to, date_to),
    )
    return cur.fetchone()["total"]

def get_all_checks(cur, date_from, date_to):
    cur.execute(
        """
        SELECT check_number, print_date, sum_total, vat, id_employee, card_number
        FROM "check"
        WHERE (%s::date IS NULL OR print_date::date >= %s)
          AND (%s::date IS NULL OR print_date::date <= %s)
        ORDER BY print_date
        """,
        (date_from, date_from, date_to, date_to),
    )
    return _attach_items(cur, cur.fetchall())


def sum_checks_all(cur, date_from, date_to):
    cur.execute(
        """
        SELECT COALESCE(SUM(sum_total), 0) AS total
        FROM "check"
        WHERE (%s::date IS NULL OR print_date::date >= %s)
          AND (%s::date IS NULL OR print_date::date <= %s)
        """,
        (date_from, date_from, date_to, date_to),
    )
    return cur.fetchone()["total"]


def product_qty_sold(cur, id_product, date_from, date_to):
    cur.execute(
        """
        SELECT COALESCE(SUM(s.product_number), 0) AS qty
        FROM sale s
        JOIN store_product sp ON sp.UPC = s.UPC
        JOIN "check" c ON c.check_number = s.check_number
        WHERE sp.id_product = %s
          AND (%s::date IS NULL OR c.print_date::date >= %s)
          AND (%s::date IS NULL OR c.print_date::date <= %s)
        """,
        (id_product, date_from, date_from, date_to, date_to),
    )
    return cur.fetchone()["qty"]


def create_check(conn, id_employee, data):
    with conn.transaction():
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT nextval('check_number_sequence')")
            check_number = str(cur.fetchone()["nextval"]).zfill(10) # zfill for 1 -> 0000000001

            # calculating total sum and save rows
            sum_total = Decimal(0)
            sale_rows = []
            for sale_row in data.sales:
                cur.execute( # validating and locking store product
                    """
                    SELECT selling_price, products_number
                    FROM store_product
                    WHERE UPC = %s
                    FOR UPDATE
                    """,
                    (sale_row.UPC,),
                )
                store_product = cur.fetchone()
                if store_product is None:
                    raise HTTPException(404, f"Store product {sale_row.UPC} not found")
                if store_product["products_number"] < sale_row.product_number:
                    raise HTTPException(409, f"Not enough product {sale_row.UPC}")

                sum_total += store_product["selling_price"] * sale_row.product_number
                sale_rows.append((sale_row.UPC, sale_row.product_number, store_product["selling_price"]))

            # customer card discount
            if data.card_number:
                cur.execute(
                    "SELECT percent FROM customer_card WHERE card_number = %s",
                    (data.card_number,),
                )
                customer_card = cur.fetchone()
                if customer_card is None:
                    raise HTTPException(404, "Client card not found")
                sum_total = sum_total * (100 - customer_card["percent"]) / 100

            vat = sum_total * Decimal("0.2")

            cur.execute( # creating check
                """
                INSERT INTO "check"
                    (check_number, id_employee, card_number, print_date, sum_total, vat)
                VALUES (%s, %s, %s, NOW(), %s, %s)
                """,
                (check_number, id_employee, data.card_number, sum_total, vat),
            )

            for upc, product_number, selling_price in sale_rows:
                cur.execute( # creating sale
                    """
                    INSERT INTO sale (UPC, check_number, product_number, selling_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (upc, check_number, product_number, selling_price),
                )
                cur.execute( # updating store_product number
                    """
                    UPDATE store_product
                    SET products_number = products_number - %s
                    WHERE UPC = %s
                    """,
                    (product_number, upc),
                )

    return check_number


def delete_check(cur, check_number):
    cur.execute(
        """
        DELETE FROM "check"
        WHERE check_number = %s
        RETURNING *
        """,
        (check_number,),
    )
    return cur.fetchone()

# Індивідуальне. Запит з групуванням (Дар'я)
def sales_by_cashier(cur, date_from, date_to):
    cur.execute(
        """
        SELECT e.id_employee, e.empl_surname, e.empl_name,
               COUNT(DISTINCT c.check_number)              AS check_count,
               SUM(s.product_number * s.selling_price)     AS total_sum
        FROM employee e
        JOIN "check" c  ON c.id_employee = e.id_employee
        JOIN sale s     ON s.check_number = c.check_number
        WHERE CAST(c.print_date AS DATE) BETWEEN %s AND %s
        GROUP BY e.id_employee, e.empl_surname, e.empl_name
        ORDER BY total_sum DESC
        """,
        (date_from, date_to),
    )
    return cur.fetchall()

# Індивідуальне. Запит з подвійним запереченням (Дар'я)
def categories_all_products_sold(cur):
    cur.execute(
        """
        SELECT cat.category_number, cat.category_name
        FROM category cat
        WHERE NOT EXISTS (
                SELECT 1 FROM product p
                WHERE p.category_number = cat.category_number
                  AND NOT EXISTS (
                      SELECT 1
                      FROM store_product sp
                      JOIN sale s ON s.UPC = sp.UPC
                      WHERE sp.id_product = p.id_product
                  )
              )
        ORDER BY cat.category_name
        """
    )
    return cur.fetchall()