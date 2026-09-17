import backtrader as bt


class MovingAverageCross(bt.Strategy):

    params = (
        ("fast_period", 20),
        ("slow_period", 50),
    )

    def __init__(self):

        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.params.fast_period
        )

        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.params.slow_period
        )

        self.crossover = bt.indicators.CrossOver(
            self.fast_ma,
            self.slow_ma
        )

    def next(self):

        if not self.position:

            if self.crossover > 0:
                self.buy()

        else:

            if self.crossover < 0:
                self.close()