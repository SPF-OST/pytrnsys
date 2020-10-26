.. _getting-started:

Getting Started
===============

Installation
------------

Up to now, only TRNSYS17 is fully supported in all the example projects. In order to use pytrnsys, you need the
following prerequisites on your machine:

- TRNSYS17 is installed.
- A working LaTeX distribution. We recommend MiKTex due to its included package management system.

TRNSYS17 should be installed under::

    C:/Trnsys17

If the path to your TRNSYS17 installation is different from that you will need to manually copy dll-files (see below)
and adjust the TRNSYS-path in the config-file.

Additional optional prerequisites are:

- Automated plotting is done by matplotlib. `GLE <http://glx.sourceforge.net/>`_  is needed to create Q-vs-T plots using the commands :ref:`plotHourlyQvsT <ref-plotHourlyQvsT>` or :ref:`plotTimestepQvsT <ref-plotTimestepQvsT>`
- `GLE <http://glx.sourceforge.net/>`_ is also supported by the configuration file keyword :ref:`setPrintDataForGle <ref-setPrintDataForGle>` which exports a .gle file which can be used for further plotting in GLE.
- `Inkscape <https://inkscape.org/>`_ can be used to save the plots in the enhanced meta file format by using the :ref:`plotEmf keyword <ref-plotEmf>` in the processing.

The pytrnsys package is available for python>3.5 through pip::

	pip install pytrnsys

Along the main pytrnsys-package two additional packages will be installed. The package pytrnsys_examples contains
different example projects that can be used out of the box to investigate different parametrizations of the represented
systems. Up to now, the example projects contain a solar thermal system for domestic hot water preparation and a pv
battery system. The other package pytrnsys_ddck contains the ddck-repository.

Before you can run the example, you need to copy dll-files to your TRNSYS17-installation. This is done by executing::

    pytrnsys-dll

If the path of your TRNSYS17-installation is different from the one specified above you need to manually copy all
dll-files from::

    ptrnsys_ddck/dlls

to::

    Trnsys17/UserLib/ReleaseDLLs

You can now test the setup by executing one of the example projects.
The default solar domestic hot water system can be run by executing::

	pytrnsys-run
	
in the python environment in which pytrnsys was installed. The command will launch a parametric study of different
solar collector areas that aims to determine the solar fraction of the domestic hot water system. It will
run on multiple cores in parallel using the total amount of cores of your machine minus 4. The simulations will be
executed in a new folder called solar_dhw_simulaions that will be created in the current working directory.

Once the simulations are finished the simulation results can be processed using the following command inside the newly
created simulation folder solar_dhw::

	pytrnsys-process
	
The most important files created by the processing are a results pdf-file in each subfolder
of the parametric runs as well as comparison plots in the main folder.

The philosophy of pytrnsys
--------------------------

Pytrnsys provides a python framework for TRNSYS along with a working methodology. This means that the workflow of using
TRNSYS with pytrnsys is different compared to using a standard methods such as Studio. The main purpose of pytrnsys is
to facilitate the life of the user allowing to use most of the funcionality of the python package without having to
know python in detail. For that we use config files with some scripting funcionality that is described along this
documentation. The proposed methodology works at three different level:

pytrnsys methodology
    - Build a TRNSYS deck
        - The idea is to use a modular approach stacking files with an extension \*.ddck together to form a single dck
          TRNSYS file.
        - The ddck files are structured in a way that can be reused/modified easily to adpat to new cases. These files
          should be uploaded to GIT repositories if sharing/reusing is foreseen.
        - Our core idea to build a TRNSYS deck is to use a flow solver and an hydraulic ddck file which is custom to
          each case. A TRNSYS flow solver is an own-developed TYPE that gives the mass flow of all pipes and elements
          given the mass flows of pumps and positon of 3-way controlled valves for each time step.
        - This hydraulic file also includes all TYPEs for the hydraulic elements such as pipes and tee-pieces. Thus,
          when connecting to all elements such as solar collectors the mass flow and temperature of the pipe that
          enters the collector which has a specific format name can be used directly. That is, connection between
          elements is very easy and can be done in a fully automatic way.
        - At SPF we have a TRNSYS Graphical User Interface (GUI) under development. One of the functionalities of the
          GUI is to export the hydraulic set-up such that can be used directly with the flow solver. For examples the
          hydraulic files you will find in the examples are exported from our GUI. However, the GUI is not publicly
          available at the moment.
        - Although it is theoretically possible to use the TYPE flow solver without a GUI it is very tedious to do so.
          This means that without the GUI the flow solver might not help you.
        - If you are interested in the TRNSYS GUI you can contact danil.carbonell@pf.ch. Currently this GUI is being
          shared with institutes in the framework of research projects. Until we can offer this GUI in a more
          "professional" version, a collaboration within a project might be the easiest way to get access to it. We are
          not a software development company and we don't get the GUI developments paid at all, thus we need to improve
          it and extend it within research projects.
        - If you don't have the GUI you can still work with the pytrnsys without any problem. However, you will need to
          know/connect the inputs (mass flow and temperature) for each component like in normal TRNSYS. Our GUI and
          flow solver makes this almost fully automatic. This is the only limitation of the open source version. All
          the rest can be used 100%.
    - Run a TRNSYS deck
        - Once a TRNSYS deck has been generated with the method described above, by your own method or by Studio you
          can execute this deck with a lot of nice functionalities. For example you can easily run parametric studies
          in parallel and modifiy the deck file using a configuration file.
    - Process a TRNSYS simulation
        - Once the simulations are done you can easily process all results including several results from parametric
          studies using a config file where the main processing calculations can be done.
        - Some automatic processing is always done. For example the energy demand and the energy balance of the system
          is calculated automatically provided a proper syntaxis is used in the TRNSYS deck.
        - The custom-made processing can be easily added. To fully use our processing functionality you need a working
          latex environment.
        - The processing functionality includes monthly and hourly calculations, files with results, and different
          types of automatic plots.
        - Basically all functionality we see is of use in general we add it into the config file. Other more project
          specific processing we do at python level. You will see how to do this at the developer's guide section.
        - Our method of processing TRNSYS simulations is based on our method to build a TRNSYS deck, so to fully use
          all functionalities you will need to change your own deck to have a similar structure as the one we have. For
          example the results are always stored in a temp subfolder and to do the automatic energy balance you need to
          provide the data with specific namings convention. However, still many functionality can be theoretically
          done if you don't follow our method and style, but we never checked this, so you might find issues there.


This package is not intended to substitute your skills in TRNSYS, but if you have them it will make your life easier.
For those that don't know TRNSYS yet it will make the introduction easier, or at least this is our hope.

Load the example projects and the TRNSYS files
----------------------------------------------
.. _trnsys-load:

The core idea of pytrnsys is to use modular parts of a TRNSYS dck file called ddck files.
Due to the modularization these ddck files can be stacked together in order to build a complete
system simulation. The main repository of ddck files is installed together with pytrnsys in a
separate package called pytrnsys_ddck. Pytrnsys has different example projects included that are installed in a
separate package called pytrnsys_examples. You can copy the ddck files as well as the example projects to a local
directory of your machine be executing the following command in the chosen folder::

    pytrnsys-load

This will create two folders pytrnsys_examples and pytrnsys_ddck. In pytrnsys_ddck you find
the whole default ddck repository of pytrnsys. In pytrnsys_examples the example projects are
located. In each example project subfolder, a run configuration file and a process configuration file
as well as some ddcks that are custom to the project can be found.

You can test the new local setup by again executing the solar domestic hot water system. The local set up
is executed by running ``pytrnsys_run`` with a configuration file as the first and single argument::

    pytrnsys-run path_to_your_pytrnsys_examples/solar_dhw/run_solar_dhw.config

Similarly, after the simulation is finished, you can change to the newly created folder solar_dhw
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