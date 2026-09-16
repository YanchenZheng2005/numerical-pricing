# Stage 1 Notes

## No-arbitrage condition

The one-period market is specified by the stock price S(0) with its two
time-1 outcomes S(0)u and S(0)d, and by a bond with prices A(0) and A(1).
Writing R = A(1)/A(0) for the gross return on the bond, all three assets are
measured on the same scale: u and d are the stock's gross returns in the up
and down states, and R is the bond's certain gross return. The market admits
no arbitrage if and only if

    d < R < u.

Only the ratio R enters the condition; the levels of A(0) and A(1) are
irrelevant, so the bond's unit of account has no effect on any price. Note
also that this form does not presuppose S(0) = A(0), unlike the equivalent
statement S(0)d < A(1) < S(0)u found in the textbook.

Both inequalities are strict. Equality is enough to construct an arbitrage,
as the two constructions below make clear.

## Arbitrage when R >= u

Short one share of the stock and deposit the proceeds S(0) in the bond. The
net cost at time 0 is S(0) - S(0) = 0. At time 1 the deposit is worth S(0)R
and the short position must be closed at S(0)u or S(0)d, so the net payoff is
S(0)(R - u) in the up state and S(0)(R - d) in the down state. Since R >= u > d,
the first is non-negative and the second is strictly positive. The strategy
costs nothing, never loses, and pays strictly more than zero with positive
probability, which is an arbitrage. When R > u strictly, both states pay
strictly more than zero.

## Arbitrage when R <= d

Borrow S(0) at the bond rate and buy one share of the stock. Again the net
cost at time 0 is zero. At time 1 the loan must be repaid at S(0)R and the
share is worth S(0)u or S(0)d, giving a net payoff of S(0)(u - R) in the up
state and S(0)(d - R) in the down state. Since u > d >= R, the first is
strictly positive and the second is non-negative. This is the mirror image of
the previous case, and it is an arbitrage for the same reason.

## Two routes to the price, and why both are implemented

The replicating-portfolio route solves for the pair (x, y) whose time-1 value
matches the derivative in both states, and then prices the derivative at the
cost of that portfolio, x S(0) + y A(0). The risk-neutral route computes
q = (R - d) / (u - d) and discounts the expected payoff under q at rate R.

The two agree, and the agreement is not a coincidence: q is what falls out of
the replication argument once it is solved in general, not a separate
assumption. Implementing only the risk-neutral formula would hide this, so
both routes are computed independently and the implementation asserts that
they agree at every node. The tolerance is 1e-12; the observed discrepancy on
the test cases is of order 1e-16, consistent with floating-point rounding
alone.

## Multi-period lattice (European)

### Recombination

The interval [0, T] is split into n steps of length Δt = T/n. Over each step
the stock is multiplied by u or d and the bond by R = exp(r·Δt), so every step
is a copy of the one-period market above. Because

    S(0)·u·d = S(0)·d·u,

an up-move followed by a down-move lands on the same price as the reverse
order. Layer i therefore holds only i + 1 distinct nodes instead of 2^i, and
the whole tree has

    (n + 1)(n + 2) / 2

nodes. For n = 500 this is 125,751 nodes, against 2^500 terminal paths in a
non-recombining tree. Recombination is what makes the binomial method usable
at realistic step counts.

### Indexing convention

Node (i, j) is the node at layer i reached after j down-moves:

    S(i, j) = S(0) · u^(i−j) · d^j,    0 ≤ j ≤ i.

Within a layer, prices are therefore stored from largest to smallest. For
S(0) = 50, u = 1.2, d = 0.9, layer 2 is [72, 54, 40.5]. The up-child of (i, j)
is (i+1, j) and the down-child is (i+1, j+1), so backward induction reads

    V(i, j) = [ q·V(i+1, j) + (1 − q)·V(i+1, j+1) ] / R,
    q = (R − d) / (u − d),

with V(n, j) = h(S(n, j)) at maturity. Both R and q are per-step quantities.

The lattice functions take (S0, u, d, r, T, n, h) directly. u, d and R are
shared by every node in the tree, while S0 only describes the root, so the
per-node prices are generated from S0 once in `stock_lattice` rather than
carried inside a market object.

### Two memory strategies

`Euro_option_A` stores the full (n+1) × (n+1) value array and returns it.
Memory is O(n²), and every intermediate value remains available.

`Euro_option_B` keeps a single array of length n + 1 and overwrites it layer
by layer. Memory is O(n), but only V(0, 0) survives. The in-place update
computes V[j] from V[j] and V[j+1]; iterating j upward is safe because V[j+1]
has not yet been overwritten when V[j] is computed. The loop variable `i` in
this function is the number of nodes in the current layer, not the layer
index, so `range(i)` gives exactly the nodes to update.

Both are kept because they serve different purposes. When only the price is
needed, B is strictly better. Anything that looks inside the tree (the
early-exercise boundary, the self-financing check at each node, lattice
plots) requires A. The two implementations of the same recursion must also
agree to within 1e-12, which serves as a cross-check in the same spirit as
the replication versus risk-neutral comparison in the one-period case.

### Validation

The tests check the stock lattice, the two-period call and put examples,
put–call parity at full precision, agreement with `replicate` when n = 1,
and agreement between A and B for several n. The quoted reference values
for the two-period example (2.3350 and 6.3003) differ from the
full-precision results (2.334853… and 6.300199…) by about 1e-4, and the
source of the discrepancy has not been identified. Those two tests
therefore use a tolerance of 1e-3 as a coarse check only. Exactness rests
on the parity, n = 1 and A/B tests, none of which depend on external
figures.

## American options and the early-exercise boundary

### Change to the recursion

An American holder may exercise at any node. The discounted expectation
from the European recursion becomes the continuation value

    C(i, j) = [ q·V(i+1, j) + (1 − q)·V(i+1, j+1) ] / R,

and the node value is the better of continuing and exercising:

    V(i, j) = max( C(i, j), h(S(i, j)) ).

At maturity V(n, j) = h(S(n, j)) as before. The tree structure and
indexing are unchanged.

### Exercise boundary

Node (i, j) is flagged as an exercise node when immediate exercise is
strictly better than continuing:

    h(S(i, j)) > C(i, j).

Ties are treated as continuation. At maturity there is no continuation, so
the condition reduces to h(S(n, j)) > 0; out-of-the-money terminal nodes are
not flagged.

The flag has to be set inside the backward loop, while C(i, j) is still
available. Once the max has been taken, only the larger value remains, and
comparing V with h afterwards cannot distinguish "exercise won" from a tie.

Only the full-tree strategy is implemented for American options, since the
recursion needs S(i, j) at every node and the boundary itself is a per-node
output.

### Worked example

S(0) = 50, K = 55, u = 1.2, d = 0.9, r = 5%, T = 0.5, n = 2 (put).

At node (1, 1), S = 45, so h = 10, while the continuation value is 9.3168.
The holder exercises and V(1, 1) = 10. At node (1, 0), S = 60, h = 0 and
C = 0.6170, so the holder continues. At the root, h = 5 < C = 6.3984.

The American put is worth 6.3984, against 5.9769 for the European put, an
early-exercise premium of about 0.4215. The exercise region is
{(1, 1), (2, 1), (2, 2)}.

### American call without dividends

With R > 1 and no dividends, the American call has the same price as the
European call (2.334853… in the example above), and no node is flagged.
The reason: at any node with m steps to maturity, put–call parity gives

    C_E = S − K / R^m + P_E ≥ S − K / R^m > S − K,

and the American continuation value is at least C_E. Continuing is
therefore always worth more than exercising, and h > C never holds.

### Validation

The tests check V(1, 1) = 10 and the exact exercise region in the example
above, and that the American put is never cheaper than the European put for
K ∈ {40, 50, 55, 70} and n ∈ {1, 2, 5, 20}.