-- Test 1: result view exists
SELECT CASE
  WHEN EXISTS (SELECT 1 FROM sqlite_master WHERE type='view' AND name='result')
  THEN 'PASS: view result exists'
  ELSE 'FAIL: view result does not exist'
END;

-- Test 2: correct row count (3 customers have orders)
SELECT CASE
  WHEN (SELECT COUNT(*) FROM result) = 3
  THEN 'PASS: row count is 3'
  ELSE 'FAIL: expected 3 rows in result'
END;

-- Test 3: top customer should be Boris with 20.0
SELECT CASE
  WHEN (SELECT name FROM result LIMIT 1) = 'Boris'
  THEN 'PASS: top customer is Boris'
  ELSE 'FAIL: top customer should be Boris'
END;

-- Test 4: Ana total spend should be 15.0
SELECT CASE
  WHEN (SELECT total_spend FROM result WHERE customer_id = 1) = 15.0
  THEN 'PASS: Ana spend is 15.0'
  ELSE 'FAIL: Ana spend should be 15.0'
END;
