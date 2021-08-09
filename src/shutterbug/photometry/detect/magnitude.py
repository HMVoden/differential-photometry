def find_stars_by_magnitude(
    ds: xr.Dataset, tolerance: float, target: str
) -> npt.NDArray:
    """Locates all stars that are less than (brighter) a target star's median
    magnitude plus a tolerance

        Parameters
        ----------
        ds : xr.Dataset
            Already cleaned dataset
        tolerance : float
            The amount to add to a star's median
        target : str
            Target star's name

        Returns
        -------
        npt.NDArray
            Numpy array of all the star's names that this found

    """
    target_median = ds["mag"].sel(star=target).median("time")
    target_median_plus_tolerance = target_median + tolerance
    all_medians = ds.groupby("star").median("time")
    filtered = all_medians.where(
        all_medians.mag <= target_median_plus_tolerance, drop=True
    )
    filtered_stars = filtered["star"].values
    return filtered_stars
