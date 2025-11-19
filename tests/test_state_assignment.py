import numpy as np
import c4dynamics as c4d


def main():
    # 1) initial dtype for integer initializers should be integer
    s = c4d.state(x=0, y=0)
    assert s.X.dtype.kind in ("i", "u"), f"expected integer dtype, got {s.X.dtype}"

    # scalar assignment with different dtype should update value and change dtype
    s.x = 1.5
    assert s.x == 1.5
    assert s.X.dtype.kind == "f", f"expected float dtype after assignment, got {s.X.dtype}"

    # 2) bulk assignment: change dtype and values
    s2 = c4d.state(a=0, b=0, c=0)
    s2.X = np.array([1.0, 2.0, 3.0])
    assert np.allclose(s2.X, np.array([1.0, 2.0, 3.0]))
    assert s2.X.dtype.kind == "f"

    # 3) length mismatch must raise ValueError
    try:
        s2.X = [1, 2]
        raise SystemExit("Expected ValueError for length mismatch")
    except ValueError:
        pass

    print("state assignment tests passed")


if __name__ == "__main__":
    main()
