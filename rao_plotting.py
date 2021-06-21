from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def plot_and_save_all_4_grid(df: pd.DataFrame, output_filename: str):
    """Takes a pandas dataframe that contains raw magnitude, time as julian date, average magnitude and error, then generates plots for every single star with these values side by side.

    Parameters
    ----------
    dataframe : pd.DataFrame
        A dataframe containing raw magnitude, a time column, average magnitude and errors for magnitudes, with a star's name
    output_filename : str
        the desired filename that will be prepended onto the star's
    """
    stars = df['name'].unique()
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

    top_row = axes[0]
    bottom_row = axes[1]
    top_row_settings = {
        'ylabel': 'Raw Magnitude',
        'xlabel': 'Julian Date',
        'color': 'blue',
        'x': 'jd',
        'y': 'mag'
    }
    bottom_row_settings = {
        'ylabel': 'Average Differential Magnitude',
        'xlabel': 'Julian Date',
        'color': 'orange',
        'x': 'jd',
        'y': 'average_diff_mags'
    }
    error_settings = {
        'x': df['jd'].unique(),
        'fmt': 'none',
        'color': 'black',
        'capsize': 1
    }

    for star in stars:
        plot_frame = df[df['name'] == star]
        file = Path(("./results/" + output_filename + "_" + star + ".png"))
        if not file.parent.exists():
            file.parent.mkdir()

        plt.suptitle(('Magnitude and differential magntiude of star ' + star))
        plot_frame.plot(ax=axes[0, 0],
                        label='Line magnitude', **top_row_settings)
        plot_frame.plot.scatter(
            ax=axes[0, 1], label='Scatterplot magnitude', **top_row_settings)
        plot_frame.plot(ax=axes[1, 0],
                        label='Line differential magnitude', **bottom_row_settings)
        plot_frame.plot.scatter(
            ax=axes[1, 1], label='Scatter differential magnitude', **bottom_row_settings)
        for i, ax in enumerate(top_row):
            ax.errorbar(y=plot_frame['mag'], yerr=plot_frame['error'],
                        label='Magnitude Error', **error_settings)
            ax.sharex(axes[1, i])
        for ax in bottom_row:
            ax.errorbar(y=plot_frame['average_diff_mags'], yerr=plot_frame['average_uncertainties'],
                        label='Average Differential Magnitude Error', **error_settings)
        plt.rcParams['axes.grid'] = True
        fig.tight_layout()
        fig.autofmt_xdate()
        fig.patch.set_facecolor('white')
        for ax in axes.reshape(-1):
            ax.legend()
        fig.savefig(fname=file, transparent=False, bbox_inches='tight')
        for ax in axes.reshape(-1):
            ax.clear()
        plt.close(fig)
