"""Metrics and gates, implemented in torch so they run on the GPU and need no
scikit-learn (which is *not* installed in the project's ``cszero`` env).

The gates come from `docs/plans/PLAN_CONFIGURATION_STEERING.md` section 8:

* **F0** -- material-only AUC on the built dataset must be < 0.65. Already passed
  and independently re-run at audit time; re-checked here for free, because it
  also proves the data you just loaded is the data that was audited.
* **F1** -- Phi's held-out AUC must exceed **0.70**, or configurations are not
  learnable at this representation.
* **F2** -- Phi's AUC must beat the material-only baseline by at least **0.03**,
  or Phi learned material rather than configuration.
"""

from __future__ import annotations

import torch

F0_MAX_MATERIAL_AUC = 0.65
F1_MIN_PHI_AUC = 0.70
F2_MIN_EDGE = 0.03


def roc_auc(y_true: torch.Tensor, score: torch.Tensor) -> float:
    """Rank-based ROC AUC (the Mann-Whitney U form). Ties get average ranks."""
    y = y_true.detach().float().flatten()
    s = score.detach().float().flatten()
    n_pos = float((y == 1).sum())
    n_neg = float((y == 0).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    order = torch.argsort(s)
    ranks = torch.empty_like(s)
    ranks[order] = torch.arange(1, len(s) + 1, dtype=s.dtype, device=s.device)
    # average ranks within tied groups
    sorted_s = s[order]
    start = 0
    for i in range(1, len(sorted_s) + 1):
        if i == len(sorted_s) or sorted_s[i] != sorted_s[start]:
            if i - start > 1:
                idx = order[start:i]
                ranks[idx] = ranks[idx].mean()
            start = i
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def logistic_auc(x_train: torch.Tensor, y_train: torch.Tensor,
                 x_val: torch.Tensor, y_val: torch.Tensor, iters: int = 300) -> float:
    """Fit a logistic regression with LBFGS and return its validation AUC.

    Used for the material-only baseline. Features are standardised with the
    training split's own statistics -- never the validation split's."""
    mu, sd = x_train.mean(0), x_train.std(0) + 1e-6
    a, b = (x_train - mu) / sd, (x_val - mu) / sd
    w = torch.zeros(a.shape[1], device=a.device, requires_grad=True)
    bias = torch.zeros(1, device=a.device, requires_grad=True)
    opt = torch.optim.LBFGS([w, bias], max_iter=iters)
    loss_fn = torch.nn.functional.binary_cross_entropy_with_logits

    def closure():
        opt.zero_grad()
        loss = loss_fn(a @ w + bias, y_train)
        loss.backward()
        return loss

    opt.step(closure)
    with torch.no_grad():
        return roc_auc(y_val, b @ w + bias)


def gate_report(phi_auc: float, material_auc: float) -> tuple[str, bool]:
    """Return a printable gate table and whether everything passed."""
    edge = phi_auc - material_auc
    rows = [
        ("F0  material-only AUC", material_auc, f"< {F0_MAX_MATERIAL_AUC}",
         material_auc < F0_MAX_MATERIAL_AUC),
        ("F1  Phi held-out AUC", phi_auc, f"> {F1_MIN_PHI_AUC}",
         phi_auc > F1_MIN_PHI_AUC),
        ("F2  Phi minus material", edge, f">= {F2_MIN_EDGE}", edge >= F2_MIN_EDGE),
    ]
    width = max(len(r[0]) for r in rows)
    lines = ["", "  " + "GATE".ljust(width) + "   VALUE   THRESHOLD   VERDICT",
             "  " + "-" * (width + 32)]
    for name, value, threshold, ok in rows:
        lines.append(f"  {name.ljust(width)}   {value:6.4f}   {threshold:<9}   "
                     f"{'PASS' if ok else 'FAIL'}")
    lines.append("")
    return "\n".join(lines), all(r[3] for r in rows)
