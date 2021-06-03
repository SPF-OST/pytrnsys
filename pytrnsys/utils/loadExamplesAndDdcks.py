# pylint: skip-file
# type: ignore

import pkg_resources
import shutil
import os
import logging

logger = logging.getLogger("root")


def load():
    try:
        template = pkg_resources.resource_filename("pytrnsys_examples", ".")
        shutil.copytree(template, os.path.join(os.getcwd(), "pytrnsys_examples"))
    except:
        logger.warning("not able to copy pytrnsys_examples to this folder")
    try:
        template = pkg_resources.resource_filename("pytrnsys_ddck", ".")
        shutil.copytree(template, os.path.join(os.getcwd(), "pytrnsys_ddck"))
    except:
        logger.warning("not able to copy pytrnsys_ddck to this folder")
    logger.debug(1)


if __name__ == "__main__":
    load()
