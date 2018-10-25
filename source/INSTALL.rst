.. _install-ref:

====================================
Installation
====================================


Installation from PIP Package 
---------------------------------

The built package of CAM2 Camera Database API Client is uploaded in Pypi. You can check `Pypi page of the package <https://placeholder>`_ for specific environment requirements.

To install CAM2 Camera Database API Client, simply run the following command to install the latest version:

::

	$ pip install CAM2CameraDatabaseClient


To install a specific version, run command: 

::

	$ pip install CAM2CameraDatabaseClient==<desired_version_number>



Installation from Python Source 
---------------------------------

Source code of CAM2 Camera Database API Client is public on `GitHub <https://github.com/PurdueCAM2Project/CameraDatabaseClient>`_. You can always install the package from source code by either downloading the zip file or clone the repository with command:

::

	$ git clone git@github.com:PurdueCAM2Project/CameraDatabaseClient.git

You can add the downloaded source code in your own python package and use CAM2 Camera Database API Client modules by importing them.

.. warning::
	
	
	We are continuously developing the Python client and updating the code. Downloading or cloning the source code will not guarantee you will a stable software to use.
	
Insallation for Developers
---------------------------------

The CameraDatabaseAPIClient uses `Docker <https://www.docker.com/>`_ which proivdes developers a sandbox enviroemnt using containers to easily create, deploy, and run projects on any operating system. You can follow the steps on the `Docker <https://www.docker.com/install>`_ website to download and install Docker on your machine.

After running Docker, you can build your project by running the Setup bash file which contains all the Docker commands needed to run Docker:

::
	
	$ sh Setup.sh

Docker will now run and download the images needed from the web to run the testing commands
