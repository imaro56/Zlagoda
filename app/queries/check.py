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
        WHERE id_employee = %s AND print_date::date BETWEEN %s AND %s
        ORDER BY print_date
        """,
        (id_employee, date_from, date_to),
    )
    return _attach_items(cur, cur.fetchall())

def sum_checks_by_cashier(cur, id_employee, date_from, date_to):
    cur.execute(
        """
        SELECT COALESCE(SUM(sum_total), 0) AS total
        FROM "check"
        WHERE id_employee = %s AND print_date::date BETWEEN %s AND %s
        """,
        (id_employee, date_from, date_to),
    )
    return cur.fetchone()["total"]

def get_all_checks(cur, date_from, date_to):
    cur.execute(
        """
        SELECT check_number, print_date, sum_total, vat, id_employee, card_number
        FROM "check"
        WHERE print_date::date BETWEEN %s AND %s
        ORDER BY print_date
        """,
        (date_from, date_to),
    )
    return _attach_items(cur, cur.fetchall())


def sum_checks_all(cur, date_from, date_to):
    cur.execute(
        """
        SELECT COALESCE(SUM(sum_total), 0) AS total
        FROM "check"
        WHERE print_date::date BETWEEN %s AND %s
        """,
        (date_from, date_to),
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
          AND c.print_date::date BETWEEN %s AND %s
        """,
        (id_product, date_from, date_to),
    )
    return cur.fetchone()["qty"]