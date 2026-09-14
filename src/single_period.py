def replicate(market,h):
    """Price a one-period derivative with payoff h by replication.

    Returns (x, y, O0, q): x shares of stock, y units of the bond,
    the time-0 price, and the risk-neutral probability.
    """
    O_up = h(market.S_up)
    O_down = h(market.S_down)
    x = (O_up - O_down) / (market.S_up - market.S_down)
    y = (O_up - x * market.S_up) / market.A1
    O0 = x *market.S0 + y * market.A0
    q = (market.R - market.d)/(market.u - market.d)
    assert abs(O0 - (q * O_up + (1 - q) * O_down) / market.R) < 1e-6

    return x, y, O0, q

