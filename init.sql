SET @username := '$USERNAME';
SET @nama_user := '$NAMA_USER';

CREATE USER 'TeleBotDevel'@'%' IDENTIFIED WITH mysql_native_password BY 'lOsyogzuy8iewaEUwvKPApz2D2XNxCF0';
GRANT SELECT, INSERT, UPDATE, DELETE ON 'TeleBotDevelDB'.'allowed_users' TO 'TeleBotDevel'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE, DROP ON 'TeleBotDevelDB'.'site_data' TO 'TeleBotDevel'@'%';
CREATE USER 'phpmyadmin'@'%' IDENTIFIED WITH mysql_native_password BY 'lOsyogzuy8iewaEUwvKPApz2D2XNxCF0';
GRANT USAGE ON *.* TO 'phpmyadmin'@'%'
GRANT ALL PRIVILEGES ON 'phpmyadmin'.* TO 'phpmyadmin'@'%'
FLUSH PRIVILEGES;

USE TeleBotDevelDB;
CREATE TABLE allowed_users (
    ID int AUTO_INCREMENT PRIMARY KEY,
    username varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL UNIQUE,
    nama varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    is_admin tinyint(1) NOT NULL
);

SET @insert_sql := CONCAT('INSERT INTO allowed_users (username, nama, is_admin) VALUES (', @username, ', ', @nama_user, ', 1)')
PREPARE stmt FROM @insert_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE TABLE site_data (
    ID int AUTO_INCREMENT PRIMARY KEY,
    Site_ID_Tenant varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    Tenant varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    Alamat varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    Latitude FLOAT NOT NULL,
    Longitude FLOAT NOT NULL
);
