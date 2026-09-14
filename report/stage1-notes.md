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