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
        for j in range(i + 1):
            if i == n:
                option_price[i][j] = h(stock_price[i][j])
            else:
                option_price[i][j] = (q * option_price[i+1][j] + (1 - q) * option_price[i+1][j+1]) / R
    return option_price


def portfolio_tree(S0, u, d, r, T, n, h):
    stock_price = stock_lattice(S0, u, d, n)
    option_price = Euro_option_A(S0, u, d, r, T, n, h)
    stock_share_tree = [[0] * (n + 1) for _ in range(n + 1)]
    bond_value_tree = [[0] * (n + 1) for _ in range(n + 1)]
    R = math.exp(r * T / n)
    for i in range(n):
        for j in range(i + 1):
            O_up = option_price[i + 1][j]
            O_down = option_price[i + 1][j + 1]
            S_up = stock_price[i + 1][j]
            S_down = stock_price[i + 1][j + 1]

            delta = (O_up - O_down) / (S_up - S_down)
            B = (O_up - delta * S_up) / R

            stock_share_tree[i][j] = delta
            bond_value_tree[i][j] = B

    return stock_share_tree, bond_value_tree


def Euro_option_B(S0, u, d, r, T, n, h):
    stock_price = stock_lattice(S0, u, d, n)
    option_price = [h(stock_price[n][_]) for _ in range(n + 1)]
    R = math.exp(r * T / n)
    q = (R - d) / (u - d)
    for i in range(n,-1,-1):
        for j in range(i):
            option_price[j] = (q * option_price[j] + (1 - q) * option_price[j+1]) / R
    return option_price[0]

def American_option_A(S0, u, d, r, T, n, h):
    stock_price = stock_lattice(S0, u, d, n)
    R = math.exp(r * T / n)
    q = (R - d) / (u - d)
    option_price = [[0] * (n + 1) for _ in range(n + 1)]
    exercise = [[False] * (n + 1) for _ in range(n + 1)]
    for i in range(n,-1,-1):
        for j in range(i+1):
            if i == n:
                if h(stock_price[i][j]) > 0 :
                    exercise[i][j] = True
                option_price[i][j] = h(stock_price[i][j])
            else:
                holding_value = (q * option_price[i+1][j] + (1 - q) * option_price[i+1][j+1]) / R
                exercise_value = h(stock_price[i][j])

                if holding_value >= exercise_value:
                    exercise[i][j] = False 
                    option_price[i][j] = holding_value
                else:
                    exercise[i][j] = True
                    option_price[i][j] = exercise_value

    return option_price, exercise
