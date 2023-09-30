# TIDAK UNTUK DISUNTING SECARA MANUAL
# Naskah ini digenerasi oleh deploy.sh atau deploy.bat.
# Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data.

-- TIDAK UNTUK DISUNTING SECARA MANUAL 
-- Naskah ini digenerasi oleh deploy.sh atau deploy.bat. 
-- Silahkan sunting berkas initialization.sql untuk mengubah kueri inisialisasi basis data. 
 
 
USE TeleBotDevelDB;

-- Creating tables and inserting first admin into allowed users.
CREATE TABLE `allowed_users` (
    `ID` int AUTO_INCREMENT PRIMARY KEY,
    `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL UNIQUE,
    `nama` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `is_admin` tinyint(1) NOT NULL
);

INSERT INTO allowed_users (`username`, `nama`, `is_admin`) VALUES ('1139987918', 'Muhammad Ivan Wiryawan', 1);

CREATE TABLE `site_data` (
    `ID` int AUTO_INCREMENT PRIMARY KEY,
    `Site_ID_Tenant` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Tenant` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Alamat` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Latitude` FLOAT NOT NULL,
    `Longitude` FLOAT NOT NULL
);

-- Creating a user for telegram bot and granting it privileges.
CREATE USER `TeleBotDevel`@`%` IDENTIFIED WITH mysql_native_password BY 'Mx7Sme5RSvXPW0EQyCCQedQG';
GRANT SELECT, INSERT, UPDATE, DELETE ON `TeleBotDevelDB`.`allowed_users` TO `TeleBotDevel`@`%`;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP ON `TeleBotDevelDB`.`site_data` TO `TeleBotDevel`@`%`;
FLUSH PRIVILEGES;
