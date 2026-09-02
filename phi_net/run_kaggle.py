"""One-cell entry point for a Kaggle notebook.

Paste into a single cell (GPU accelerator on):

    !python /kaggle/working/phi_net/run_kaggle.py --data-dir /kaggle/input/<your-dataset>

It runs the ladder in order and stops at the first rung that fails a gate, which
is the point of a ladder. Everything it prints is measured in that session --
there are no numbers baked into this file.
"""

from __future__ import annotations

import argparse
import sys
import time

import torch

from phi_net.train import build_parser, train


def preflight(require_gpu: bool = True) -> None:
    """Fail loudly rather than quietly training on a CPU for eleven hours.

    A Kaggle session bills wall-clock for a GPU-enabled notebook whether or not
    the card is used, so a silent CPU fallback costs quota and returns nothing.
    """
    print("=" * 66)
    print(f"torch {torch.__version__}   cuda available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"  GPU {i}: {props.name}  {props.total_memory / 1e9:.1f} GB  "
                  f"SM {props.major}.{props.minor}")
        if torch.cuda.get_device_properties(0).major < 8:
            print("  note: SM < 8.0 -> no hardware bfloat16. This code uses float16, "
                  "which is correct for T4 (SM 7.5) and P100 (SM 6.0).")
    elif require_gpu:
        sys.exit("ABORT: no CUDA device. Enable the GPU accelerator, or pass "
                 "--allow-cpu if you really mean to run on CPU.")
    print("=" * 66)


def main() -> None:
    p = argparse.ArgumentParser(description="Run the Phi training ladder on Kaggle.")
    p.add_argument("--data-dir", default=None,
                   help="e.g. /kaggle/input/config-steering")
    p.add_argument("--out-dir", default="/kaggle/working/phi_runs")
    p.add_argument("--b1-limit", type=int, default=100_000)
    p.add_argument("--b1-epochs", type=int, default=15)
    p.add_argument("--b2-epochs", type=int, default=40)
    p.add_argument("--batch-size", type=int, default=8192)
    p.add_argument("--allow-cpu", action="store_true")
    p.add_argument("--compile", action="store_true")
    args = p.parse_args()

    preflight(require_gpu=not args.allow_cpu)
    wall0 = time.perf_counter()

    def rung(tag: str, limit, epochs) -> dict:
        print(f"\n{'=' * 66}\n  RUNG {tag.upper()}  "
              f"({'full train split' if limit is None else f'{limit:,} rows'}, "
              f"{epochs} epochs)\n{'=' * 66}")
        rung_args = build_parser().parse_args([])
        rung_args.data_dir = args.data_dir
        rung_args.out_dir = args.out_dir
        rung_args.tag = tag
        rung_args.limit = limit
        rung_args.epochs = epochs
        rung_args.batch_size = args.batch_size
        rung_args.compile = args.compile
        return train(rung_args)

    b1 = rung("b1", args.b1_limit, args.b1_epochs)
    if not b1["gates_passed"]:
        print("\nB1 did not pass its gates. Stopping here deliberately: scaling a "
              "model that has not learned anything only makes it confident.\n"
              "Read PLAN_CONFIGURATION_STEERING.md section 8 before changing "
              "hyper-parameters -- a failed F2 in particular is a DATA result, "
              "not a tuning problem.")
        return

    b2 = rung("b2", None, args.b2_epochs)
    print(f"\n{'=' * 66}")
    print(f"  B1 best val AUC {b1['best']['auc']:.4f} in {b1['total_seconds']:.0f}s")
    print(f"  B2 best val AUC {b2['best']['auc']:.4f} in {b2['total_seconds']:.0f}s")
    print(f"  session wall-clock {time.perf_counter() - wall0:.0f}s")
    print(f"{'=' * 66}")
    print("\nNext: python -m phi_net.evaluate --checkpoint "
          f"{args.out_dir}/phi_b2.pt   (run ONCE, on the test split)")


if __name__ == "__main__":
    main()
