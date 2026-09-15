import math
def stock_lattice(S0, u, d, n):
    S = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n,-1,-1):
        for j in range(i+1):
            S[i][j] = S0 * u ** (i - j) * d ** (j)
    return S

def Euro_option_A(S0, u, d, r, T, n, h):
    stock_price = stock_lattice(S0, u, d, n)
    R = math.exp(r * T / n)
    q = (R - d) / (u - d)
    option_price = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n,-1,-1):
        for j in range(i+1):
            if i == n:
                option_price[i][j] = h(stock_price[i][j])
            else:
                option_price[i][j] = (q * option_price[i+1][j] + (1 - q) * option_price[i+1][j+1]) / R
    return option_price

def Euro_option_B(S0, u, d, r, T, n, h):
    stock_price = stock_lattice(S0, u, d, n)
    option_price = [h(stock_price[n][_]) for _ in range(n + 1)]
    R = math.exp(r * T / n)
    q = (R - d) / (u - d)
    for i in range(n,-1,-1):
        for j in range(i):
            option_price[j] = (q * option_price[j] + (1 - q) * option_price[j+1]) / R
    return option_price[0]


