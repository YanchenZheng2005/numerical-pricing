class ArbitrageError(Exception):
    """Raised when the market parameters admit an arbitrage."""
    pass

class Market:
    def __init__(self, S0, u, d, A0, A1):
        self.S0 = S0
        self.u = u
        self.d = d
        self.A0 = A0
        self.A1 = A1
    
        self.S_up = S0 * u
        self.S_down = S0 * d
        
        self.R = A1 / A0

        if self.R >= self.u:
                raise ArbitrageError("We can shortsell 1 share of stock and deposit S0 in bank accounts to arbitrage")
                    
        
        if self.R <= self.d:
                raise ArbitrageError("We can buy 1 share of stock and borrow S0 from bank accounts to arbitrage")
        

                    

    
