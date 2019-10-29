.. _configFile:

-----------------
Config-File Syntax
-----------------

The idea of the config files is to include general functionality without having to type python code for the user.
Thus, this config file will grow as long as users believe some functionality is used so often that its worth to implemente it within the config file. All the functionality not included in the config file will need to be implemented as python code and thus will be a bit limited to those knowing how to program in python. 

1. Variables
----------------------

There are several types of variables with scape separator:

==========================  =============================================================
*bool*                      with True/False as possible value
*int*                       with any interger as possible value
*string*                    with ``any string'' as possible value
*deck*                      | with any float/int as possible value. If a string is needed 
                            | then the format deck name string anystring should be used.
*STRING\$*                  | ddck file path. STRING\$ needs to 
                            | define one path of the ddck folder.
*variation*                 | used to do parametric variations of 
                            | chaginfg deck variables. For parallel 
                            | simulations
*changeDdckFile*            | used to do changes on the ddck files 
                            | loaded in the config, e.g. weather 
                            | data
*fit*                       to do
*case*                      to do
*fitobs*                    to do
==========================  =============================================================
