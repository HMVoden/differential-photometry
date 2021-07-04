import pandas as pd


def correct_offset(df: pd.DataFrame) -> pd.DataFrame:
    """Finds the offset of an entire timeseries across many days
    by taking the weighted average of every point in timeseries and assuming
    that this is the true mean of the timeseries, then finds the mean of each
    individual day in the timeseries, and brings that to the assumed true mean

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing magnitude and differential magnitude

    Returns
    -------
    pd.DataFrame
        Dataframe where magnitude and differential magnitude have been corrected
    """
    non_varying = df[df["varying"] == False]
    # Probably close to what it 'really' is across all days,
    # more data points will make it closer to real mean.
    true_mean = non_varying.groupby("name").agg({
        "mag": "mean",
        "average_diff_mags": "mean"
    })
    # Individual day means to find offset
    day_star_mean = non_varying.groupby(["d_m_y", "name"]).agg({
        "mag":
        "mean",
        "average_diff_mags":
        "mean"
    })
    offset = day_star_mean.sub(true_mean, axis="index").reset_index()
    # Median of offsets to prevent huge outliers from mucking with data
    per_day_offset = offset.groupby("d_m_y").mean().reset_index()
    # rename so merge doesn't go wonky
    per_day_offset = per_day_offset.rename(
        columns={
            "mag": "mag_offset",
            "average_diff_mags": "diff_mag_offset"
        })
    df_corrected = df.copy()
    df_corrected = df_corrected.merge(per_day_offset,
                                      left_on="d_m_y",
                                      right_on="d_m_y",
                                      how="inner")
    df_corrected["mag"] = df_corrected["mag"] - df_corrected["mag_offset"]
    df_corrected["average_diff_mags"] = df_corrected[
        "average_diff_mags"] - df_corrected["diff_mag_offset"]
    df_corrected["corrected"] = True

    return df_corrected
