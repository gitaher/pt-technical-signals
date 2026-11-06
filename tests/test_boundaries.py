import copy
import unittest

import test_verifier as helpers

from plugin.logic import solve
from verifier import verify_input


class BoundaryTests(unittest.TestCase):
    setUp = helpers.VerifierTests.setUp
    check = helpers.VerifierTests.check

    def reject(self, x):
        self.assertFalse(verify_input("compute", x)["valid"])

    def accept(self, x, gold):
        self.assertTrue(self.check(gold, x))
        self.assertEqual(solve(x), gold)

    def test_flat_rsi_and_hold(self):
        x = copy.deepcopy(self.x)
        for r in x["bars"]:
            r["close"] = 10.0
        self.accept(x, {"sma_short": 10.0, "sma_long": 10.0, "rsi": 50.0, "signal": "hold"})

    def test_all_gains(self):
        x = copy.deepcopy(self.x)
        for i, r in enumerate(x["bars"]):
            r["close"] = float(i + 1)
        self.accept(x, {"sma_short": 4.5, "sma_long": 3.5, "rsi": 100.0, "signal": "buy"})

    def test_all_losses(self):
        x = copy.deepcopy(self.x)
        for i, r in enumerate(x["bars"]):
            r["close"] = float(10 - i)
        self.accept(x, {"sma_short": 6.5, "sma_long": 7.5, "rsi": 0.0, "signal": "sell"})

    def test_future_price_cannot_change_answer(self):
        x = copy.deepcopy(self.x)
        x["bars"][-1]["close"] = 1e12
        self.accept(x, self.gold)

    def test_insufficient_history(self):
        x = copy.deepcopy(self.x)
        x["cutoff"] = "2026-01-03"
        self.reject(x)

    def test_duplicate_date(self):
        x = copy.deepcopy(self.x)
        x["bars"].append(copy.deepcopy(x["bars"][0]))
        self.reject(x)

    def test_unsorted_bars(self):
        x = copy.deepcopy(self.x)
        x["bars"].reverse()
        self.reject(x)

    def test_zero_and_nonfinite_close(self):
        for v in [0.0, -1.0, float("inf"), float("nan"), True, 1e13]:
            x = copy.deepcopy(self.x)
            x["bars"][0]["close"] = v
            self.reject(x)

    def test_period_zero_or_equal_windows(self):
        for k, v in [("rsi_period", 0), ("short_window", 4), ("long_window", 1), ("short_window", True)]:
            x = dict(self.x, **{k: v})
            self.reject(x)

    def test_precision_tolerance(self):
        self.assertTrue(self.check(dict(self.gold, sma_short=12.0 + 1e-10)))
        self.assertFalse(self.check(dict(self.gold, sma_short=12.01)))

    def test_impossible_date(self):
        self.reject(dict(self.x, cutoff="2026-02-29"))
