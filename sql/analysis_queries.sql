-- India Agricultural Commodity Price Analysis
-- MySQL 8.0+ | Source table: commodity_prices
-- Expected columns: State, District, Market, Commodity, Variety, Grade,
-- Arrival_Date, Min_Price, Max_Price, Modal_Price, Commodity_Code

-- 1. Long-term average price change by commodity (2015-2025).
WITH yearly_prices AS (
    SELECT Commodity, YEAR(Arrival_Date) AS price_year,
           AVG(Modal_Price) AS avg_modal_price
    FROM commodity_prices
    WHERE Arrival_Date >= '2015-01-01'
      AND Arrival_Date < '2026-01-01'
    GROUP BY Commodity, YEAR(Arrival_Date)
), endpoints AS (
    SELECT Commodity,
           MAX(CASE WHEN price_year = 2015 THEN avg_modal_price END) AS price_2015,
           MAX(CASE WHEN price_year = 2025 THEN avg_modal_price END) AS price_2025
    FROM yearly_prices
    GROUP BY Commodity
)
SELECT Commodity, price_2015, price_2025,
       price_2025 - price_2015 AS absolute_change,
       100.0 * (price_2025 - price_2015) / NULLIF(price_2015, 0) AS percent_change,
       RANK() OVER (ORDER BY price_2025 - price_2015 DESC) AS increase_rank
FROM endpoints
WHERE price_2015 IS NOT NULL AND price_2025 IS NOT NULL
ORDER BY increase_rank;

-- 2. Monthly average and month-over-month change by commodity and market.
WITH monthly_prices AS (
    SELECT State, Market, Commodity,
           YEAR(Arrival_Date) AS price_year,
           MONTH(Arrival_Date) AS price_month,
           AVG(Modal_Price) AS avg_modal_price
    FROM commodity_prices
    GROUP BY State, Market, Commodity,
             YEAR(Arrival_Date), MONTH(Arrival_Date)
), with_previous AS (
    SELECT *,
           LAG(avg_modal_price) OVER (
               PARTITION BY State, Market, Commodity
               ORDER BY price_year, price_month
           ) AS prior_month_price
    FROM monthly_prices
)
SELECT State, Market, Commodity, price_year, price_month,
       avg_modal_price, prior_month_price,
       100.0 * (avg_modal_price - prior_month_price)
           / NULLIF(prior_month_price, 0) AS mom_change_pct
FROM with_previous
ORDER BY Commodity, State, Market, price_year, price_month;

-- 3. Year-over-year monthly price change by commodity.
-- The same month in the preceding year is joined explicitly, so missing months
-- do not shift the comparison as they would with a 12-row LAG.
WITH monthly_prices AS (
    SELECT Commodity, YEAR(Arrival_Date) AS price_year,
           MONTH(Arrival_Date) AS price_month,
           AVG(Modal_Price) AS avg_modal_price
    FROM commodity_prices
    GROUP BY Commodity, YEAR(Arrival_Date), MONTH(Arrival_Date)
)
SELECT curr.Commodity, curr.price_year, curr.price_month,
       curr.avg_modal_price, prior.avg_modal_price AS prior_year_price,
       100.0 * (curr.avg_modal_price - prior.avg_modal_price)
           / NULLIF(prior.avg_modal_price, 0) AS yoy_change_pct
FROM monthly_prices AS current
LEFT JOIN monthly_prices AS prior
  ON prior.Commodity = curr.Commodity
 AND prior.price_year = curr.price_year - 1
 AND prior.price_month = curr.price_month
ORDER BY curr.Commodity, curr.price_year, curr.price_month;

-- 4. Rank districts by mean daily price spread as a percentage of modal price.
WITH district_spread AS (
    SELECT State, District,
           AVG(100.0 * (Max_Price - Min_Price) / NULLIF(Modal_Price, 0))
               AS avg_spread_pct
    FROM commodity_prices
    WHERE Modal_Price > 0 AND Max_Price >= Min_Price
    GROUP BY State, District
)
SELECT State, District, avg_spread_pct,
       RANK() OVER (ORDER BY avg_spread_pct DESC) AS volatility_rank
FROM district_spread
ORDER BY volatility_rank
LIMIT 20;

-- 5. FAQ versus Medium grade price premiums by commodity and variety.
WITH grade_prices AS (
    SELECT Commodity, Variety,
           AVG(CASE WHEN Grade = 'FAQ' THEN Modal_Price END) AS faq_avg_price,
           AVG(CASE WHEN Grade = 'Medium' THEN Modal_Price END) AS medium_avg_price
    FROM commodity_prices
    WHERE Grade IN ('FAQ', 'Medium')
    GROUP BY Commodity, Variety
)
SELECT Commodity, Variety, faq_avg_price, medium_avg_price,
       faq_avg_price - medium_avg_price AS faq_premium
FROM grade_prices
WHERE faq_avg_price IS NOT NULL AND medium_avg_price IS NOT NULL
ORDER BY faq_premium DESC;

-- 6. Markets with most high-price tomato days in 2024 (>= ₹3,000/quintal).
WITH tomato_days AS (
    SELECT State, Market, Arrival_Date,
           MAX(Modal_Price) AS daily_modal_price
    FROM commodity_prices
    WHERE Commodity = 'Tomato'
      AND Arrival_Date >= '2024-01-01'
      AND Arrival_Date < '2025-01-01'
    GROUP BY State, Market, Arrival_Date
)
SELECT State, Market,
       SUM(CASE WHEN daily_modal_price >= 3000 THEN 1 ELSE 0 END)
           AS days_at_or_above_3000,
       AVG(daily_modal_price) AS avg_daily_modal_price
FROM tomato_days
GROUP BY State, Market
HAVING days_at_or_above_3000 > 0
ORDER BY days_at_or_above_3000 DESC
LIMIT 20;

-- 7. State price comparison for Onion in 2024, with a defensive outlier cap.
SELECT State, AVG(Modal_Price) AS avg_modal_price_2024,
       COUNT(*) AS observations
FROM commodity_prices
WHERE Commodity = 'Onion'
  AND Arrival_Date >= '2024-01-01'
  AND Arrival_Date < '2025-01-01'
  AND Modal_Price < 1000000
GROUP BY State
ORDER BY avg_modal_price_2024 DESC;
