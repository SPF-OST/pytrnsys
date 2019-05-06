
# TRNSYS TOOL 
 
The TRNSYS tool provides basic functionality written in python to run and process, plot and report TRNSYS simulations.
Nevertheless, many functions can be used to process and plot other kind of data such as those extracted from monitoring systems
or exported from other softwares like Polysun.

##### Main developer: 
- Daniel Carbonell : Institut für Solartechnik SPF, Rapperswil, Switzerland.
- To be able to commit contact : dani.carbonell@spf.ch
##### Collaborators:
- Mattia Battaglia : Institut für Solartechnik SPF, Rapperswil, Switzerland.
- Jeremias Schmidli : Institut für Solartechnik SPF, Rapperswil, Switzerland.

This code was not initially developed with the intention to be shared with others, 
but after realizing that it could help the community to have a better workflow with TRNSYS 
we decided to share it. Currently this code is in testing phase under the European project 
TRI-HP with Grant Agreement No. 81488. 
 
## Aknowledgements
 
A first version of this package was first created in 2013 and since then it has evolved considerably. 
We would like to thank the Swiss Federal Office Of Energy (SFOE) 
who supported many projects related to simulations of renewable energy systems where this code has been developed. We would also like to thank the European Union’s Horizon 2020 research and innovation programme
for the funding received in TRI-HP under the Grant Agreement No.  81488. This project allowed to decicate 
efforts in to share the code with the consortium and to make the code usable for the others.  

  
## Installation of python 2.7 and needed libraries

- Install python 2.7 with numpy, scipy, matplotlib and pandas
- CoolProp package is nedded if physical properties of fluids need to be used, otherwise it's not mandatory
- We recommend to install anaconda with default installation packages
- Choose the python editor you like, such as PyCharm, Spyder or alike. This readme file is automatically processed by PyCharm
in a html visual style   

```
 https://www.anaconda.com/distribution/
```

## Installation of LaTeX for reporting
- For all processing cases, a pdf made with LaTeX will be generated.
Therefore LaTeX is highly recommended. We suggest MiKTeX, but other packages can be used.
- In order to use the LaTeX class for preparing the pdf, the enviromental variables 
  that tell LaTeX where to find local files need to  be specified
- Create an enviromental variable named TEXINPUTS and give a path to it 

```
TEXINPUTS => ....\TrnsysTools\lib\reporting\LaTexDoc
```
 
## Activate the import of the spfPythonTool package into python environment


- Modify the myLocalPath.pth file according to your paths 
- Copy the myLocalPath.pth this file to ...\Lib\site-packages. 

For example copy the spfTrnsysToolLocalPath.pth to: 
```
...\Users\dcarbone\AppData\Local\Continuum\anaconda2\Lib\site-packages
```

## Define enviromental variables (do we need this?)

create avariable named TRNSYS_EXE and define the path of executable, for example

```
TRNSYS_EXE => D:\MyPrograms\Trnsys17\Exe\TRNExe.exe
```
create avariable named LATEX_EXE and define the path of executable, for example

``` 
LATEX_EXE => D:\MyPrograms\MiKTeX\miktex\bin\texify.exe
```


