from psycopg.rows import dict_row
from app.db import pool
from app.security import hash_password

from ..queries import employee as employee_queries


def seed():
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            employee = employee_queries.get_employee_by_login(cur, "admin")            
            if employee:
                return
            employee_queries.create_employee(cur, {
                "login": "admin",
                "password_hash": hash_password("password"),
                "id_employee": "0",          
                "empl_surname": "Admin",
                "empl_name": "Admin",
                "empl_patronymic": "Admin",
                "empl_role": "manager",
                "salary": 0,
                "date_of_birth": "2000-01-01",
                "date_of_start": "2020-01-01",
                "phone_number": "0",
                "city": "0",
                "street": "0",
                "zip_code": "0",
            })

if __name__ == "__main__":
    with pool:
        seed()