import random

import numpy as np
import pytest
import shutterbug.config.manager as config
import shutterbug.photometry.differential as diff


@pytest.fixture()
def clean_tree():
    config.delete("kd_tree")
    yield


@pytest.fixture()
def random_target(clean_data):
    rand_idx = random.randint(0, clean_data["star"].size - 1)
    random_star = clean_data["star"].values.tolist()[rand_idx]
    yield random_star


@pytest.mark.usefixtures("clean_tree")
class TestFindStars:
    @pytest.mark.parametrize("tolerance", [0, 10, 15, 20, 25, 30, 40, 50, 999])
    def test_nearby_stars(self, clean_data, random_target, tolerance):
        target = random_target
        tolerance = 10

        # set up brute force method
        target_x = clean_data.sel(star=target)["x"]
        target_y = clean_data.sel(star=target)["y"]
        d_x = clean_data["x"] - target_x
        d_y = clean_data["y"] - target_y
        dist = np.sqrt(d_x ** 2 + d_y ** 2)
        close_stars = clean_data.where(dist <= tolerance, drop=True)["star"].values
        close_stars = np.sort(close_stars)

        # now efficient method in program
        tree = diff.build_kd_tree(clean_data["x"].values, clean_data["y"].values)
        nearby_stars = diff.find_nearby_stars(clean_data, tree, tolerance, target)
        nearby_stars = np.sort(nearby_stars)
        assert np.equal(close_stars, nearby_stars).all()
        assert nearby_stars[0] == target  # first will always be original star

    def test_build_kd_tree(self, clean_data):
        tree = diff.build_kd_tree(clean_data["x"].values, clean_data["y"].values)
        assert tree.n == clean_data["star"].size
        assert tree.m == 2

    @pytest.mark.parametrize("tolerance", [0, 0.5, 1, 1.5, 2.0, 999])
    def test_stars_by_magnitude(self, clean_data, random_target, tolerance):
        target = random_target

        # set up brute force method
        target_median = np.median(clean_data.sel(star=target)["mag"].values)
        good_mag_stars = np.median(clean_data["mag"].values, axis=0)
        good_star_idx = np.argwhere(
            good_mag_stars <= (target_median + tolerance)
        ).flatten()
        good_stars = clean_data.isel(star=good_star_idx, drop=True)["star"].values

        # actual code
        results = diff.find_stars_by_magnitude(clean_data, tolerance, target)
        results = np.sort(results)
        assert np.equal(good_stars, results).all()

    @pytest.mark.parametrize(
        "distance_tol, max_iter, minimum_stars, tol_increment",
        [(1.0, 50, 1, 0.1), (10, 10, 10, 20), (200, 3, 5, 50)],
    )
    def test_expanding_star_search(
        self,
        clean_data,
        distance_tol,
        max_iter,
        random_target,
        minimum_stars,
        tol_increment,
    ):
        target = random_target
        matches, returned_tol = diff.expanding_star_search(
            ds=clean_data,
            radius=distance_tol,
            mag_tol=1,
            max_iter=max_iter,
            target=target,
            minimum_stars=minimum_stars,
            tol_increment=tol_increment,
        )
        assert matches.size >= minimum_stars
        assert returned_tol >= distance_tol

    def test_expanding_star_error(self, clean_data, random_target):
        target = random_target
        with pytest.raises(RuntimeError):
            diff.expanding_star_search(
                ds=clean_data,
                radius=0,
                mag_tol=0.5,
                max_iter=1,
                target=target,
                minimum_stars=2,
                tol_increment=0,
            )

    def test_expanding_star_logs(self, clean_data, random_target):
        target = random_target
        stars = clean_data.star.values
        res_star, d_tol = diff.expanding_star_search(
            ds=clean_data,
            radius=10,
            mag_tol=0.5,
            max_iter=1,
            target=target,
            minimum_stars=999,
            tol_increment=10,
        )
        assert np.array_equal(res_star, stars)
        assert d_tol == 10
