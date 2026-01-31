import solution

def test_big_ints():
    assert solution.add(10**18, 10**18) == 2 * 10**18

def test_mixed_signs():
    assert solution.add(999999999, -999999998) == 1

def test_more_negatives():
    assert solution.add(-123456, -654321) == -777777
