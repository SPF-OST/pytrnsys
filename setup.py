import setuptools
from glob import glob
import os

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "pytrnsys",
    packages=setuptools.find_packages(),
    version="0.2.3",
    author="Dani Carbonell, Mattia Battaglia, Jeremias Schmidli, Martin Neugebauer",
    author_email="martin.neugebauer@spf.ch",
    description="pytrnsys simulation framework",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://pytrnsys.readthedocs.io",
    # project_urls={
    #     "Documentation": "https://pytrnsys.readthedocs.io",
    #     "Source Code": "https://github.com/dcarbonellsanchez/pytrnsys",
    # },
    download_url = "https://github.com/dcarbonellsanchez/pytrnsys/archive/0.2.2.tar.gz",
    include_package_data=True,
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'seaborn'
    ],
    package_data={'pytrnsys_examples': ['./*.*','./**/*.*','./**/**/*.*'],
                  'pytrnsys_ddck': ['./*.*','./**/*.*','./**/**/*.*','./**/**/**/*.*','./**/**/**/**/*.*','./**/**/**/**/**/*.*'],
                  'pytrnsys': ['./plot/stylesheets/*.*','./report/latex_doc/*.*']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
	entry_points="""
    [console_scripts]
    pytrnsys-dll = pytrnsys.utils.copyDllFiles:dllCopy
    pytrnsys-run = pytrnsys.rsim.runParallelTrnsys:run
    pytrnsys-process = pytrnsys.psim.processParallelTrnsys:process
    pytrnsys-load = pytrnsys.utils.loadExamplesAndDdcks:load
    """,
    python_requires='>=3.5'
)