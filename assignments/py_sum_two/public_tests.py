import pytest
import solution

def test_small_positive():
    assert solution.add(1, 2) == 3

def test_zero():
    assert solution.add(0, 0) == 0

def test_negative():
    assert solution.add(-5, 2) == -3

def test_large():
    assert solution.add(10**6, 10**6) == 2 * 10**6
