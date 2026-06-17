def get_category(cur, category_number):
    cur.execute(
        """
        SELECT * FROM category 
        WHERE category_number = %s
        """,
        (category_number,),
    )
    return cur.fetchone()
    

def get_all_categories(cur):
    cur.execute(
        """
        SELECT * FROM category 
        ORDER BY category_name
        """
    )
    return cur.fetchall()

def create_category(cur, data):
    cur.execute(
        """
        INSERT INTO category (category_name)
            VALUES (%s) 
            RETURNING *
        """,
        (data['category_name'],),
    )
    return cur.fetchone()

def delete_category(cur, category_number):
    cur.execute(
        """
        DELETE FROM category 
        WHERE category_number = %s 
        RETURNING *
        """,
        (category_number,),
    )
    return cur.fetchone()
    
def update_category(cur, category_number, data):
    cur.execute(
        """
        UPDATE category
        SET category_name = %s
        WHERE category_number = %s
        RETURNING *
        """,
        (data['category_name'], category_number),
    )
    return cur.fetchone()

def get_category_total_values(cur, min_value):
    cur.execute(
        """
        SELECT ct.category_name, 
            COUNT(sp.UPC) AS diff_products, 
            SUM(sp.products_number) AS total_cnt,
            SUM(sp.products_number * sp.selling_price) AS price,
            MIN(sp.selling_price) AS min_price,
            MAX(sp.selling_price) AS max_price
        FROM category AS ct
            INNER JOIN product AS p ON p.category_number = ct.category_number
            INNER JOIN store_product AS sp ON sp.id_product = p.id_product
    
        GROUP BY ct.category_number, ct.category_name
        HAVING SUM(sp.products_number * sp.selling_price) >= %s
        ORDER BY price DESC
        """,
        (min_value,),
    )
    return cur.fetchall()
