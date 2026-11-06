def solve(x):
    values = [r["close"] for r in x["bars"] if r["date"] <= x["cutoff"]]
    means = [sum(values[len(values) - w :]) / w for w in (x["short_window"], x["long_window"])]
    gains, losses = 0.0, 0.0
    for i in range(len(values) - x["rsi_period"], len(values)):
        delta = values[i] - values[i - 1]
        gains += max(0, delta)
        losses += -delta if delta < 0 else 0
    signal = "hold"
    if means[0] < values[-1] and means[1] < means[0]:
        signal = "buy"
    if means[0] > values[-1] and means[1] > means[0]:
        signal = "sell"
    return {
        "sma_short": means[0],
        "sma_long": means[1],
        "rsi": 100.0 * gains / (gains + losses) if gains + losses else 50.0,
        "signal": signal,
    }
