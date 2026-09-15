"""
Fixed-precision money arithmetic for PKR.

All monetary values in the system are exact base-10 decimals with two
fractional digits (paisa). Floating point (`float`) must never touch a money
value — binary floats cannot represent values like 0.10 exactly, which causes
drift and reconciliation errors.

Use `to_money()` at every boundary where a value enters arithmetic or leaves
the system, and `money_sum()` to total an iterable. Rounding is ROUND_HALF_UP
(the conventional rule for currency), not Python's default banker's rounding.
"""
from decimal import Decimal, ROUND_HALF_UP

CURRENCY = 'PKR'

# Smallest representable unit: 1 paisa.
QUANTUM = Decimal('0.01')
ZERO = Decimal('0.00')


def to_money(value):
    """
    Coerce any numeric-ish input to a 2-dp Decimal, quantized HALF_UP.

    Floats are converted via `str()` first so we capture the value the caller
    *typed* (0.1) rather than its binary approximation (0.1000000000000000055…).
    None becomes ZERO.
    """
    if value is None:
        return ZERO
    if isinstance(value, Decimal):
        dec = value
    elif isinstance(value, float):
        dec = Decimal(str(value))
    else:
        # int / numeric string
        dec = Decimal(str(value))
    return dec.quantize(QUANTUM, rounding=ROUND_HALF_UP)


def money_sum(values):
    """Exact total of an iterable of money-ish values, quantized to 2 dp."""
    total = ZERO
    for v in values:
        total += to_money(v)
    return total.quantize(QUANTUM, rounding=ROUND_HALF_UP)
