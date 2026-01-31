-- Hidden tests add extra data and check ordering/ties

INSERT INTO customers(id, name) VALUES (4, 'Davit'), (5, 'Eva');
INSERT INTO orders(id, customer_id, amount) VALUES
 (10, 4, 100.0),
 (11, 5, 100.0),
 (12, 5, 0.5);

-- Must include only customers with orders
SELECT CASE
  WHEN NOT EXISTS (SELECT 1 FROM result WHERE customer_id = 999)
  THEN 'PASS'
  ELSE 'FAIL'
END;

-- Must order by total_spend desc then customer_id asc
-- Here: Davit total=100.0, Eva total=100.5 -> Eva should be first
SELECT CASE
  WHEN (SELECT customer_id FROM result LIMIT 1) = 5
  THEN 'PASS'
  ELSE 'FAIL'
END;

-- Check Eva total is 100.5
SELECT CASE
  WHEN (SELECT total_spend FROM result WHERE customer_id=5) = 100.5
  THEN 'PASS'
  ELSE 'FAIL'
END;
