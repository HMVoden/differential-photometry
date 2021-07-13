Installing (Differential Photometry Project Name)
=====================================================

Prerequisites
-------------
Python version >=3.9 must be available for this installation. It is recommended to install Anaconda on your computer for this purpose. Anaconda installation instructions and links are located here: `Anaconda Installation <https://docs.anaconda.com/anaconda/install/index.html>`_

Installation
-------------

The simplest way to install (Differential Photometry Project Name's) is with an active Conda installation.

First, make a directory where you want to put the project, then move the .whl file you have been provided into it.

Open an Anaconda cmd prompt and navigate to your project directory, then run these commands:

.. code-block:: console

    $conda create --name diff_eq -y

This creates a Python virtual environment specifically for the differential photometry project. The name "diff_eq" is a placeholder, you can choose whichever you like

.. code-block:: console

    $conda activate diff_eq

This activates the Python virtual environment

.. code-block:: console

    (diff_eq) $conda install pip -y

Conda does not by default install pip, the Python package installer, so installing this is necessary.

.. note::
    When typing in the cmd prompt, when you write :command:`.\\` or any other directory name you can tab-complete the entry into the full file name, so there is no need to write it out entirely.

.. code-block:: console

    (diff_eq) $pip install --target "." --no-dependencies .\differential_photometry-0.1.xx-py3-none-any.whl  -y

installs the .whl package you've been provided to the local directory. The .xx will be replaced with some version number. Line 5 will install all dependencies that the software needs. If you do not want to edit the source code, simply run line 5.

.. code-block:: console

    (diff_eq) $pip install .\differential_photometry-0.1.xx-py3-none-any.whl -y

At this point the software is ready for use.

.. note::
    The "." in line 4 simply means 'current directory', so that command will target whatever directory you're in.

Updating
-------------

To update, simply delete the folder that (Differential Photometry Project Name) exists in, then run

.. code-block:: console

    (diff_eq) $pip install --target "." --no-dependencies .\differential_photometry-0.1.xx-py3-none-any.whl  -y

to install to a local directory again (Optional)

.. code-block:: console

    (diff_eq) $pip install .\differential_photometry-0.1.xx-py3-none-any.whl -y

to update the software for the entire virtual environment