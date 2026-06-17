def get_store_product(cur, upc):
    cur.execute(
        """
        SELECT * FROM store_product 
        WHERE UPC = %s
        """,
        (upc,))
    return cur.fetchone()


def get_all_store_products(cur, sort="quantity"):
    order_by = {"quantity": "products_number DESC", "name": "product_name ASC"}[sort]
    cur.execute(
        f"""
        SELECT * FROM store_product
        JOIN product USING (id_product)
        JOIN category USING (category_number)
        ORDER BY {order_by}
        """)
    return cur.fetchall()


def create_store_product(cur, upc, data):
    cur.execute(
        """
        INSERT INTO store_product (UPC, UPC_prom, id_product, selling_price, products_number, promotional_product)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (upc, data['UPC_prom'], data['id_product'], data['selling_price'], data['products_number'], data["promotional_product"]))
    return cur.fetchone()


def update_store_product(cur, upc, data):
    cur.execute(
        """
        UPDATE store_product
        SET UPC_prom = %s, id_product = %s, selling_price = %s, products_number = %s, promotional_product = %s
        WHERE UPC = %s
        RETURNING *
        """,
        (data['UPC_prom'], data['id_product'], data['selling_price'], data['products_number'], data["promotional_product"], upc))
    return cur.fetchone()


def delete_store_product(cur, upc):
    cur.execute(
        """
        DELETE FROM store_product
        WHERE UPC = %s
        RETURNING *
        """,
        (upc,))
    return cur.fetchone()


def get_store_product_full(cur, upc):
    cur.execute(
        """
        SELECT store_product.*, product_name, characteristics, category_name FROM store_product
        JOIN product USING (id_product)
        JOIN category USING (category_number)
        WHERE UPC = %s
        """,
        (upc,))
    return cur.fetchone()


def get_promotional_store_products(cur, sort="quantity"):
    order_by = {"quantity": "products_number DESC", "name": "product_name ASC"}[sort]
    cur.execute(
        f"""
        SELECT * FROM store_product
        JOIN product USING (id_product)
        JOIN category USING (category_number)
        WHERE promotional_product = TRUE
        ORDER BY {order_by}
        """)
    return cur.fetchall()


def get_non_promotional_store_products(cur, sort="quantity"):
    order_by = {"quantity": "products_number DESC", "name": "product_name ASC"}[sort]
    cur.execute(
        f"""
        SELECT * FROM store_product
        JOIN product USING (id_product)
        JOIN category USING (category_number)
        WHERE promotional_product = FALSE
        ORDER BY {order_by}
        """)
    return cur.fetchall()

def reprice_store_product(cur, id_product, new_price):
    cur.execute(
        """
        UPDATE store_product
        SET selling_price = CASE
            WHEN promotional_product = TRUE THEN %s * 0.8
            ELSE %s
        END
        WHERE id_product = %s
        RETURNING *
        """,
        (new_price, new_price, id_product))
    return cur.fetchall()


def create_promotional_store_product(cur, upc, upc_prom, products_number):
    cur.execute(  # insert a promotional product based on the non-promotional product
        # select chooses the non-prom product without promotional product connected
        """
        INSERT INTO store_product (UPC, UPC_prom, id_product, selling_price, products_number, promotional_product)
        SELECT %s, NULL, sp.id_product, sp.selling_price * 0.8, %s, TRUE  
        FROM store_product as sp
        WHERE sp.UPC = %s
            AND sp.promotional_product = FALSE
            AND NOT EXISTS (  
                SELECT 1 FROM store_product 
                WHERE id_product = sp.id_product AND promotional_product = TRUE
            )
        RETURNING *
        """,
        (upc_prom, products_number, upc))
    promo = cur.fetchone()
    if promo:
        cur.execute(  # update UPC_prom for the promotional product
            """
            UPDATE store_product
            SET UPC_prom = %s
            WHERE UPC = %s
            """,
            (upc_prom, upc))
    return promo
