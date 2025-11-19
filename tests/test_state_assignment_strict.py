import warnings
import numpy as np
import c4dynamics as c4d


def main():
    # Capture warnings explicitly
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')

        # Start with integer-initialized state
        s = c4d.state(x=0, y=0)
        assert s.X.dtype.kind in ("i", "u"), "expected integer dtype initially"

        # Assign a float scalar -> _X should be cast to float and value updated
        s.x = 1.9
        assert any('Type mismatch' in str(x.message) for x in w), "expected a dtype mismatch warning"
        assert s.x == 1.9
        assert s.X.dtype.kind == 'f', "expected float dtype after scalar float assignment"

    # Bulk assignment: float array -> dtype becomes float
    s2 = c4d.state(a=0, b=0, c=0)
    with warnings.catch_warnings(record=True) as w2:
        warnings.simplefilter('always')
        s2.X = np.array([1.1, 2.2, 3.3])
        assert s2.X.dtype.kind == 'f'
        assert np.allclose(s2.X, np.array([1.1, 2.2, 3.3]))
        assert any('Type mismatch' in str(x.message) for x in w2), "expected dtype mismatch warning on bulk assign"

    # Now assign integer array to float state -> dtype becomes integer and floats are truncated
    with warnings.catch_warnings(record=True) as w3:
        warnings.simplefilter('always')
        s2.X = np.array([1, 2, 3])
        assert any('Type mismatch' in str(x.message) for x in w3), "expected dtype mismatch warning when assigning ints to float state"
        assert s2.X.dtype.kind in ('i', 'u')
        # check values are integer (no fractional parts)
        assert np.all(np.equal(s2.X, s2.X.astype(int)))

    # length mismatch should raise ValueError
    try:
        s2.X = [1, 2]
        raise SystemExit("Expected ValueError due to length mismatch")
    except ValueError:
        pass

    # Direct single-field assignment from int->float and float->int behavior
    s3 = c4d.state(p=0)
    s3.p = 2.5
    assert s3.p == 2.5
    s3.p = 1
    # after assigning int, dtype may change to int; value should be representable as int
    assert s3.X.dtype.kind in ('i', 'u', 'f')

    print("strict state assignment tests passed")


if __name__ == "__main__":
    main()
