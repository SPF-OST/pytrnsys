
# SPF TRNSYS TOOL : Basic functionality to run and process, plot and report TRNSYS simulations

## Installation of python 2.7 and needed libraries

- Install python 2.7 with numpy, scipy, matplotlib and pandas
- CoolProp package is nedded if physical properties of fluids need to be used, otherwise it's not mandatory
- We recommend to install anaconda with default installation packages
- Choose the python editor you like, such as PyCharm, spyder or alike. This readme file is automatically processed by PyCharm
in an html visual sytle   

```
 https://www.anaconda.com/distribution/
```
 
## Activate the import of the spfPythonTool package into python environment


- Modify the myLocalPath.pth file according to your paths 
- Copy the myLocalPath.pth this file to ...\Lib\site-packages. 

For example copy the spfTrnsysToolLocalPath.pth to: 
```
C:\Users\dcarbone\AppData\Local\Continuum\anaconda2\Lib\site-packages
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


