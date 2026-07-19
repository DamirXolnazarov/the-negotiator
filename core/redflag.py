def is_redflag(total: float, benchmark_low: float, threshold_pct: float = 30) -> dict:
    """
    Returns a structured verdict with reasoning, so the report can show WHY
    a quote was flagged, not just that it was.
    """
    if total is None or benchmark_low is None:
        return {"flagged": False, "reason": None}

    cutoff = benchmark_low * (1 - threshold_pct / 100)
    if total < cutoff:
        pct_below = round(100 * (benchmark_low - total) / benchmark_low, 1)
        return {
            "flagged": True,
            "reason": f"${total:.0f} is {pct_below}% below the ${benchmark_low:.0f} benchmark low — "
                      f"treat as a warning sign, not a win (source: FMCSA/moveBuddha)."
        }
    return {"flagged": False, "reason": None}