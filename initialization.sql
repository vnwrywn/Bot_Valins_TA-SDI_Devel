ALTER USER `root`@`%` IDENTIFIED WITH mysql_native_password BY "__MYSQL_ROOT_PASSWORD__";

CREATE USER `__TELEBOT_USER__`@`%` IDENTIFIED WITH mysql_native_password BY "__TELEBOT_PASSWORD__";
USE __MYSQL_DATABASE__;

-- Creating tables and inserting first admin into allowed users.
CREATE TABLE `allowed_users` (
    `ID` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL UNIQUE,
    `nama` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `is_admin` TINYINT(1) NOT NULL
);

INSERT INTO `allowed_users` (`username`, `nama`, `is_admin`) VALUES ("__USERNAME__", "__NAMA_USER__", 1);

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
GRANT SELECT, INSERT, UPDATE, DELETE ON `__MYSQL_DATABASE__`.`allowed_users` TO `__TELEBOT_USER__`@`%`;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP ON `__MYSQL_DATABASE__`.`site_data` TO `__TELEBOT_USER__`@`%`;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP ON `__MYSQL_DATABASE__`.`contact_persons` TO `__TELEBOT_USER__`@`%`;
FLUSH PRIVILEGES;

