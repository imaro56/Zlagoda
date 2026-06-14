def get_card(cur, card_number):
    cur.execute(
        """
        SELECT * FROM customer_card 
        WHERE card_number = %s
        """,
        (card_number,),
    )
    return cur.fetchone()

def get_all_cards(cur):
    cur.execute(
        """
        SELECT * FROM customer_card 
        ORDER BY cust_surname
        """
    )
    return cur.fetchall()

def get_cards_by_percent(cur, percent):
    cur.execute(
        """
        SELECT * FROM customer_card
        WHERE percent=%s
        ORDER BY cust_surname
        """,
        (percent,),
    )
    return cur.fetchall()

def get_cards_by_surname(cur, cust_surname):
    cur.execute(
        """
        SELECT * FROM customer_card
        WHERE cust_surname ILIKE %s
        ORDER BY cust_surname
        """,
        (f"%{cust_surname}%",),
    )
    return cur.fetchall()

def create_card(cur, data):
    cur.execute(
        """
        INSERT INTO customer_card (card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING *
        """,
        (data['card_number'], data['cust_surname'], data['cust_name'], data['cust_patronymic'], data['phone_number'], data['city'], data['street'], data['zip_code'], data['percent']),
    )
    return cur.fetchone()

def update_card(cur, card_number, data):
    cur.execute(
        """
        UPDATE customer_card
        SET 
            cust_surname = %s, cust_name = %s, cust_patronymic = %s, phone_number = %s, city = %s, street = %s, zip_code = %s, percent = %s
        WHERE card_number = %s
        RETURNING *
        """,
        (
            data['cust_surname'], data['cust_name'], data['cust_patronymic'], data['phone_number'], data['city'], data['street'], data['zip_code'], data['percent'], card_number),
    )
    return cur.fetchone()

def delete_card(cur, card_number):
    cur.execute(
        """
        DELETE FROM customer_card
        WHERE card_number = %s
        RETURNING *
        """,
        (card_number,),
    )
    return cur.fetchone()