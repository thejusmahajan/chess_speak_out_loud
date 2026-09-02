"""VRAM-resident data loading for Phi.

There is no ``DataLoader`` in this file and that is deliberate. The whole dataset
is 34.7 MB on disk as packed bitboards and ~300 MB unpacked; it fits on any GPU
Kaggle offers with room to spare. A ``DataLoader`` with worker processes would
spend the entire epoch in Python while the GPU idles -- the vectorised unpack of
one split measured **27.45 s on the project laptop's two CPU cores**, and doing
that per epoch is the single easiest way to waste a GPU session.

So: load once, unpack once, keep everything on the device, and index batches with
a permutation tensor.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

# data/training/config_steering/ relative to the repo root
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "training" / "config_steering"

SOURCE_POSITIVE = 0   # s_err  -- the opponent is to move and about to go wrong
SOURCE_N1_SPENT = 1   # the position after a puzzle's full solution line
SOURCE_N2_QUIET = 2   # real quiet play from the user's own games

# Plane indices holding our/their P N B R Q (kings excluded: always exactly one).
_MATERIAL_PLANES = [0, 1, 2, 3, 4, 6, 7, 8, 9, 10]


def _unpack(bb_u64: np.ndarray, device: torch.device, chunk: int = 32_768) -> torch.Tensor:
    """(N, 18) uint64 bitboards -> (N, 18, 8, 8) uint8 planes, on ``device``.

    Done in chunks because the intermediate is int64: unpacking all 209k training
    rows in one shot would allocate 209036 * 18 * 64 * 8 bytes ~= 1.9 GB of
    scratch. Chunking at 32k rows caps that spike at ~300 MB.

    The ``view(np.int64)`` is a bit-level reinterpret, not a conversion. Values
    with bit 63 set become negative, and torch's ``>>`` is then an arithmetic
    shift -- but ``(x >> k) & 1`` still yields bit k correctly for every k in
    0..63, because sign extension only ever fills bits *above* the one we mask.
    """
    n = bb_u64.shape[0]
    bits = torch.arange(64, dtype=torch.int64, device=device)
    out = torch.empty((n, 18, 8, 8), dtype=torch.uint8, device=device)
    for start in range(0, n, chunk):
        stop = min(start + chunk, n)
        block = torch.from_numpy(np.ascontiguousarray(bb_u64[start:stop]).view(np.int64)).to(device)
        planes = ((block.unsqueeze(-1) >> bits) & 1).to(torch.uint8)
        out[start:stop] = planes.view(stop - start, 18, 8, 8)
    return out


class Split:
    """One split of the dataset, fully resident on the target device."""

    def __init__(self, x: torch.Tensor, y: torch.Tensor, motif: torch.Tensor,
                 source: torch.Tensor, name: str):
        self.x = x            # (N, 18, 8, 8) uint8
        self.y = y            # (N,)          float32
        self.motif = motif    # (N, 20)       float32
        self.source = source  # (N,)          uint8
        self.name = name

    def __len__(self) -> int:
        return self.x.shape[0]

    @property
    def device(self) -> torch.device:
        return self.x.device

    def material_counts(self) -> torch.Tensor:
        """(N, 10) piece counts -- the features behind alarm A3 and gate F2."""
        return self.x[:, _MATERIAL_PLANES].sum(dim=(2, 3)).float()

    def describe(self) -> str:
        n = len(self)
        pos = int((self.y == 1).sum())
        by_src = {int(s): int((self.source == s).sum()) for s in torch.unique(self.source)}
        mb = self.x.numel() / 1e6
        return (f"{self.name:5s} {n:>7,} rows | {pos:>7,} pos / {n - pos:>7,} neg "
                f"| sources {by_src} | {mb:.0f} MB resident")


def load_split(name: str, device: torch.device, data_dir: Path | None = None,
               limit: int | None = None, seed: int = 20260901) -> Split:
    """Load one split and move it, unpacked, onto ``device``.

    ``limit`` takes a class-balanced random subset -- this is how the B1 rung of
    the ladder is run without building a second dataset. Subsetting is stratified
    so a small run does not silently change the class balance.
    """
    data_dir = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
    path = data_dir / f"{name}.npz"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Build it first with the config_steering dataset "
            f"builder, or pass --data-dir pointing at the Kaggle input mount."
        )
    with np.load(path) as d:
        bb, y, motif = d["bb"], d["y"], d["motif"]
        source = d["source"] if "source" in d.files else np.zeros(len(y), dtype=np.uint8)

    if limit is not None and limit < len(y):
        rng = np.random.default_rng(seed)
        take = []
        for cls in (0, 1):
            idx = np.where(y == cls)[0]
            take.append(rng.choice(idx, min(limit // 2, len(idx)), replace=False))
        keep = np.sort(np.concatenate(take))
        bb, y, motif, source = bb[keep], y[keep], motif[keep], source[keep]

    return Split(
        x=_unpack(bb, device),
        y=torch.from_numpy(y.astype(np.float32)).to(device),
        motif=torch.from_numpy(motif.astype(np.float32)).to(device),
        source=torch.from_numpy(source.astype(np.uint8)).to(device),
        name=name,
    )


def batches(n: int, batch_size: int, generator: torch.Generator,
            device: torch.device, drop_last: bool = True):
    """Yield index tensors for one shuffled epoch.

    ``drop_last`` defaults to True. A ragged final batch changes the input shape,
    which forces ``torch.compile(mode="reduce-overhead")`` to re-capture its CUDA
    graph every epoch -- costing exactly what the mode was meant to save. With
    ~25 batches an epoch, dropping a few thousand rows from a freshly reshuffled
    permutation costs nothing.
    """
    perm = torch.randperm(n, generator=generator, device=device)
    stop = (n // batch_size) * batch_size if drop_last else n
    for start in range(0, stop, batch_size):
        yield perm[start:start + batch_size]
