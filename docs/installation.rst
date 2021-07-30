Installing shutterbug
=====================================================

Prerequisites
-------------
Python version >=3.9 must be available for this installation. It is recommended to install Anaconda on your computer for this purpose. Anaconda installation instructions and links are located here: `Anaconda Installation <https://docs.anaconda.com/anaconda/install/index.html>`_

Installation
-------------

The simplest way to install shutterbug is with an active Conda installation.

First, make a directory where you want to put the project, then move the .whl file you have been provided into it.

Open an Anaconda cmd prompt and navigate to your project directory, then run these commands:


This creates a Python virtual environment specifically for the differential photometry project. The name "diff_eq" is a placeholder, you can choose whichever you like

.. code-block:: console

    $conda create --name diff_eq -y

This activates the Python virtual environment

.. code-block:: console

    $conda activate diff_eq


Conda does not by default install pip, the Python package installer, so installing this is necessary.

.. code-block:: console

    (diff_eq) $conda install pip -y

.. note::
    When typing in the cmd prompt, when you write :command:`.\\` or any other directory name you can tab-complete the entry into the full file name, so there is no need to write it out entirely.

The next command installs the .whl package you've been provided to the local directory. The .xx will be replaced with some version number. The final command will install all dependencies that the software needs. If you do not want to edit the source code simply run the final command and ignore the previous.

.. code-block:: console

    (diff_eq) $pip install --target "." --no-dependencies .\shutterbug-0.1.xx-py3-none-any.whl  -y
    (diff_eq) $pip install .\shutterbug-0.1.xx-py3-none-any.whl -y

At this point the software is ready for use.

.. note::
    The "." simply means 'current directory', so that command will target whatever directory you're in.
    The -y in a few commands is an auto-accept for the installation process, so pip will not ask you to confirm the installation.

Updating
-------------

To update, simply delete the folder that shutterbug exists in, it will be labelled something like "shutterbug-0.2.XX". Then run

.. code-block:: console

    (diff_eq) $pip install --target "." --no-dependencies .\shutterbug-0.1.xx-py3-none-any.whl  -y

to install to a local directory again (Optional)

.. code-block:: console

    (diff_eq) $pip install .\shutterbug-0.1.xx-py3-none-any.whl -y

to update the software for the entire virtual environment