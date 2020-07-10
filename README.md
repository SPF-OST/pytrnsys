
# pytrnsys : the python TRNSYS Tool-kit 
 
The pytrnsys package provides a complete framework to run and process, plot and report 
TRNSYS simulations. It is designed to give researchers a fast,
fully automatized and easily reproducible way to execute and share TRNSYS simulations by the use of a single short
configuration file. In addition, a large variety of commands is accessible
to post-process simulation results in one shot.

##### Developers: 
- Daniel Carbonell : Institut für Solartechnik SPF, Rapperswil, Switzerland.
- Mattia Battaglia : Institut für Solartechnik SPF, Rapperswil, Switzerland.
- Jeremias Schmidli : Institut für Solartechnik SPF, Rapperswil, Switzerland.

## About

This code was not initially developed with the intention to be shared with others outside our institute SPF,
but after realizing that it could help the community to have a better workflow with TRNSYS, we decided to share it.
In order to know exactly what can you do with this package please check the documentation.
 
## Aknowledgements
 
A first version of this package was first created in 2013 and since then it has evolved considerably. 
We would like to thank the Swiss Federal Office Of Energy (SFOE) 
who supported many projects related to simulations of renewable energy systems where this code has been developed. 
We would also like to thank the European Union’s Horizon 2020 research and innovation programme
for the funding received in TRI-HP under the Grant Agreement No. 81488. 
This project allowed to decicate efforts in sharing the code with the consortium and to make the code usable for the others.  

  
## Installation of python 3.5 and needed libraries

- Install python 3.5 with numpy, scipy, matplotlib, pandas and Tk. 
The pytrnsys package is available for python>3.5 through pip:

```
pip install pytrnsys
```
   
- CoolProp package is nedded if physical properties of fluids need to be used, otherwise it's not mandatory
- We recommend to install anaconda with default installation packages
- Choose the python editor you like, such as PyCharm, Spyder or alike. This readme file is automatically processed by PyCharm in a html visual style   

## Installation of LaTeX for reporting
- For all processing cases, a pdf made with LaTeX will be generated.
Therefore LaTeX is highly recommended. We suggest MiKTeX, but other packages can be used.
- In order to use the LaTeX class for preparing the pdf, the enviromental variables 
  that tell LaTeX where to find local files need to  be specified
- Create an enviromental variable named TEXINPUTS and give a path to it 

```
TEXINPUTS => ....\pytrnsys\pytrnsys\reporting\latex_doc
```
 
## Activate the import of the spfPythonTool package into python environment


- Modify the pytrnsysPath.pth file according to your paths 
- Copy the pytrnsysPath.pth this file to ...\Lib\site-packages. 

For example copy the pytrnsysPath.pth to: 
```
...\Users\....\AppData\Local\Continuum\anaconda2\Lib\site-packages
```



