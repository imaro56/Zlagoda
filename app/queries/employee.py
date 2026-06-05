

def get_employee_by_login(cur , login):
    cur.execute(
        "SELECT * FROM employee WHERE login = %s", 
        (login,),
    )
    return cur.fetchone()

def get_employee(cur, id_employee):
    cur.execute(
        "SELECT * FROM employee WHERE id_employee = %s",
        (id_employee,),
    )
    return cur.fetchone()
    

def get_all_employees(cur):
    cur.execute(
        "SELECT * FROM employee ORDER BY "
    )
    return cur.fetchall()
    