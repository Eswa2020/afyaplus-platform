import time


class SpendBreaker:
    def __init__(self, max_usd_per_min=0.50):
        self.max_usd_per_min = max_usd_per_min
        self.window_start = time.time()
        self.spent = 0.0
        self.open = False

    def record(self, usd: float):
        now = time.time()
        if now - self.window_start > 60:
            self.window_start, self.spent = now, 0.0
            self.open = False
        self.spent += usd
        if self.spent > self.max_usd_per_min:
            self.open = True

    def allow(self) -> bool:
        return not self.open


if __name__ == '__main__':
    breaker = SpendBreaker(max_usd_per_min=0.50)
    for i in range(1, 6):
        breaker.record(0.15)
        print(f'call={i} spent={breaker.spent:.2f} allow={breaker.allow()}')