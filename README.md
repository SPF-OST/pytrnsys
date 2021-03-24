
# pytrnsys: The python TRNSYS tool kit
 
The pytrnsys package provides a complete framework to run and process, plot and report 
TRNSYS simulations. It is designed to give researchers a fast,
fully automatized and easily reproducible way to execute and share TRNSYS simulations by the use of a single short
configuration file. In addition, a large variety of commands is accessible
to post-process simulation results in one shot.

## Documentation

The documentation can be found on [pytrnsys.readthedocs.io](https://pytrnsys.readthedocs.io).

## Developer Installation

### Prerequisites

#### Required:

1. [Python 3.9](https://www.python.org/downloads/)
1. A local clone of this GIT repository (`https://github.com/SPF-OST/pytrnsys.git`) into
a folder called `pytrnsys`.

#### Recommended
* [PyCharm Community IDE](https://www.jetbrains.com/pycharm/downloa)

### Getting started

All the following commands should be run from the `pytrnsys` directory. The commands
specified are for a Windows environment. They are very similar for Linux.

1. Create a virtual environment:
    ```commandline
    py -3.9 -m venv venv
    ```
1. Activate it:
    ```commandline
    venv\Scripts\activate
    ```
1. Install the requirements:
    ```commandline
    pip install wheel
    pip install -r requirements\dev\requirements.txt
    ```

And you're ready to go!
    
Beware that `pytrnsys` can only be run from within the virtual environment you created in 
step 1, i.e., whenever you open a new console window from which you want to run it you 
first need to active the environment (step 2. above).


## About

This code was not initially developed with the intention to be shared with others outside our institute SPF,
but after realizing that it could help the community to have a better workflow with TRNSYS, we decided to share it.

#### Developers: 
- Daniel Carbonell : Institut für Solartechnik SPF, Rapperswil, Switzerland.
- Jeremias Schmidli : Institut für Solartechnik SPF, Rapperswil, Switzerland.
- Maike Schubert: Institut für Solartechnik SPF, Rapperswil, Switzerland.
- Martin Neugebauer: Institut für Solartechnik SPF, Rapperswil, Switzerland.
- Mattia Battaglia : Institut für Solartechnik SPF, Rapperswil, Switzerland.

## Acknowledgements
 
A first version of this package was created in 2013 and since then it has evolved considerably. 
We would like to thank the Swiss Federal Office Of Energy (SFOE) 
who supported many projects related to simulations of renewable energy systems where this code has been developed. 
We would also like to thank the European Union’s Horizon 2020 research and innovation programme
for the funding received in TRI-HP under the Grant Agreement No. 81488. 
This project allowed to decicate efforts in sharing the code with the consortium and to make the code usable for the others.  