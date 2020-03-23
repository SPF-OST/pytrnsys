
#!/usr/bin/python

"""
Clean files produced by TRNSYS simulations and by processing the results to store only
essential data.
Author : Daniel Carbonell
Date   : 21-01-2014
ToDo :
"""


import os,sys
import shutil

class CleanFiles():
    
    def __init__(self,_path):
    
        self.path = _path
        
        self.filesToBeErased = []
        self.foldersToBeErased = []
        self.filesToBeCopied = []
        self.filesToBeIgnored = []

        
       
    def addFoldersToBeErasedByDefault(self):
    
        self.foldersToBeErased.append("Wastewaterprofil")
        self.foldersToBeErased.append("building")

    def addFileToBeErasedByDefault(self,name):
        
        self.filesToBeErased.append("CtrlInputs.Prt")
        self.filesToBeErased.append("HydOut.plt")
        self.filesToBeErased.append("mDotOut.plt")
        self.filesToBeErased.append("SOLSYSTEM_DAY.Prt")
#        self.filesToBeErased.append("SOLSYSTEM_HOUR.Prt")
#        self.filesToBeErased.append("*.lst")
        self.filesToBeErased.append("*.jpg")
        self.filesToBeErased.append("*.png")
        self.filesToBeErased.append("*.aux")
        self.filesToBeErased.append("*.log")
        self.filesToBeErased.append("*.PTI")
        self.filesToBeErased.append("*.gz")
        self.filesToBeErased.append("*.tex")
        

        self.filesToBeErased.append("WWHR.PRT")

        self.filesToBeErased.append("colEnergyMonthly.pdf")
        self.filesToBeErased.append("EnergyYear.pdf")
        self.filesToBeErased.append("IceTESMinMaxMonthly.pdf")
        self.filesToBeErased.append("IceTESMonthly.pdf")
        self.filesToBeErased.append("IceTESYear.pdf")
        self.filesToBeErased.append("PEl.pdf")
        self.filesToBeErased.append("TesEnergyMonthly.pdf")
        self.filesToBeErased.append("energyMonthly.pdf")
        self.filesToBeErased.append("TGroundIni.dat")
        

        self.filesToBeErased.append("*.Qv")
        self.filesToBeErased.append("*.Tg")

        self.filesToBeErased.append("fort.20")
        #Now I need this to calculate building balance
        self.filesToBeErased.append("Energy_zone.BAL")
        self.filesToBeErased.append("fort.90")
        
    def addFileToBeErased(self,name):
        
        self.filesToBeErased.append(name)

    def addFolderToBeErased(self,name):
        
        self.foldersToBeErased.append(name)

    def addFileToBeCopied(self, name):

        self.filesToBeCopied.append(name)

    def addFileToBeIgnored(self,name):

        self.filesToBeIgnored.append(name)

    def ig_f(self, dir, files):
        return [f for f in files if os.path.isfile(os.path.join(dir, f))]

    def ignore_notToBeCopied(self, dir, files):
        ignoreFiles = []
        for f in files:
            print(f)
            if os.path.isfile(os.path.join(dir, f)):
                # if not f in self.filesToBeCopied:
                # return f
                ignore = True
                for ignEnding in self.filesToBeIgnored:
                    if ignEnding in f:
                        ignore = True

                    else:
                        for ending in self.filesToBeCopied:

                            if  ending in f:
                                ignore = False
                                break
                            else:
                                ignore =True
                if ignore:
                    ignoreFiles.append(f)
        return ignoreFiles
            # else:
                # return f




        # return [f for f in files if (os.path.isfile(os.path.join(dir, f)) and ]

    def replicateFolderStructure(self, dst):
        self.folderNames = []
        self.folderNames = [name for name in os.listdir(self.path) if os.path.isdir(self.path + "\\" + name)]

        # if not os.path.isdir(dst):
        #     os.mkdir(dst)

        # for folder in self.folderNames:
        #     os.mkdir(dst + "\\" + folder)

        shutil.copytree(self.path, dst, ignore=self.ig_f)
        print("copytree")
        return self.folderNames

    def copyTree(self,dst):
        shutil.copytree(self.path, dst, ignore=self.ignore_notToBeCopied)

    def removeFolders(self):
        
#       listDir= os.listdir(self.path)        
#       print listDir
       
       sys.stdout.write("###########Erase folder tool########\n")
       sys.stdout.flush()  
       
       for root, dirs, files in os.walk(self.path):
#           print dirs
           for i in dirs:
#               print i
               for erase in self.foldersToBeErased:
#                   print i
                   if(erase==i):
                     removedFolder = os.path.join(root,i)
                     print("removedFolder : %s" % removedFolder)
                     shutil.rmtree(removedFolder)

           
    def removeFiles(self):                             

       sys.stdout.write("###########Erase files tool########\n")
       sys.stdout.flush()  
       
       for root, dirs, files in os.walk(self.path):
           
           # print dirs
           for i in files:    
               # print "file:%s split:%s"%(i,i.split('.')[1])
               for erase in self.filesToBeErased:
                   # print "file:%s erase:%s fileSplit:%s eraseSplit:%s"%(i,erase,i.split('.')[-1],erase.split('.')[1])
                       
                   remove=False                    
                   if(i==erase):                       
                       remove=True
                   elif(erase.split('.')[0]=="*"):
                       try:
                           if(i.split('.')[-1]==erase.split('.')[1] or i.split('.')[1]==erase.split('.')[1]):
                               remove=True
                       except:
                           pass
                           
                   if(remove):
                     removedFile = os.path.join(root,i)
                     print("removedFile : %s" % removedFile)
                     os.remove(removedFile)

    def copyFilesToNewFolder(self,dstFolder=None):
        sys.stdout.write("###########Copy files tool########\n")
        sys.stdout.flush()

        FolderName = self.path.split('\\')[-1]
        if dstFolder == None:
            dstFolder = self.path + '-copy'
            FolderNameNew = FolderName + '-copy'

        for root, dirs, files in os.walk(self.path):

            #           print dirs
            for i in files:
                #               print "file:%s split:%s"%(i,i.split('.')[1])
                for toCopy in self.filesToBeCopied:
                    #                   print "file:%s erase:%s fileSplit:%s eraseSplit:%s"%(i,erase,i.split('.')[-1],erase.split('.')[1])

                    copy = False
                    if (i == copy):
                        copy = True
                    elif (toCopy.split('.')[0] == "*"):
                        try:
                            if (i.split('.')[-1] == toCopy.split('.')[1] or i.split('.')[1] == toCopy.split('.')[1]):
                                copy = True
                        except:
                            pass
                    elif (toCopy.split('-')[-1] == "*"):
                        try:
                            if (i.split('.')[-1] == toCopy.split('.')[1] or i.split('.')[1] == toCopy.split('.')[1]):
                                copy = True
                        except:
                            pass
                    else:
                        if toCopy.split("*")[-1] in i:
                            copy = True

                    if (copy):
                        copiedFile = os.path.join(root, i)
                        # dstPath = self.path + copyFolderExtension + "\\" + root.split("\\")[-1] + "\\" + i
                        if 'FolderNameNew' in locals():
                            dstPath = copiedFile.replace(FolderName,FolderNameNew)
                        else:
                            if root == self.path:
                                dstPath = dstFolder + "\\" + i
                            else:
                                dstPath = dstFolder + "\\" + root.split("\\")[-1] + "\\" + i

                        print("copiedFile : %s" % copiedFile)
                        shutil.copyfile(copiedFile,dstPath)
        pass

    def removeTempFolder(self):
        for root, dirs, files in os.walk(self.path):

            if 'temp' in root:

                for i in files:
                    copiedFile = os.path.join(root, i)
                    dstPath = os.path.join(os.path.split(root)[0], i)

                    shutil.move(copiedFile,dstPath)
                    print("copiedFile : %s" % copiedFile)

                shutil.rmtree(root)



            # for dir in dirs:
            #
            #     if dir == 'temp':
            #         for i in files:
            #
            #
            #             copiedFile = os.path.join(root,dir, i)
            #
            #             dstPath = os.path.join(root,i)
            #
            #
            #
            #         # tempFolder = os.path.join(root,dir)
            #         # os.remove(tempFolder)
            #

    def renameFiles(self, source, end):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file == source:
                    sourcePath = os.path.join(root,file)
                    endPath = os.path.join(root,end)
                    os.rename(sourcePath,endPath)

               
if __name__ == '__main__':


    path="C:\Daten\OngoingProject\Ice-Ex"
    

    clean = CleanFiles(path)
     
    clean.removeFiles()
    clean.removeFolders()
    
    sys.stdout.write("###########END Erase files tool########\n")
    sys.stdout.flush()  