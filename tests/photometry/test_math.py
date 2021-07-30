import numpy as np
import pytest
import shutterbug.photometry.math as math


@pytest.fixture
def data():
    stars = np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]])
    return (stars.transpose(), np.full((4, 1), 5))


def test_diff_mag(data):
    non, var = math.differential_magnitude(*data)
    des_non = np.array(
        [
            [2.0, 2.0, 2.0, 2.0],
            [0.66666667, 0.66666667, 0.66666667, 0.66666667],
            [-0.66666667, -0.66666667, -0.66666667, -0.66666667],
            [-2.0, -2.0, -2.0, -2.0],
        ]
    )
    des_var = np.array([[-2.5, -2.5, -2.5, -2.5]])
    assert np.isclose(non, des_non).all()
    assert np.isclose(var, des_var).all()

