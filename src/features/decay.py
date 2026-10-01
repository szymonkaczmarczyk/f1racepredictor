from __future__ import annotations


class Decayed:

    __slots__ = ("weight", "total", "count", "best", "stamp")

    def __init__(self) -> None:
        self.weight = 0.0
        self.total = 0.0
        self.count = 0
        self.best: float | None = None
        self.stamp: float | None = None

    def add(self, value: float, decay: float = 1.0, weight: float = 1.0) -> None:
        self.weight = self.weight * decay + weight
        self.total = self.total * decay + value * weight
        self.count += 1
        if self.best is None or value < self.best:
            self.best = value

    def add_at(self, value: float, when: float, decay_per_unit: float, weight: float = 1.0) -> None:
        if self.stamp is not None:
            elapsed = max(0.0, when - self.stamp)
            factor = decay_per_unit ** elapsed
            self.weight *= factor
            self.total *= factor
        self.stamp = when
        self.weight += weight
        self.total += value * weight
        self.count += 1
        if self.best is None or value < self.best:
            self.best = value

    @property
    def mean(self) -> float | None:
        return self.total / self.weight if self.weight > 0 else None

    def mean_or(self, default: float | None) -> float | None:
        m = self.mean
        return default if m is None else m

    def blended(self, prior: float, prior_weight: float = 2.0) -> float:
        return (self.total + prior * prior_weight) / (self.weight + prior_weight)
