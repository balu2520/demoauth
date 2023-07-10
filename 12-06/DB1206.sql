CREATE DATABASE users;
USE users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    login_timestamp DATETIME NOT NULL,
    round_trip_time_ms FLOAT NOT NULL,
	ip_address VARCHAR(50) NOT NULL,
	country VARCHAR(50) NOT NULL,
	region VARCHAR(50) NOT NULL,
	city VARCHAR(50) NOT NULL,
    asn VARCHAR(50) NOT NULL,
	browser_version VARCHAR(50) NOT NULL,
    os_name VARCHAR(50) NOT NULL,
    device_type VARCHAR(50) NOT NULL
);
SELECT*FROM USERS;

