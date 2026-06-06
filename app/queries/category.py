def get_category(cur, category_number):
    cur.execute(
        "SELECT * FROM category WHERE category_number = %s",
        (category_number,),
    )
    return cur.fetchone()
    

def get_all_categories(cur):
    cur.execute(
        "SELECT * FROM category ORDER BY category_number"
    )
    return cur.fetchall()

def create_category(cur, data):
    cur.execute(
        """
        INSERT INTO category (
            category_number, category_name) 
            VALUES (%s, %s) 
            RETURNING *
        """,
        (data['category_number'], data['category_name']),
    )
    return cur.fetchone()
