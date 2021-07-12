Installing (Differential Photometry Project Name)
=====================================================

The simplest way to install (Differential Photometry Project Name's) is with an active Conda installation.

First, make a directory where you want to put the project, then move the .whl file you have been provided into it.

Open a cmd prompt and navigate to your project directory, then run these commands:

.. code-block:: console
    :linenos:

    $conda create --name diff_eq
    $activate diff_eq
    (diff_eq) $conda install pip
    (diff_eq) $pip install --target "." --no-dependencies .\differential_photometry-0.1.xx-py3-none-any.whl 
    (diff_eq) $pip install .\differential_photometry-0.1.xx-py3-none-any.whl

The first line creates a virtual environment for the project and the second activates the environment. 
This environment will contain all the necessary dependencies for the project to use. Feel free to change the name "diff_eq"
to anything that you might like.

.. note::
    The "." in line 4 simply means 'current directory', so that command will target whatever directory you're in.


Conda does not by default install pip, the Python package installer, so installing this is necessary.
Line 4 installs the .whl package you've been provided to the local directory. The .xx will be replaced with some version number. Line 5 will install all dependencies that the software needs. If you do not want to edit the source code, simply run line 5.

When writing out line 4 and 5, as soon as you write :command:`.\\`  you can tab-complete the entry into the full file name, so there is no need to write it out entirely.

At this point the software is ready for use.
