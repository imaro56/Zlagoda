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
        ORDER BY empl_surname
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

def update_employee(cur, id_employee, data):
    cur.execute(
        """
        UPDATE employee
        SET 
            empl_surname = %s, empl_name = %s, empl_patronymic = %s, 
            empl_role = %s, salary = %s, date_of_birth = %s, 
            date_of_start = %s, phone_number = %s, city = %s, 
            street = %s, zip_code = %s
        WHERE id_employee = %s
        RETURNING *
        """,
        (
            data['empl_surname'], data['empl_name'], data['empl_patronymic'], 
            data['empl_role'], data['salary'], data['date_of_birth'], 
            data['date_of_start'], data['phone_number'], data['city'], 
            data['street'], data['zip_code'], id_employee),
    )
    return cur.fetchone()


def delete_employee(cur, id_employee):
    cur.execute(
        """
        DELETE FROM employee
        WHERE id_employee = %s
        RETURNING *
        """,
        (id_employee,),
    )
    return cur.fetchone()

def get_employee_by_surname(cur, surname):
    cur.execute(
        """
        SELECT * FROM employee
        WHERE empl_surname ILIKE %s
        ORDER BY empl_surname
        """,
        (f"%{surname}%",),
    )
    return cur.fetchall()

def get_all_cashiers(cur):
    cur.execute(
        """
        SELECT * FROM employee
        WHERE empl_role = 'cashier'
        ORDER BY empl_surname
        """,
    )
    return cur.fetchall()


def cashiers_with_only_promo_checks(cur):
    cur.execute(
        """
        SELECT e.id_employee, e.empl_surname, e.empl_name
        FROM employee AS e
        WHERE e.empl_role = 'cashier'
            AND EXISTS (
                SELECT 1 FROM "check" c2
                WHERE c2.id_employee = e.id_employee)
            AND NOT EXISTS (
                SELECT 1 FROM "check" AS c
                WHERE c.id_employee = e.id_employee
                AND NOT EXISTS (
                    SELECT 1
                    FROM sale AS s
                        JOIN store_product AS sp ON sp.UPC = s.UPC
                    WHERE s.check_number = c.check_number
                        AND sp.promotional_product = TRUE
                )
            )
        ORDER BY e.empl_surname
        """
    )
    return cur.fetchall()