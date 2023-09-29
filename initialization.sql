-- SET @bot_user :='$TELEBOT_USER';
-- SET @bot_passwd :='$TELEBOT_PASSWORD';
-- SET @username :='$USERNAME';
-- SET @nama_user :='$NAMA_USER';
-- DECLARE @phpmyadmin_passwd AS VARCHAR='$PHPMYADMIN_PASSWORD';

-- SET @insert_sql := CONCAT('CREATE USER `phpmyadmin`@`%` IDENTIFIED WITH mysql_native_password BY `', @phpmyadmin_passwd, '`');
-- PREPARE stmt FROM @insert_sql;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt;
-- 
-- SET @insert_sql := CONCAT('GRANT SELECT, INSERT, UPDATE, DELETE ON `TeleBotDevelDB`.`site_data` TO `', @bot_user, '`@`%`');
-- PREPARE stmt FROM @insert_sql;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt;
-- GRANT USAGE ON *.* TO `phpmyadmin`@`%`;
-- GRANT ALL PRIVILEGES ON `phpmyadmin`.* TO `phpmyadmin`@`%`;
FLUSH PRIVILEGES;

USE __MYSQL_DATABASE__;

CREATE TABLE `allowed_users` (
    `ID` int AUTO_INCREMENT PRIMARY KEY,
    `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL UNIQUE,
    `nama` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `is_admin` tinyint(1) NOT NULL
);

INSERT INTO allowed_users (`username`, `nama`, `is_admin`) VALUES ('__USERNAME__', '__NAMA_USER__', 1);
-- SET @insert_sql := CONCAT('INSERT INTO allowed_users (`username`, `nama`, `is_admin`) VALUES (', $USERNAME, ', ', Muhammad Ivan Wiryawan, ', 1)');
-- PREPARE stmt FROM @insert_sql;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt;

CREATE TABLE `site_data` (
    `ID` int AUTO_INCREMENT PRIMARY KEY,
    `Site_ID_Tenant` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Tenant` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Alamat` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    `Latitude` FLOAT NOT NULL,
    `Longitude` FLOAT NOT NULL
);

CREATE USER `__TELEBOT_USER__`@`%` IDENTIFIED WITH mysql_native_password BY '__TELEBOT_PASSWORD__';
-- SET @create_sql := CONCAT('CREATE USER `', TeleBotDevel, '`@`%` IDENTIFIED WITH mysql_native_password BY `', $TELEBOT_PASSWORD, '`');
-- PREPARE stmt FROM @insert_sql;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt;

GRANT SELECT, INSERT, UPDATE, DELETE ON `__MYSQL_DATABASE__`.`allowed_users` TO `__TELEBOT_USER__`@`%`;
-- SET @grant_sql := CONCAT('GRANT SELECT, INSERT, UPDATE, DELETE ON `TeleBotDevelDB`.`allowed_users` TO `', TeleBotDevel, '`@`%`');
-- PREPARE stmt FROM @grant_sql;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt;

GRANT SELECT, INSERT, UPDATE, DELETE, DROP ON `__MYSQL_DATABASE__`.`site_data` TO `__TELEBOT_USER__`@`%`;
-- SET @grant_sql := CONCAT('GRANT SELECT, INSERT, UPDATE, DELETE, DROP ON `TeleBotDevelDB`.`site_data` TO `', TeleBotDevel, '`@`%`');
-- PREPARE stmt FROM @grant_sql;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt;
