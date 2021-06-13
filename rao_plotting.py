import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pathlib import Path

def plot_and_save_all_4_grid(dataframe: pd.DataFrame, output_filename: str):
    stars = dataframe['name'].unique()
    for star in stars:
        
        plot_frame = dataframe[dataframe['name'] == star]
        file = Path(("./results/" + output_filename + "_" +  star + ".png"))
        if not file.parent.exists():
            file.parent.mkdir()
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))
        plt.suptitle(('Magnitude and differential magntiude of star ' + star))
        plt.rcParams['axes.grid'] = True
        
        plot_frame.plot(x='jd', y='mag', ax=axes[0, 0], color='blue',
                        xlabel='Julian Date', ylabel='Raw Magnitude', label='Line magnitude')
        plot_frame.plot.scatter(x='jd', y='mag', yerr='error', ax=axes[0, 1], color='blue',
                                xlabel='Julian Date', ylabel='Raw Magnitude', label='Scatterplot magnitude')
        plot_frame.plot(x='jd', y='average_diff_mags', ax=axes[1, 0], color='orange',
                                xlabel='Julian Date', ylabel='Average differential magnitude', 
                                label='Line differential magnitude')
        plot_frame.plot.scatter(x='jd', y='average_diff_mags', ax=axes[1, 1], color='orange',
                                xlabel='Julian Date', ylabel='Average differential magnitude', 
                                label='Scatter differential magnitude')

        axes[0, 0].errorbar(x=plot_frame['jd'], y=plot_frame['mag'], yerr=plot_frame['error'],
                    fmt='none', color='black', label='Magnitude Error', capsize=1)
        axes[0, 0].legend()
        axes[0, 0].sharex(axes[0, 1])
        axes[0, 0].sharey(axes[0, 1])
        axes[0, 1].errorbar(x=plot_frame['jd'], y=plot_frame['mag'], yerr=plot_frame['error'],
            fmt='none', color='black', label='Magnitude Error', capsize=1)
        axes[0, 1].legend()
        axes[1, 0].errorbar(x=plot_frame['jd'], y=plot_frame['average_diff_mags'], yerr=plot_frame['average_uncertainties'],
            fmt='none', color='black', label='Average Differential Magnitude Error', capsize=1)
        axes[1, 0].legend()
        axes[1, 0].sharex(axes[1, 1])
        axes[1, 0].sharey(axes[1, 1])
        axes[1, 1].errorbar(x=plot_frame['jd'], y=plot_frame['average_diff_mags'], yerr=plot_frame['average_uncertainties'],
            fmt='none', color='black', label='Average Differential Magnitude Error', capsize=1)
        axes[1, 1].legend()

        fig.tight_layout()
        fig.autofmt_xdate()
        fig.patch.set_facecolor('white')

        fig.savefig(fname=file, transparent=False, bbox_inches='tight')
        plt.close(fig)

