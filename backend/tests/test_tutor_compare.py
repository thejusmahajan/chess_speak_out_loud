"""Track T (Tutor-style comparison) — T1 primitives: ValueCount, weighted_mean,
grade, importance. Lifted from lila modules/tutor (TutorNumber)."""
import math

import pytest

from backend.training import metrics as m


def test_weighted_mean_is_count_weighted():
    # 0.2 over 90 samples vs 0.9 over 10 -> pooled mean pulled toward 0.2
    vc = m.weighted_mean([m.ValueCount(0.2, 90), m.ValueCount(0.9, 10)])
    assert vc.count == 100
    assert vc.value == pytest.approx((0.2 * 90 + 0.9 * 10) / 100)  # 0.27


def test_weighted_mean_empty_is_none():
    assert m.weighted_mean([]) is None
    assert m.weighted_mean([m.ValueCount(0.5, 0)]) is None  # zero total count


def test_grade_sign_and_divisor_scaling():
    # mine better than ref by exactly one divisor -> +1.0
    assert m.grade(mine=0.30, ref=0.20, divisor=0.10) == pytest.approx(1.0)
    # worse -> negative; larger divisor -> smaller magnitude
    assert m.grade(0.20, 0.30, 0.10) == pytest.approx(-1.0)
    assert m.grade(0.30, 0.20, 0.20) == pytest.approx(0.5)


def test_grade_reverse_for_lower_is_better():
    # a LOWER blind rate than the reference should grade POSITIVE under reverse
    assert m.grade(0.10, 0.30, 0.20, reverse=True) == pytest.approx(1.0)
    # and a higher blind rate grades negative
    assert m.grade(0.50, 0.30, 0.20, reverse=True) == pytest.approx(-1.0)


def test_grade_rejects_nonpositive_divisor():
    with pytest.raises(ValueError):
        m.grade(0.3, 0.2, 0.0)


def test_importance_scales_with_sqrt_count_and_is_unsigned():
    # abs(grade) * sqrt(count * weight)
    assert m.importance(-2.0, count=9, weight=1.0) == pytest.approx(2.0 * 3.0)
    # 4x the sample -> 2x the importance (sqrt)
    base = m.importance(1.0, count=25)
    quad = m.importance(1.0, count=100)
    assert quad == pytest.approx(2 * base)
    # weight multiplies under the sqrt
    assert m.importance(1.0, 100, weight=0.0) == 0.0
    assert m.importance(1.0, 100, weight=35) == pytest.approx(math.sqrt(100 * 35))


def test_importance_ranks_wellsampled_over_thin_extreme():
    # the small-sample distortion the raw-count sort suffers from: a 1-game
    # 100%-blind opening must NOT outrank a well-sampled moderate weakness.
    thin = m.importance(m.grade(1.0, 0.2, 0.5, reverse=True), count=1)      # extreme, n=1
    solid = m.importance(m.grade(0.45, 0.2, 0.5, reverse=True), count=200)  # moderate, n=200
    assert solid > thin
