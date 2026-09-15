"""Payoff functions for options written on a single underlying.

Each factory returns a function mapping a terminal stock price to the
option's payoff, so that pricing routines need not know which contract
they are valuing.
"""


def call(K):
    """Return the payoff function of a European call with strike K."""
    return lambda S: max(S - K, 0.0)


def put(K):
    """Return the payoff function of a European put with strike K."""
    return lambda S: max(K - S, 0.0)