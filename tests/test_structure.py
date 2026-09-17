import pytest
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

