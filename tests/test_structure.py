import pytest, math
from src.lattice import portfolio_tree, stock_lattice, Euro_option_A
from src.payoffs import call, put

def check_self_financing(S0, u, d, r, T, n, h):
    stock_price = stock_lattice(S0, u, d, n)
    option_price = Euro_option_A(S0, u, d, r, T, n, h)
    stock_share_tree, bond_value_tree = portfolio_tree(S0, u, d, r, T, n, h)

    for i in range(n):
        for j in range(i + 1):
            assert abs(stock_share_tree[i][j] * stock_price[i][j] + bond_value_tree[i][j] - option_price[i][j]) < 1e-10

def test_self_financing_call_n2():
    check_self_financing(50, 1.2, 0.9, 0.05, 0.5, 2, call(55))

def test_self_financing_put_n2():
    check_self_financing(50, 1.2, 0.9, 0.05, 0.5, 2, put(55))

def test_self_financing_call_n200():
    check_self_financing(50, 1.02, 0.98, 0.05, 1.0, 200, call(55))

def test_self_financing_put_n200():
    check_self_financing(50, 1.02, 0.98, 0.05, 1.0, 200, put(55))

def check_price_bounds_call(S0, u, d, r, T, n, h, K):
    stock_price = stock_lattice(S0, u, d, n)
    option_price = Euro_option_A(S0, u, d, r, T, n, h)
    R = math.exp(r * T / n)
    for i in range(n + 1):
        for j in range(i + 1):
            assert max(stock_price[i][j] - K / R ** (n - i), 0) <= option_price[i][j] + 1e-12
            assert option_price[i][j] <= stock_price[i][j] + 1e-12

def check_price_bounds_put(S0, u, d, r, T, n, h, K):
    stock_price = stock_lattice(S0, u, d, n)
    option_price = Euro_option_A(S0, u, d, r, T, n, h)
    R = math.exp(r * T / n)
    for i in range(n + 1):
        for j in range(i + 1):
            assert max(K / R ** (n - i) - stock_price[i][j], 0) <= option_price[i][j] + 1e-12
            assert option_price[i][j] <= K / R ** (n - i) + 1e-12


def test_price_bounds_call():
    for K in [30, 50, 55, 80]:
        check_price_bounds_call(50, 1.02, 0.98, 0.05, 1, 200, call(K), K)

def test_price_bounds_put():
    for K in [30, 50, 55, 80]:
        check_price_bounds_put(50, 1.02, 0.98, 0.05, 1, 200, put(K), K)



def test_monotonicity_call():
    price = 10 ** 10
    for K in [30, 40, 50, 55, 60, 70, 80]:
        option_price = Euro_option_A(50, 1.02, 0.98, 0.05, 1, 200, call(K))
        assert price >= (option_price[0][0] - 1e-12)
        price = option_price[0][0]

def test_monotonicity_put():
    price = 0
    for K in [30, 40, 50, 55, 60, 70, 80]:
        option_price = Euro_option_A(50, 1.02, 0.98, 0.05, 1, 200, put(K))
        assert (price - 1e-12) <= option_price[0][0]
        price = option_price[0][0]

def check_delta_range_call(S0, u, d, r, T, n, h):
    stock_share_tree, _ = portfolio_tree(S0, u, d, r, T, n, h)
    for i in range(n):
        for j in range(i + 1):
            assert -1e-12 <= stock_share_tree[i][j] <= 1 + 1e-12

def check_delta_range_put(S0, u, d, r, T, n, h):
    stock_share_tree, _ = portfolio_tree(S0, u, d, r, T, n, h)
    for i in range(n):
        for j in range(i + 1):
            assert -1 -1e-12 <= stock_share_tree[i][j] <= 1e-12


def test_delta_range_call():
    for K in [30, 50, 55, 80]:
        check_delta_range_call(50, 1.02, 0.98, 0.05, 1, 200, call(K))

def test_delta_range_put():
    for K in [30, 50, 55, 80]:
        check_delta_range_put(50, 1.02, 0.98, 0.05, 1, 200, put(K))