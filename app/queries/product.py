def get_product(cur, id_product):
    cur.execute(
        """
        SELECT * FROM product 
        WHERE id_product = %s
        """,
        (id_product,),
    )
    return cur.fetchone()

def get_all_products(cur):
    cur.execute(
        """
        SELECT product.*, category_name FROM product
        JOIN category USING (category_number)
        ORDER BY product_name
        """
    )
    return cur.fetchall()

def get_products_by_category(cur, category_number):
    cur.execute(
        """
        SELECT product.*, category_name FROM product
        JOIN category USING (category_number)
        WHERE category_number=%s
        ORDER BY product_name
        """,
        (category_number,),
    )
    return cur.fetchall()

def get_products_by_name(cur, product_name):
    cur.execute(
        """
        SELECT product.*, category_name FROM product
        JOIN category USING (category_number)
        WHERE product_name ILIKE %s
        ORDER BY product_name
        """,
        (f"%{product_name}%",),
    )
    return cur.fetchall()

def create_product(cur, data):
    cur.execute(
        """
        INSERT INTO product (product_name, category_number, characteristics) 
            VALUES (%s, %s, %s) 
            RETURNING *
        """,
        (data['product_name'], data['category_number'], data['characteristics']),
    )
    return cur.fetchone()

def update_product(cur, id_product, data):
    cur.execute(
        """
        UPDATE product
        SET 
            product_name = %s, category_number = %s, characteristics = %s
        WHERE id_product = %s
        RETURNING *
        """,
        (
            data['product_name'], data['category_number'], data['characteristics'], id_product),
    )
    return cur.fetchone()

def delete_product(cur, id_product):
    cur.execute(
        """
        DELETE FROM product
        WHERE id_product = %s
        RETURNING *
        """,
        (id_product,),
    )
    return cur.fetchone()
