.. _getting-started:

Welcome to the pytrnsys documentation!
======================================

The pytrnsys package provides a complete framework to run and process, plot and report 
TRNSYS simulations. It is designed to give researchers a fast,
fully automatized and easily reproducible way to execute and share TRNSYS simulations by the use of a single short configuration file. In addition, a large variety of commands are accessible
to post-process simulation results in one shot.
For more details checkout the :any:`reference <pytrnsys>`.

Getting Started
---------------

Up to now, only TRNSYS17 is fully supported in all the example projects. In order to use pytrnsys, you need the following prequisites on your machine:

- TRNSYS17 installed. No license is necessary, since the TRNSYS-Studio is not used.
- A working LaTeX distirbution. We recommend MiKTex due to its included package management.

The pytrnsys-package is available for python>3.5 through pip::

	pip install pytrnsys

Along the main pytrnsys-package two additional packages will be installed.
The package pytrnsys-examples contains different example projects, that can 
be used out of the box to investigate different parametrizations of the represented systems.
Up to now the example projects contain a solar thermal system for domestic hot water preparation and a pv system.

After the installation you can test the setup by executing one of the example projects.
The default solar domestic hot water system can be run by executing::

	pytrnsys-run
	
in the python enviromnent in which pytrnsys was installed. The command will launch a parametric study of different
solar collector areas that aims to determine the solar fraction of the domestic hot water system. It will
run on multiple cores in parallel using the total amount of cores of your machine minus 4. For the simulations
a new folder called solar_dhw_simulaions will be created in the current working directory.

Once the simulations are finished the simulation results can be processed using the following command::

	pytrnsys-process
	
The most important files created by the processing are a results pdf-file in each subfolder
of the parametric runs as well as comparison plots in the main folder.


Setting up your simulation
--------------------------

Pytrnsys offers a large number of possibilities that allow the user to customize the system without
having to change the dck files by hand. To learn how to use pytrnsys you can
go through the tutorial:

.. toctree::
    :maxdepth: 3
   tutorial

Or directly read through all the options of the configuration files and play around by yourself.

.. toctree::
    :maxdepth: 3
   config_file

About
-----
This code was not initially developed with the intention to be shared with others,
but after realizing that it could help the community to have a better workflow with TRNSYS
we decided to share it. Currently this code is in testing phase under the European project
TRI-HP with Grant Agreement No. 81488.

Developers
^^^^^^^^^^

- Daniel Carbonell : SPF Institute for Solar Technology, Rapperswil, Switzerland.
- Mattia Battaglia : SPF Institute for Solar Technology, Rapperswil, Switzerland.
- Jeremias Schmidli : SPF Institute for Solar Technology, Rapperswil, Switzerland.
- Maike Schubert : SPF Institute for Solar Technology, Rapperswil, Switzerland.



Aknowledgements
^^^^^^^^^^^^^^^

A first version of this package was first created in 2013 and since then it has evolved considerably.
We would like to thank the Swiss Federal Office Of Energy (SFOE)
who supported many projects related to simulations of renewable energy systems where this code has been developed. We would also like to thank the European Union’s Horizon 2020 research and innovation programme
We also would like to tank the EU Commission for the funding received in TRI-HP under the Grant Agreement No.  81488.
This project allowed to decicate efforts in sharing the code with the consortium and to make the code usable for the others.
   

