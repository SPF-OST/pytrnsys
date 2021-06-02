# pylint: skip-file
# type: ignore

"""
Author : Dani Carbonell
Date   : 14.12.2012
"""


import logging

logger = logging.getLogger("root")

# skypChar  = ['*','!'] Eliminated the lines with those characters
# To not use it we can say [] or None
# replaceChar = [';','\''] will replace ; and ' by nothing
# To not use it we can say [] or None


def purgueLines(lines, skypChar, replaceChar, skypedLines=0, removeBlankLines=False, removeBlankSpaces=False):

    flines = []
    for n in range(len(lines)):

        skypedLine = False

        if removeBlankLines:
            if not lines[n].strip():
                #            print "Line in strip sequence"
                skypedLine = True

        if removeBlankSpaces:
            # skype empty line
            lines[n] = lines[n].replace(" ", "")

        # The last character is \n and we do not want it. We only do that if the line is not empty
        if len(lines[n]) > 1:
            if lines[n][-1] == "\n":  # only remove the \n if it exists
                line = lines[n][:-1]
            else:
                line = lines[n]
            lineExist = True
        else:
            lineExist = False

        #        else:
        #            print line
        #            raise ValueError("purgueLines from a null line")

        if lineExist:

            if n < skypedLines:
                skypedLine = True

            elif skypChar != None:
                for skyp in skypChar:
                    if line[0] == skyp:
                        skypedLine = True

            if line != "\n" and skypedLine == False:
                fline = "%s\n" % line

                if replaceChar != None:

                    for r in replaceChar:
                        #                    print "replaceChar:%s"%replace
                        # Replacing the replceChar for nothing to convert 2,500.0 for 2500.0 for example
                        fline = fline.replace(r, "")
                flines.append(fline)

    return flines


def purgueComments(lines, commentsChar):

    if commentsChar != None:

        flines = []
        for n in range(len(lines)):
            line = lines[n][:-1]
            iComment = len(line)
            fline = line
            for i in range(len(line)):
                # If the character is a commented character
                for comment in commentsChar:
                    if line[i] == comment:
                        if iComment == len(line):
                            iComment = i
            #                        try:
            #                            #checks if the previous character is a " so that we have "*
            #                            if line[i-1]=='"':
            #                                iComment=i-1
            #                        except:
            #                            pass
            #                        break;
            # We will eliminate from the commented index (character) to the end

            iBlank = iComment

            # from the commented character to the beginning of the line
            for i in range(iComment - 1, 1, -1):
                if line[i] != " " and line[i] != "\t":
                    iBlank = i + 1
                    break

            # the fline if from the beginning to the iBlank index
            fline = "%s\n" % line[:iBlank]

            for i in range(len(fline)):
                # Eliminating the beginning blanks and so on
                # The first time we go in we break to the if fline!='\n' statement
                if fline[i] != " " and fline[i] != "\t":
                    fline = fline[i:]
                    break
            # We use this line of its not a void line
            if fline != "\n":
                # Replacing the , for nothing to convert 2,100.45 => 2100.45
                # flines.append(string.replace(fline,",",""))
                flines.append(fline)

        logger.debug("end of Purgue Lines")

        return flines

    else:
        return lines
