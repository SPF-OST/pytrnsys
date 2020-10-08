import os

os.system('sphinx-apidoc -f -o . ../pytrnsys')
#os.system('make clean')
#os.system('make html')
os.system('make pdf')
#os.system('sphinx-build -b pdf ../pytrnsys')
