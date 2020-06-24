.. _getting-started:

Welcome to the pytrnsys documentation!
======================================

The pytrnsys package provides a complete framework to run and process, plot and report 
TRNSYS simulations. It is designed to give researchers a fast,
fully automatized and easily reproducible way to execute and share TRNSYS simulations by the use of a single short
configuration file. In addition, a large variety of commands is accessible
to post-process simulation results in one shot.
For more details checkout the :any:`reference <pytrnsys>`.

Getting Started
---------------

Up to now, only TRNSYS17 is fully supported in all the example projects. In order to use pytrnsys, you need the following prerequisites on your machine:

- TRNSYS17 is installed.
- A working LaTeX distribution. We recommend MiKTex due to its included package management system.

Additional optional prerequisites are:

- Automated plotting is done by matplotlib. `GLE <http://glx.sourceforge.net/>`_  is needed to create Q-vs-T plots using the commands :ref:`plotHourlyQvsT <ref-plotHourlyQvsT>` or :ref:`plotTimestepQvsT <ref-plotTimestepQvsT>`
- `GLE <http://glx.sourceforge.net/>`_ is also supported by the configuration file keyword :ref:`setPrintDataForGle <ref-setPrintDataForGle>` which exports a .gle file which can be used for further plotting in GLE.
- `Inkscape <https://inkscape.org/>`_ can be used to save the plots in the enhanced meta file format by using the :ref:`plotEmf keyword <ref-plotEmf>` in the processing.

The pytrnsys package is available for python>3.5 through pip::

	pip install pytrnsys

Along the main pytrnsys-package two additional packages will be installed.
The package pytrnsys-examples contains different example projects that can
be used out of the box to investigate different parametrizations of the represented systems.
Up to now, the example projects contain a solar thermal system for domestic hot water preparation and a pv battery system.

After the installation, you can test the setup by executing one of the example projects.
The default solar domestic hot water system can be run by executing::

	pytrnsys-run
	
in the python environment in which pytrnsys was installed. The command will launch a parametric study of different
solar collector areas that aims to determine the solar fraction of the domestic hot water system. It will
run on multiple cores in parallel using the total amount of cores of your machine minus 4. The simulations will be executed in
a new folder called solar_dhw_simulaions that will be created in the current working directory.

Once the simulations are finished the simulation results can be processed using the following command::

	pytrnsys-process
	
The most important files created by the processing are a results pdf-file in each subfolder
of the parametric runs as well as comparison plots in the main folder.

Load the example projects and the TRNSYS files
----------------------------------------------
.. _trnsys-load:

The core idea of pytrnsys is to use modular parts of a TRNSYS dck file called ddck files.
Due to the modularization this ddck files can be stacked together in order to build a complete
system simulation. The main repository of ddck files is installed together with pytrnsys in a
separate package called pytrnsys_ddck. Pytrnsys has different example projects included that are installed in a separate package called
pytrnsys_examples. You can copy the ddck files as well as the example projects to a local
directory of your machine be executing the following command in the chosen folder::

    pytrnsys-load

This will create two folders pytrnsys_examples and pytrnsys_ddck. In pytrnsys_ddck you find
the whole default ddck repository of pytrnsys. In pytrnsys_examples the example projects are
located. In each example project subfolder, a run configuration file and a process configuration file
as well as some ddcks that are custom to the project can be found.

You can test the new local setup by again executing the solar domestic hot water system. The local set up
is executed by running ``pytrnsys_run`` with a configuration file as the first and single argument::

    pytrnsys-run path_to_your_pytrnsys_examples/solar_dhw/run_solar_dhw.config

Similarily, after the simulation is finished, you can change to the newly created folder solar_dhw
and execute::

    pytrnsys-process path_to_your_pytrnsys_examples/solar_dhw/process_solar_dhw.config

Congratulations! You now have your own pytrnsys installation with a local version of the
example projects and ddck files that you can change as you wish. In the following section,
you will learn about the opportunities pytrnsys offers for customizing the simulations.

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
   

