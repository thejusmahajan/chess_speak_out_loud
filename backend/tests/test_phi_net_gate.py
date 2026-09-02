"""Guards for the two phi_net decisions that were most recently wrong.

Both of these were live defects found in review, not hypotheticals:

* ``b1_verdict`` applied the full falsification gate set to the B1 rung, so a B1
  of 0.66 -- a good result at that scale -- aborted the Kaggle session before B2
  ever started. (Independent audit, 2026-09-02.)
* ``roc_auc`` walked the sorted scores in a Python loop, costing 1.22 s per call
  and one host-device synchronisation per element on CUDA. (Self-review,
  2026-09-02.)

No GPU, no network, no dataset needed.
"""

import torch

from phi_net.metrics import roc_auc
from phi_net.run_kaggle import b1_verdict


def _brute_force_auc(y: torch.Tensor, s: torch.Tensor) -> float:
    """Pairwise Mann-Whitney definition, half credit for ties. O(n^2), obviously
    correct, and therefore the right thing to check the fast version against."""
    pos, neg = s[y == 1], s[y == 0]
    wins = (pos[:, None] > neg[None, :]).float()
    ties = (pos[:, None] == neg[None, :]).float()
    return float((wins + 0.5 * ties).mean())


def test_b1_proceeds_when_signal_is_present_but_below_f1():
    """The exact case that used to kill the run: real signal, below F1's 0.70."""
    proceed, message = b1_verdict(b1_auc=0.66, material_auc=0.49)
    assert proceed is True
    assert "proceeding to B2" in message


def test_b1_stops_when_phi_does_not_beat_material():
    proceed, message = b1_verdict(b1_auc=0.50, material_auc=0.51)
    assert proceed is False
    assert "REPRESENTATION result" in message


def test_b1_stops_when_f0_fails_even_if_phi_scores_well():
    """A high AUC on a dataset separable by piece counts is worse than useless."""
    proceed, message = b1_verdict(b1_auc=0.80, material_auc=0.71)
    assert proceed is False
    assert "F0 failed" in message


def test_b1_ties_go_to_stopping():
    assert b1_verdict(b1_auc=0.50, material_auc=0.50)[0] is False


def test_roc_auc_matches_brute_force_without_ties():
    torch.manual_seed(0)
    y = (torch.rand(300) > 0.5).float()
    s = torch.rand(300)
    assert abs(roc_auc(y, s) - _brute_force_auc(y, s)) < 1e-6


def test_roc_auc_matches_brute_force_with_heavy_ties():
    """Ties are not hypothetical: the material baseline is fit on ten integer
    piece counts, so thousands of rows share a score exactly."""
    torch.manual_seed(1)
    y = (torch.rand(400) > 0.5).float()
    s = torch.randint(0, 5, (400,)).float()
    assert abs(roc_auc(y, s) - _brute_force_auc(y, s)) < 1e-6


def test_roc_auc_is_nan_when_a_class_is_missing():
    y = torch.ones(10)
    assert roc_auc(y, torch.rand(10)) != roc_auc(y, torch.rand(10)) or True
    assert str(roc_auc(y, torch.rand(10))) == "nan"
