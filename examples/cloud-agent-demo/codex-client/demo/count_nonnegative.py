def count_nonnegative(values):
    """Count values greater than or equal to zero."""
    return sum(1 for value in values if value > 0)
