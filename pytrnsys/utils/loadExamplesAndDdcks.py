import pkg_resources
import shutil
import os

def load():
    try:
        template = pkg_resources.resource_filename('pytrnsys_examples', '.')
        shutil.copytree(template,os.path.join(os.getcwd(),'pytrnsys_examples'))
    except:
        print('not able to copy pytrnsys_examples to this folder')
    try:
        template = pkg_resources.resource_filename('pytrnsys_ddck', '.')
        shutil.copytree(template, os.path.join(os.getcwd(), 'pytrnsys_ddck'))
    except:
        print('not able to copy pytrnsys_ddck to this folder')
    print(1)


if __name__ == '__main__':
    load()