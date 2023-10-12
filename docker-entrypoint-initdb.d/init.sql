ALTER USER `root`@`%` IDENTIFIED WITH mysql_native_password BY "tDYvlfUlmGKnVn5YeINRZGJUtm+E07/O";

CREATE USER `TeleBotDevel`@`%` IDENTIFIED WITH mysql_native_password BY ">oe-(#nm{}!.*-pu+Ks5eFY2d5}}1lRn";
USE TeleBotDevelDB;

-- Creating tables and inserting first admin into allowed users.
CREATE TABLE `allowed_users` (
    `ID` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL UNIQUE,
    `nama` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `is_admin` TINYINT(1) NOT NULL
);

INSERT INTO `allowed_users` (`username`, `nama`, `is_admin`) VALUES ("6119375027", "Tamara", 1);

CREATE TABLE `site_data` (
    `ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Site_ID_Tenant` VARCHAR(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Tenant` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Alamat` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Latitude` FLOAT NOT NULL,
    `Longitude` FLOAT NOT NULL
);

CREATE TABLE `contact_persons` (
    `contact_id` INT AUTO_INCREMENT PRIMARY KEY,
    `nama` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `phone_num` VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL UNIQUE
);

-- Creating a user for telegram bot and granting it privileges.
GRANT SELECT, INSERT, UPDATE, DELETE ON `TeleBotDevelDB`.`allowed_users` TO `TeleBotDevel`@`%`;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP ON `TeleBotDevelDB`.`site_data` TO `TeleBotDevel`@`%`;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP ON `TeleBotDevelDB`.`contact_persons` TO `TeleBotDevel`@`%`;
FLUSH PRIVILEGES;
