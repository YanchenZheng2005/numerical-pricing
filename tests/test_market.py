import math
import pytest
from src.market import Market, ArbitrageError


def test_valid_market_constructs():
    """d < R < u holds; construction should succeed."""
    m = Market(S0=20, u=1.2, d=0.9, A0=1, A1=math.exp(0.0125))
    assert abs(m.R - math.exp(0.0125)) < 1e-12
    assert abs(m.S_up - 24) < 1e-12
    assert abs(m.S_down - 18) < 1e-12


def test_arbitrage_R_above_u():
    """R = 1.5 >= u = 1.2: the bond dominates the stock's best outcome."""
    with pytest.raises(ArbitrageError):
        Market(S0=20, u=1.2, d=0.9, A0=1, A1=1.5)


def test_arbitrage_R_below_d():
    """R = 0.8 <= d = 0.9: the stock dominates the bond."""
    with pytest.raises(ArbitrageError):
        Market(S0=20, u=1.2, d=0.9, A0=1, A1=0.8)


def test_arbitrage_R_equals_u():
    """Boundary: R = u. The condition is strict, so this must raise."""
    with pytest.raises(ArbitrageError):
        Market(S0=20, u=1.2, d=0.9, A0=1, A1=1.2)


def test_arbitrage_R_equals_d():
    """Boundary: R = d. The condition is strict, so this must raise."""
    with pytest.raises(ArbitrageError):
        Market(S0=20, u=1.2, d=0.9, A0=1, A1=0.9)


def test_bond_level_does_not_matter():
    """Only the ratio R = A1/A0 enters the model, not the levels themselves."""
    m = Market(S0=35, u=1.2, d=0.9, A0=10, A1=10.5)
    assert abs(m.R - 1.05) < 1e-12