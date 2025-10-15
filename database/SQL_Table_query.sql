CREATE DATABASE [Database_name];

USE [Database_name];

CREATE TABLE [Table_name] (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Date_Time DATETIME NOT NULL,
    Control_Word INT,
    Status_Word INT,
    Reference_1 INT,
    Reference_2 INT,
    Speed INT,
    Torque INT,
    Voltage INT,
    Current_i INT,
    Power INT,
    Error_code INT
);
