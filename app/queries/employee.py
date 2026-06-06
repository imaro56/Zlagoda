def get_employee_by_login(cur , login):
    cur.execute(
        """
        SELECT * FROM employee 
        WHERE login = %s
        """,
        (login,),
    )
    return cur.fetchone()

def get_employee(cur, id_employee):
    cur.execute(
        """
        SELECT * FROM employee 
        WHERE id_employee = %s
        """,
        (id_employee,),
    )
    return cur.fetchone()
    

def get_all_employees(cur):
    cur.execute(
        """
        SELECT * FROM employee 
        ORDER BY empl_name
        """
    )
    return cur.fetchall()

def create_employee(cur, data):
    cur.execute(
        """
        INSERT INTO employee (
            login, password_hash, id_employee, 
            empl_surname, empl_name, empl_patronymic, 
            empl_role, salary, date_of_birth, 
            date_of_start, phone_number, city, 
            street, zip_code) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING *
        """,
        (data['login'], data['password_hash'], data['id_employee'], 
            data['empl_surname'], data['empl_name'], data['empl_patronymic'], 
            data['empl_role'], data['salary'], data['date_of_birth'], 
            data['date_of_start'], data['phone_number'], data['city'], 
            data['street'], data['zip_code']),
    )
    return cur.fetchone()
