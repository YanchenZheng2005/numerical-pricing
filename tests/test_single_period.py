import math
from src.market import Market 
from src.single_period import replicate

def test_case_1_single_period_call():
    A0 = 1
    A1 = math.exp(0.0125)
    m = Market(S0 = 20, u = 1.2, d= 0.9, A0 = A0, A1 = A1)
    h = lambda S: max(S-20,0)
    x,y,O0,q = replicate(m,h)
    R = A1/A0
    expected_x = 2/3
    expected_yA0 = -18 * expected_x / R
    expected_O0 = 20 * expected_x + expected_yA0
    assert abs(x - expected_x) < 1e-6
    assert abs(y*A0 - expected_yA0) < 1e-6
    assert abs(O0 - expected_O0) < 1e-6
