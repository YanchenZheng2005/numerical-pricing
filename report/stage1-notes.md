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


## Validation strategy

The tests fall into three layers, in increasing order of independence from
outside information.

**Layer 1 — reference values.** Specific cases are checked against figures
worked out by hand or taken from course material: the one-period example,
the two-period European call and put, the two-period American put. These
tests are the easiest to write and the weakest evidence. They confirm only
the cases actually listed, and they are only as reliable as the reference
itself, as the 1e-4 discrepancy in the two-period call shows.

**Layer 2 — structural properties.** Relations that any correct pricer must
satisfy, whatever the parameters: put–call parity, American value at least
European value, price bounds, monotonicity in the strike, and the range of
the hedge ratio. These hold identically in the model and need no external
figures, so they can be checked on large trees and over many parameter sets.

**Layer 3 — self-financing.** The replicating strategy is checked node by
node on a 200-step tree. This is the strongest of the three, and is
described below.

Layer 1 lives in `test_lattice.py`, layers 2 and 3 in `test_structure.py`.

## The replicating portfolio tree

At node (i, j) the holder sets up a portfolio of x shares and a bond
position, held until the next layer, that reproduces the option value at
both children:

    x·S(i+1, j)   + (bond position at i+1) = V(i+1, j)
    x·S(i+1, j+1) + (bond position at i+1) = V(i+1, j+1)

Subtracting,

    x(i, j) = [ V(i+1, j) − V(i+1, j+1) ] / [ S(i+1, j) − S(i+1, j+1) ].

These are the one-period replication equations of Section 1, solved once at
every node. The coefficient matrix is invertible because S(i+1, j) ≠
S(i+1, j+1), so each node has a unique hedge.

`portfolio_tree` stores the bond leg as B(i, j), its value at node (i, j)
rather than at the children:

    B(i, j) = [ V(i+1, j) − x(i, j)·S(i+1, j) ] / R.

Storing the value at the node, rather than a number of bonds, means both
legs of the portfolio are quoted at the same date as the stock price at that
node, which is what the self-financing comparison needs.

Portfolios exist on layers 0 through n−1 only; no position is set up at
maturity. For S(0) = 50, K = 55, u = 1.2, d = 0.9, r = 5%, T = 0.5, n = 2:

    (0, 0):  x = 0.420013,  B = −18.665810
    (1, 0):  x = 0.944444,  B = −50.366468
    (1, 1):  x = 0,         B = 0

At (1, 1) both children are out of the money, so the portfolio replicating
a payoff of 0 in both states is the empty portfolio.

## Self-financing

The strategy is self-financing if, at every node, liquidating the portfolio
carried in from the previous layer pays exactly for the portfolio required
going forward:

    x(p)·S(i, j) + B(p)·R = x(i, j)·S(i, j) + B(i, j),

where p is a parent of (i, j). If this holds at every node, the initial
outlay x(0,0)·S(0) + B(0,0) grows into the option payoff with no further
funding, which is what makes that outlay the no-arbitrage price.

The condition simplifies. The left-hand side is the value at (i, j) of a
portfolio constructed to be worth V(i, j) there, so it equals V(i, j) by
construction, for either parent. The test therefore reduces to

    x(i, j)·S(i, j) + B(i, j) = V(i, j)    for all 0 ≤ j ≤ i ≤ n−1,

which also covers the root, where the two sides are the initial cost and the
option price.

It matters that the check is written this way round. The obvious formulation
— roll the previous portfolio forward and compare it with V at the new node
— is an identity: x(p) and B(p) were *defined* by making that equation hold.
It would pass whatever the backward recursion computed.

The form actually used is not an identity, because the two sides come from
different layers. The left-hand side is built from V(i+1, ·) through the
replication equations; substituting them and simplifying gives

    x(i, j)·S(i, j) + B(i, j)
        = [ q·V(i+1, j) + (1 − q)·V(i+1, j+1) ] / R.

The right-hand side, V(i, j), comes from `Euro_option_A`. Equality at every
node therefore says that replication and risk-neutral discounting produce
the same value everywhere — the multi-period version of the two-route
agreement checked in the one-period case. An error in the recursion breaks
it: with a misplaced parenthesis discounting only the second term, node
(1, 0) of the example above would be recorded as 6.379454 while the
portfolio built from layer 2 costs 6.300199.

The test runs on European calls and puts at n = 2 and n = 200, with the
largest deviation on the order of 1e-15.

## Structural properties

**Price bounds.** At every node, writing m = n − i for the steps remaining,

    max( S(i, j) − K/R^m, 0 ) ≤ C(i, j) ≤ S(i, j),
    max( K/R^m − S(i, j), 0 ) ≤ P(i, j) ≤ K/R^m.

The call lower bound holds because the terminal payoff max(S − K, 0)
dominates, state by state, both the payoff of holding one share against a
loan of K/R^m and the payoff of holding nothing. A price below the bound
could be arbitraged by buying the option and selling the dominated
portfolio. The other three bounds are the same argument. These are European
bounds: an American put may exceed K/R^m, since early exercise pays K rather
than its discounted value.

**Monotonicity in the strike.** For K₁ < K₂, max(S − K₁, 0) ≥ max(S − K₂, 0)
at every terminal node, and the weights in the backward recursion are
positive, so C(K₁) ≥ C(K₂). Puts go the other way. Checked at the root over
an increasing list of strikes.

**Hedge ratio.** For a call, 0 ≤ x(i, j) ≤ 1 at every node; for a put,
−1 ≤ x(i, j) ≤ 0. The numerator of x is the difference of the two child
values and the denominator the difference of the two child prices, so the
bounds say that the option value is non-decreasing in the stock price and
changes by no more than the stock price does. Both properties hold for the
terminal payoff and are preserved by the recursion.

Strikes of 30, 50, 55 and 80 against S(0) = 50 are used throughout, so that
deep in-the-money, near-the-money and deep out-of-the-money nodes are all
covered. Near-the-money strikes alone would leave x far from ±1 and 0, and
the bounds would never be tested where they are tight.

## Tolerances

Self-financing is an internal consistency check: both sides are ordinary
floating-point results of the same magnitude, and the observed deviation is
around 1e-15, so 1e-10 is used. The structural inequalities are compared
against bounds that are attained exactly in some regions — x = 1 deep in the
money, equal prices for two strikes far out of the money — so each
inequality is relaxed by 1e-12 to absorb rounding, rather than tightened.

Absolute tolerances have to be read together with the size of the numbers
involved. Floating-point arithmetic carries a relative precision of about
1e-16, so absolute errors grow with the magnitude of the values. The n = 200
tests use u = 1.02 and d = 0.98, giving a highest node price near 2650 and
deviations below 1e-14. With u = 1.05 and d = 0.95 the highest node price is
about 823,000 and the deviation rises to 2.3e-10, which would fail at 1e-10
without anything being wrong with the code. Those step sizes are also the
realistic ones: over 200 steps of a one-year horizon, a 2% move per step is
already large.