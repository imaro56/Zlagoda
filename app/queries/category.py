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
