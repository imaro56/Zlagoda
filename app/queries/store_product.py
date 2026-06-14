def get_store_product(cur, upc):
    cur.execute(
        """
        SELECT * FROM store_product 
        WHERE UPC = %s
        """,
        (upc,))
    return cur.fetchone()


def get_all_store_products(cur):
    cur.execute(
        """
        SELECT * FROM store_product
        ORDER BY products_number DESC
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
        SELECT store_product.*, product_name, characteristics FROM store_product
        JOIN product USING (id_product)
        WHERE UPC = %s
        """,
        (upc,))
    return cur.fetchone()


def get_promotional_store_products(cur):
    cur.execute(
        """
        SELECT * FROM store_product
        WHERE promotional_product = TRUE
        ORDER BY products_number DESC
        """)
    return cur.fetchall()


def get_non_promotional_store_products(cur):
    cur.execute(
        """
        SELECT * FROM store_product
        WHERE promotional_product = FALSE
        ORDER BY products_number DESC
        """)
    return cur.fetchall()