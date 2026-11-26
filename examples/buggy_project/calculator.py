"""Small synthetic repository for the DevMind walkthrough."""


def safe_divide(numerator: float, denominator: float) -> float | None:
    """Divide two numbers, returning None when denominator is zero."""
    if denominator == 0:
        return None
    return numerator / denominator

