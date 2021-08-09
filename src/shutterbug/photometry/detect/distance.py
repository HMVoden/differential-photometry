def find_nearby_stars(ds: xr.Dataset, tree: KDTree, tolerance: float, target: str):
    """Finds stars that are nearby target star, within radius tolerance, using a
    KDtree


        Parameters
        ----------
        ds : xr.Dataset
            Clean dataset with target star
        tree : KDTree
            KDtree using all stars in dataset's locations
        tolerance : float
            Maximum radius to search within
        target : str
            Name of target star

    """
    target_x = ds.sel(star=target)["x"].values
    target_y = ds.sel(star=target)["y"].values
    target_xy = np.column_stack((target_x, target_y))[0]
    result_indices = tree.query_ball_point(x=target_xy, r=tolerance)
    nearby_stars = ds.isel(star=result_indices, drop=True)["star"].values
    return nearby_stars


def build_kd_tree(x: npt.NDArray[np.float64], y: npt.NDArray[np.float64]) -> KDTree:
    """Makes a KDtree from the x-y coordinates of each star

    Parameters
    ----------
    x : npt.NDArray[np.float64]
        x-coordinates for each star, in order of each star
    y : npt.NDArray[np.float64]
        y-coordinates of each star, in order of each star

    Returns
    -------
    KDTree
        scipy KDTree of all the x-y coordinates all stars

    """
    # build once and only once
    kd_tree = config.get("kd_tree")
    if kd_tree is None:
        xy_coords = np.column_stack((x, y))
        kd_tree = KDTree(xy_coords)
        config.add("kd_tree", kd_tree)
    return kd_tree
