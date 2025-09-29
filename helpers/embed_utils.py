import numpy as np
from typing import List

def vec_to_blob(vec: List[float]) -> bytes:
    """Convert a list of floats to a binary blob."""
    return np.array(vec, dtype=np.float32).tobytes()


def blob_to_vec(b: bytes, dim: int) -> np.ndarray:
    v = np.frombuffer(b, dtype="float32")
    assert v.size == dim
    return v