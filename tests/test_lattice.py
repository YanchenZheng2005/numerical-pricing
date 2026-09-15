import math
import pytest
from src.payoffs import call, put
from src.market import Market
from src.single_period import replicate
from src.lattice import stock_lattice, Euro_option_A, Euro_option_B





# Case 2 / 3 parameters, shared by most tests below.
PARAMS = dict(S0=50, u=1.2, d=0.9, r=0.05, T=0.5, n=2)
K = 55


def test_stock_lattice_two_periods():
    """Node (i, j) holds S0 * u**(i-j) * d**j, with j counting down-moves."""
    S = stock_lattice(50, 1.2, 0.9, 2)
    assert abs(S[0][0] - 50.0) < 1e-12
    assert abs(S[1][0] - 60.0) < 1e-12
    assert abs(S[1][1] - 45.0) < 1e-12
    assert abs(S[2][0] - 72.0) < 1e-12
    assert abs(S[2][1] - 54.0) < 1e-12
    assert abs(S[2][2] - 40.5) < 1e-12


def test_case2_european_call():
    """Two-period European call: C0 = 2.3350, Cu = 6.3003."""
    V = Euro_option_A(h=call(K), **PARAMS)
    assert abs(V[0][0] - 2.3350) < 1e-3
    assert abs(V[1][0] - 6.3003) < 1e-3


def test_case3_european_put():
    """Two-period European put on the same market: P0 = 5.9769."""
    V = Euro_option_A(h=put(K), **PARAMS)
    assert abs(V[0][0] - 5.9769) < 1e-3


def test_put_call_parity():
    """C0 - P0 = S0 - K / R**n, computed at full precision."""
    C = Euro_option_A(h=call(K), **PARAMS)[0][0]
    P = Euro_option_A(h=put(K), **PARAMS)[0][0]
    R = math.exp(PARAMS["r"] * PARAMS["T"] / PARAMS["n"])
    assert abs((C - P) - (PARAMS["S0"] - K / R ** PARAMS["n"])) < 1e-12


def test_single_step_matches_replication():
    """With n = 1 the lattice must reproduce the single-period result."""
    R = math.exp(0.0125)
    m = Market(S0=20, u=1.2, d=0.9, A0=1, A1=R)
    h = call(20)
    _, _, O0, _ = replicate(m, h)
    V = Euro_option_A(S0=20, u=1.2, d=0.9, r=0.05, T=0.25, n=1, h=h)
    assert abs(V[0][0] - O0) < 1e-12


@pytest.mark.parametrize("n", [1, 2, 3, 10, 50])
def test_both_memory_strategies_agree(n):
    """The rolling one-dimensional scheme must reproduce the full lattice."""
    a = Euro_option_A(S0=50, u=1.2, d=0.9, r=0.05, T=0.5, n=n, h=call(K))[0][0]
    b = Euro_option_B(S0=50, u=1.2, d=0.9, r=0.05, T=0.5, n=n, h=call(K))
    assert abs(a - b) < 1e-12