DROP DATABASE IF EXISTS lab7;

SET NAMES 'utf8mb4';

CREATE DATABASE IF NOT EXISTS lab7 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lab7;

CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL
);

CREATE TABLE GPU (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    gpu_name VARCHAR(50) NOT NULL,
    video_memory INT NOT NULL,
    memory_type VARCHAR(20) NOT NULL,
    fan_count INT NOT NULL,
    power_consumption INT NOT NULL,
    recommended_psu_power INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE CPU (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    tdp INT NOT NULL,
    cores INT NOT NULL,
    threads INT NOT NULL,
    process_nm INT NOT NULL,
    base_clock DECIMAL(4, 2) NOT NULL,
    turbo_clock DECIMAL(4, 2) NOT NULL,
    compatible_ram_type VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE Motherboard (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    socket VARCHAR(20) NOT NULL,
    chipset VARCHAR(50) NOT NULL,
    ram_slots INT NOT NULL,
    max_ram_frequency INT NOT NULL,
    form_factor VARCHAR(20) NOT NULL,
    ram_type VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE RAM (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    frequency INT NOT NULL,
    ram_type VARCHAR(10) NOT NULL,
    kit_count INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE PSU (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    power INT NOT NULL,
    certificate VARCHAR(20) NOT NULL,
    form_factor VARCHAR(20) NOT NULL,
    modularity BOOLEAN NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE PC_Case (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    form_factor VARCHAR(20) NOT NULL,
    glass_side_panel BOOLEAN NOT NULL,
    included_fans INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE PC_Build (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gpu_id INT NOT NULL,
    cpu_id INT NOT NULL,
    motherboard_id INT NOT NULL,
    ram_id INT NOT NULL,
    psu_id INT NOT NULL,
    pc_case_id INT NOT NULL,
    total_price DECIMAL(12, 2),
    build_type VARCHAR(50) NOT NULL DEFAULT 'Бюджетна',
    FOREIGN KEY (gpu_id) REFERENCES GPU(id),
    FOREIGN KEY (cpu_id) REFERENCES CPU(id),
    FOREIGN KEY (motherboard_id) REFERENCES Motherboard(id),
    FOREIGN KEY (ram_id) REFERENCES RAM(id),
    FOREIGN KEY (psu_id) REFERENCES PSU(id),
    FOREIGN KEY (pc_case_id) REFERENCES PC_Case(id)
);

CREATE TABLE order_journal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    pc_build_id INT NOT NULL,
    production_time INT NOT NULL,
    order_date DATE NOT NULL,
    payment_status ENUM ('paid', 'unpaid') NOT NULL,
    due_amount DECIMAL(10, 2) NOT NULL,
    order_status ENUM ('ready', 'not_ready') NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (pc_build_id) REFERENCES PC_Build(id)
);

INSERT INTO clients (full_name, birth_date, email, phone) VALUES 
('Олександр Іванов', '1990-05-15', 'ivanov.alex@example.com', '+380501234567'),
('Марія Шевченко', '1985-12-03', 'shevchenko.maria@example.com', '+380671234567');

INSERT INTO GPU (model_name, manufacturer, gpu_name, video_memory, memory_type, fan_count, power_consumption, recommended_psu_power, price) VALUES
('RTX 4060 Ti Ventus', 'MSI', 'RTX 4060 Ti', 8192, 'GDDR6', 2, 160, 500, 399.99),
('RTX 4070 Gaming X', 'Gigabyte', 'RTX 4070', 12288, 'GDDR6X', 3, 215, 600, 599.99);

INSERT INTO CPU (model_name, manufacturer, tdp, cores, threads, process_nm, base_clock, turbo_clock, compatible_ram_type, price) VALUES
('Core i5-12400F', 'Intel', 65, 6, 12, 10, 2.5, 4.4, 'DDR4', 189.99),
('Ryzen 5 5600X', 'AMD', 65, 6, 12, 7, 3.7, 4.6, 'DDR4', 199.99);

INSERT INTO Motherboard (model_name, manufacturer, socket, chipset, ram_slots, max_ram_frequency, form_factor, ram_type, price) VALUES
('Z690 Aorus Master', 'Gigabyte', 'LGA 1700', 'Z690', 4, 6400, 'ATX', 'DDR5', 329.99),
('B550 TUF Gaming', 'ASUS', 'AM4', 'B550', 4, 4800, 'ATX', 'DDR4', 189.99);

INSERT INTO RAM (model_name, manufacturer, capacity, frequency, ram_type, kit_count, price) VALUES
('Ripjaws V', 'G.Skill', 16384, 3600, 'DDR4', 2, 79.99),
('Vengeance LPX', 'Corsair', 32768, 3200, 'DDR4', 2, 149.99);

INSERT INTO PSU (model_name, manufacturer, power, certificate, form_factor, modularity, price) VALUES
('RM850x', 'Corsair', 850, '80+ Gold', 'ATX', TRUE, 149.99),
('CX650M', 'Corsair', 650, '80+ Bronze', 'ATX', TRUE, 79.99);

INSERT INTO PC_Case (model_name, manufacturer, form_factor, glass_side_panel, included_fans, price) VALUES
('NZXT H510', 'NZXT', 'ATX', TRUE, 2, 89.99),
('Meshify C', 'Fractal Design', 'ATX', TRUE, 2, 109.99);

INSERT INTO PC_Build (gpu_id, cpu_id, motherboard_id, ram_id, psu_id, pc_case_id, build_type) VALUES
(1, 1, 2, 1, 2, 1, 'Бюджетна'),
(2, 2, 1, 2, 1, 2, 'Ігрова');

INSERT INTO order_journal (client_id, pc_build_id, production_time, order_date, payment_status, due_amount, order_status) VALUES
(1, 1, 7, '2024-11-15', 'paid', 0.00, 'ready'),
(2, 2, 10, '2024-11-12', 'unpaid', 1500.00, 'not_ready');

DELIMITER $$
CREATE TRIGGER trg_pc_build_insert
BEFORE INSERT ON PC_Build
FOR EACH ROW
BEGIN
    SET NEW.total_price = (
        (SELECT price FROM GPU WHERE id = NEW.gpu_id) +
        (SELECT price FROM CPU WHERE id = NEW.cpu_id) +
        (SELECT price FROM Motherboard WHERE id = NEW.motherboard_id) +
        (SELECT price FROM RAM WHERE id = NEW.ram_id) +
        (SELECT price FROM PSU WHERE id = NEW.psu_id) +
        (SELECT price FROM PC_Case WHERE id = NEW.pc_case_id)
    );
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER trg_pc_build_update
BEFORE UPDATE ON PC_Build
FOR EACH ROW
BEGIN
    SET NEW.total_price = (
        (SELECT price FROM GPU WHERE id = NEW.gpu_id) +
        (SELECT price FROM CPU WHERE id = NEW.cpu_id) +
        (SELECT price FROM Motherboard WHERE id = NEW.motherboard_id) +
        (SELECT price FROM RAM WHERE id = NEW.ram_id) +
        (SELECT price FROM PSU WHERE id = NEW.psu_id) +
        (SELECT price FROM PC_Case WHERE id = NEW.pc_case_id)
    );
END$$
DELIMITER ;
