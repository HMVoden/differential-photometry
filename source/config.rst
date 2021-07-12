Configuration
==============

In the config folder of the project there are 6 .toml files.
Each one of these files contains configuration for a different part of the software. Changing these will change the behaviour of the software.

.. note::
    All .toml files are simply text files that function a specific way, they are editable in any text editor.

.. warning::
    Removing any segment marked in brackets, such as [output.base] will result in the program failing.


In particular to pay attention to is **application.toml**, **output.toml**, **plotting.toml** and **stats.toml** as each of these files determine the most critical portions of application's run.

application.toml
-----------------
You can choose the method that will be used for each iteration of differential photometry but changing the :command:`method` text to any of the statistical function names below it. Currently the GLS Augmented Dickey-Fuller is default as this seems to work the best.

.. warning:: 
    Removing any line in this file will result in program crashing.

output.toml
------------
This determines the output folders for graphs and excel. Under any bracketed heading such as :command:`output.varying` you can add any number of new entries, only the names in quotations will be added as new folders in the chain.

For example, if I add :command:`potato = "seven"` under :command:`output.non_varying` then all non-varying graphs will be output into ::command:`..\\non_varying\\potato`.

.. note::
    Order matters in this file, so if you put the above :command:`potato` entry above the :command:`non_varying` entry the folder **potato** will come first.

.. note::
    The current order of output is :command:`..\\base\\uniform\\corrected\\varying+non_varying+briefly_varying`.
    The .toml file has been organized to reflect this. This is programmed in the code, and changing the order in the file will not change output. Only adding new entries will. 

plotting.toml
--------------
This determines how the graphs will look, the ::command:`seaborn error.fill error.bar` entries all have links to their respective sets of documentation. You can add any of the keyword-value parameters in these documentation sets to their respective bracketed areas and they will change how these specific portions of the graphs will look.

The ::command:`magnitude differential_magnitude` sections are custom for the code and cannot be added to, but can be changed. Adding anything here may cause an error, but may be ignored.


stats.toml
--------------
This contains all the settings for what is passed through to the final statistical analysis functions. Each entry has a documentation link to arch or scipy document on the function. You can add any keyword-value parameters from the linked documentation or edit any of the ones currently in the file.

.. warning::
    This will dramatically change how the star detection system behaves. Experimentation encouraged.

