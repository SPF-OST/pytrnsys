.. pytrnsys documentation master file, created by
   sphinx-quickstart on Tue Oct 22 16:02:17 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pytrnsys
========

The pytrnsys package provides a complete python-based framework to run, process, plot, and report TRNSYS simulations.
It is designed to give researchers a fast, fully automatized, and reproducible way to execute and share TRNSYS
simulations by the use of a single short configuration file. In addition, a large variety of commands is accessible
to post-process simulation results in one shot. This functionality extends beyond processing TRNSYS generated data and
can also be used for generic data.

The package was developed at the `SPF - Institute for Solar Technology <https://www.spf.ch/>`_ at the `OST - Eastern
Switzerland University of Applied Sciences <https://www.ost.ch/>`_.

.. image:: ./guide/resources/logos.svg
      :width: 600
      :alt: logos

Table of contents
=================

.. toctree::
   :maxdepth: 2

   guide/getting_started
   guide/tutorial
   guide/config_file
   guide/run_simulation
   guide/process_data
   guide/example_systems
   guide/ddck_repository
   guide/developers_guide
   Code Reference <modules>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Developers
^^^^^^^^^^

- Daniel Carbonell : SPF Institute for Solar Technology, Rapperswil, Switzerland.
- Mattia Battaglia : SPF Institute for Solar Technology, Rapperswil, Switzerland.
- Jeremias Schmidli : SPF Institute for Solar Technology, Rapperswil, Switzerland.
- Maike Schubert : SPF Institute for Solar Technology, Rapperswil, Switzerland.
- Martin Neugebauer : SPF Institute for Solar Technology, Rapperswil, Switzerland.

Acknowledgments
^^^^^^^^^^^^^^^

A first version of this package was created in 2013 and since then it has evolved considerably.
We would like to thank the Swiss Federal Office Of Energy (SFOE) who supported many projects related to simulations of
renewable energy systems where this code has been developed. We would also like to thank the European Union’s Horizon
2020 research and innovation programme for the funding received in TRI-HP under the Grant Agreement No. 81488. This
project allowed to dedicate efforts in sharing the code with the consortium and to make the code usable for the others.