Usage
======

After the project is installed to your system, you are able to run it in your virtual environment via the command in your chosen console.

.. note::

   You must run these commands inside the virtual environment you created during installation, or they will not work.
   You must also be in the root folder that you have installed the application into.

.. code-block:: console

    (diff_eq) $shutterbug [FILES/FOLDER] [OPTIONS]

alternatively, you can run

.. code-block:: console

    (diff_eq) $python -m shutterbug [FILES/FOLDER] [OPTIONS]

which will call the software module directly from Python.

The project can take any number of individual files, but any star removal via the :command:`--remove` flag will be ignored
as stars may change between different datasets (files).

Command line options
---------------------

You can access the options for the application via the command 

.. code-block:: console

    (diff_eq) $shutterbug --help

which will detail the entire command-line interface. For completeness, it is detailed here as well:

.. click:: shutterbug.cli:cli
    :prog: shutterbug
    :nested: full


The smaller options such as -o are simply short forms for faster writing.

.. warning:: 
    The iteration function *--iterations* will run the differential photometry on a single day multiple times. If this results in a massive increase or wild variation in the number of stars found in a single day, there will be substantial errors with calculation and graphing. **You must change the star detection parameters to make them less sensitive.**


Example
---------

As an example, we shall run the command against a data file in the root folder under the folder /data/, e.g. ROOT/data/data.csv

.. code-block:: console

    (diff_eq) $shutterbug .\data\data.csv --output_excel --offset --iterations 4 --remove "M3-test, M3-test2" --mag_y_scale 1 --diff_y_scale 1

Using this command, the data.csv file will be read in, two stars should be removed, all output graphs will have a total 1 mag and 1 differential magnitude y-axis scale, the star finder will run 4 times on the dataset (recalculating differential photometry each time) and the result will be offset corrected.
