CREATE TABLE category (
    category_number SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL
);

CREATE TABLE product (
    id_product SERIAL PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL,
    category_number INT NOT NULL REFERENCES category(category_number) ON UPDATE CASCADE ON DELETE NO ACTION,
    characteristics VARCHAR(100) NOT NULL
);

CREATE TABLE store_product (
    UPC VARCHAR(12) PRIMARY KEY,
    UPC_prom VARCHAR(12) REFERENCES store_product(UPC) ON UPDATE CASCADE ON DELETE SET NULL,
    id_product INT NOT NULL REFERENCES product(id_product) ON UPDATE CASCADE ON DELETE NO ACTION,
    selling_price DECIMAL(13, 4) NOT NULL CHECK (selling_price >= 0),
    products_number INT NOT NULL CHECK (products_number >= 0),
    promotional_product BOOLEAN NOT NULL
);

CREATE UNIQUE INDEX unique_regular_store_product_per_product
      ON store_product (id_product)
      WHERE promotional_product = FALSE;

CREATE TABLE employee (
    login VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    id_employee VARCHAR(10) PRIMARY KEY,
    empl_surname VARCHAR(50) NOT NULL,
    empl_name VARCHAR(50) NOT NULL,
    empl_patronymic VARCHAR(50),
    empl_role VARCHAR(10) NOT NULL CHECK (empl_role IN ('manager', 'cashier')),
    salary DECIMAL(13, 4) NOT NULL CHECK (salary >= 0),
    date_of_birth DATE NOT NULL,
    date_of_start DATE NOT NULL,
    phone_number VARCHAR(13) NOT NULL,
    city VARCHAR(50) NOT NULL,
    street VARCHAR(50) NOT NULL,
    zip_code VARCHAR(9) NOT NULL
);

CREATE OR REPLACE FUNCTION verify_age() RETURNS TRIGGER AS $$
BEGIN
    IF (AGE(NEW.date_of_birth) < '18 years') THEN
        RAISE EXCEPTION 'Employee must be 18+';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER verify_age_trigger
BEFORE INSERT OR UPDATE ON employee
FOR EACH ROW EXECUTE FUNCTION verify_age();



CREATE TABLE customer_card (
    card_number VARCHAR(13) PRIMARY KEY,
    cust_surname VARCHAR(50) NOT NULL,
    cust_name VARCHAR(50) NOT NULL,
    cust_patronymic VARCHAR(50),
    phone_number VARCHAR(13) NOT NULL,
    city VARCHAR(50),
    street VARCHAR(50),
    zip_code VARCHAR(9),
    percent INT NOT NULL CHECK (percent >= 0)
);

CREATE SEQUENCE check_number_sequence;

CREATE TABLE "check" (
    check_number VARCHAR(10) PRIMARY KEY,
    id_employee VARCHAR(10) NOT NULL REFERENCES employee(id_employee) ON UPDATE CASCADE ON DELETE NO ACTION,
    card_number VARCHAR(13) REFERENCES customer_card(card_number) ON UPDATE CASCADE ON DELETE NO ACTION,
    print_date TIMESTAMP NOT NULL,
    sum_total DECIMAL(13, 4) NOT NULL CHECK (sum_total > 0),
    vat DECIMAL(13, 4) NOT NULL CHECK (vat > 0)
);

CREATE TABLE sale (
    UPC VARCHAR(12) NOT NULL REFERENCES store_product(UPC) ON UPDATE CASCADE ON DELETE NO ACTION,
    check_number VARCHAR(10) NOT NULL REFERENCES "check"(check_number) ON UPDATE CASCADE ON DELETE CASCADE,
    product_number INT NOT NULL CHECK (product_number > 0),
    selling_price DECIMAL(13, 4) NOT NULL CHECK (selling_price > 0),
    PRIMARY KEY (UPC, check_number)
);