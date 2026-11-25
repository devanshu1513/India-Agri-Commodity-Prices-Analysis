-- MySQL 8.0+ source table for sql/analysis_queries.sql
CREATE DATABASE IF NOT EXISTS agri_prices
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE agri_prices;

CREATE TABLE IF NOT EXISTS commodity_prices (
    State           VARCHAR(100) NOT NULL,
    District        VARCHAR(120),
    Market          VARCHAR(150),
    Commodity       VARCHAR(150) NOT NULL,
    Variety         VARCHAR(150),
    Grade           VARCHAR(80),
    Arrival_Date    DATE NOT NULL,
    Min_Price       DECIMAL(14, 2),
    Max_Price       DECIMAL(14, 2),
    Modal_Price     DECIMAL(14, 2),
    Commodity_Code  INT,
    INDEX idx_date_commodity (Arrival_Date, Commodity),
    INDEX idx_state_district (State, District),
    INDEX idx_market_commodity (Market, Commodity)
) ENGINE=InnoDB;

-- Load each cleaned CSV produced under data/processed/.
-- Enable LOCAL INFILE in your MySQL client if required, then run once per file:
-- LOAD DATA LOCAL INFILE '/absolute/path/to/data/processed/2001.csv'
-- INTO TABLE commodity_prices
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 LINES
-- (State, District, Market, Commodity, Variety, Grade, @arrival_date,
--  Min_Price, Max_Price, Modal_Price, Commodity_Code)
-- SET Arrival_Date = STR_TO_DATE(@arrival_date, '%Y-%m-%d');
