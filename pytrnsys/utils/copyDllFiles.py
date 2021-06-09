# pylint: skip-file
# type: ignore

import os
import pkg_resources
from shutil import copy2


def dllCopy():

    dllDestinationDirectory = "C:\\Trnsys17\\UserLib\\ReleaseDLLs"

    if os.path.exists(dllDestinationDirectory):
        dllSourceDirectory = pkg_resources.resource_filename("pytrnsys_ddck", "dlls")
        dllSourceDirectoryFiles = os.listdir(dllSourceDirectory)

        for dllSourceDirectoryFile in dllSourceDirectoryFiles:
            if os.path.splitext(dllSourceDirectoryFile)[-1] == ".dll":
                dllSourceFile = os.path.join(dllSourceDirectory, dllSourceDirectoryFile)
                dllDestinationFile = os.path.join(dllDestinationDirectory, dllSourceDirectoryFile)
                copy2(dllSourceFile, dllDestinationFile)

        print("Copying of dll-files was successful.")

    else:
        raise ValueError("Cannot copy dll-files: %s does not exist." % dllDestinationDirectory)
