TRUNCATE sale, "check", store_product, product, category, customer_card, employee
    RESTART IDENTITY CASCADE;

INSERT INTO category (category_number, category_name) VALUES
(1, 'Молочні продукти'),
(2, 'Напої'),
(3, 'Випічка'),
(4, 'Бакалія'),
(5, 'Заморожена продукція');

INSERT INTO product (id_product, product_name, category_number, characteristics) VALUES
(1,  'Молоко 2.5%',        1, '1 л, пакет'),
(2,  'Кефір 1%',           1, '0.5 л'),
(3,  'Сік апельсиновий',   2, '1 л'),
(4,  'Вода мінеральна',    2, '1.5 л'),
(5,  'Хліб житній',        3, '500 г'),
(6,  'Батон нарізний',     3, '400 г'),
(7,  'Цукор',              4, '1 кг'),
(8,  'Сіль кухонна',       4, '1 кг'),
(9,  'Пельмені',           5, '900 г'),
(10, 'Морозиво пломбір',   5, '500 г');

INSERT INTO store_product (UPC, UPC_prom, id_product, selling_price, products_number, promotional_product) VALUES
('200000000001', NULL, 1,  25.6000, 30, TRUE),   
('200000000010', NULL, 10, 44.0000, 25, TRUE);   

INSERT INTO store_product (UPC, UPC_prom, id_product, selling_price, products_number, promotional_product) VALUES
('100000000001', '200000000001', 1,  32.0000, 100, FALSE),
('100000000002', NULL,           2,  28.0000,  80, FALSE),
('100000000003', NULL,           3,  45.0000,  60, FALSE),
('100000000004', NULL,           4,  18.0000, 200, FALSE),
('100000000005', NULL,           5,  22.0000, 150, FALSE),
('100000000006', NULL,           6,  20.0000, 120, FALSE),
('100000000007', NULL,           7,  38.0000,  90, FALSE),   
('100000000008', NULL,           8,  12.0000, 110, FALSE),
('100000000009', NULL,           9,  95.0000,  40, FALSE),   
('100000000010', '200000000010', 10, 55.0000,  70, FALSE);

INSERT INTO employee (login, password_hash, id_employee, empl_surname, empl_name, empl_patronymic,
                      empl_role, salary, date_of_birth, date_of_start, phone_number, city, street, zip_code) VALUES
('manager', '$2b$12$aVXeUAHrsV/zI.yQ6PgdY.epSPeh2BR8DCuheMpM57YfFRz/8wBei', '1', 'Адмін',     'Ольга',  'Петрівна',   'manager', 25000, '1985-04-12', '2020-01-10', '+380501112201', 'Київ', 'Хрещатик 1',   '01001'),
('cashier1','x',                     '2', 'Іваненко',  'Іван',   'Іванович',   'cashier', 15000, '1992-06-20', '2021-03-01', '+380501112202', 'Київ', 'Шевченка 5',   '01002'),
('cashier2','x',                     '3', 'Петренко',  'Олег',   'Сергійович', 'cashier', 15000, '1990-11-05', '2021-05-15', '+380501112203', 'Київ', 'Лесі Українки 3','01003'),
('cashier3','x',                     '4', 'Сидоренко', 'Марія',  'Андріївна',  'cashier', 16000, '1995-02-18', '2022-02-01', '+380501112204', 'Київ', 'Франка 7',     '01004');

INSERT INTO customer_card (card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent) VALUES
('1111111111111', 'Коваленко', 'Анна',   'Ігорівна',   '+380671112233', 'Київ', 'Гоголя 2',  '01010', 5),
('2222222222222', 'Шевченко',  'Богдан', 'Олексійович','+380671112244', 'Київ', 'Пушкіна 9', '01011', 10);

INSERT INTO "check" (check_number, id_employee, card_number, print_date, sum_total, vat) VALUES
('0000000001', '2', NULL,            '2026-06-02 10:15:00',  86.0000, 17.2000),
('0000000002', '2', '1111111111111','2026-06-05 14:30:00',  99.0000, 19.8000),
('0000000003', '3', NULL,            '2026-06-03 11:00:00',  84.0000, 16.8000),  
('0000000004', '3', NULL,            '2026-06-07 09:45:00',  56.0000, 11.2000),
('0000000005', '4', NULL,            '2026-06-04 16:20:00',  76.0000, 15.2000),
('0000000006', '4', '2222222222222','2026-06-10 12:05:00', 122.0000, 24.4000);

INSERT INTO sale (UPC, check_number, product_number, selling_price) VALUES
('100000000001', '0000000001', 2, 32.0000),
('100000000005', '0000000001', 1, 22.0000),
('100000000003', '0000000002', 1, 45.0000),
('100000000004', '0000000002', 3, 18.0000),
('200000000010', '0000000003', 1, 44.0000),   
('100000000006', '0000000003', 2, 20.0000),
('100000000002', '0000000004', 2, 28.0000),
('100000000008', '0000000005', 1, 12.0000),
('100000000005', '0000000005', 2, 22.0000),
('100000000006', '0000000005', 1, 20.0000),
('100000000001', '0000000006', 1, 32.0000),
('100000000003', '0000000006', 2, 45.0000);

SELECT setval('category_category_number_seq', (SELECT MAX(category_number) FROM category));
SELECT setval('product_id_product_seq',        (SELECT MAX(id_product) FROM product));
CREATE SEQUENCE IF NOT EXISTS check_number_sequence;
SELECT setval('check_number_sequence', 6);