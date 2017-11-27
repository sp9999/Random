#!/usr/bin/python2
import hexchat
import random
import os
import time

__module_name__ = "wbsp"
__module_version__ = "2.0"
__module_description__ = "WelcomeBack and other shit - SP edition"

wbpath = "config\\addons\\wb\\"

#---------------------------------------------------------------------------------
#
# Description: Gets help message for cmd
# Returns:     Returns string
#
#---------------------------------------------------------------------------------
def help_message(cmd):
    channel = hexchat.get_info("channel")
    if cmd == "!wb":
        hexchat.command("MSG %s Usage: !wb <nick> <line no. or '#''> <search term> - Line from <nick>.txt." %channel)
        hexchat.command("MSG %s Line param: specifies line entry or the latest entry ('#')." %channel)
        hexchat.command("MSG %s String param: Anything after <line param> specifies only lines containing <search term>." %channel)
        hexchat.command("MSG %s Optional: You can omit <nick> to use the master file." %channel)
    elif cmd == "!excuse":
        hexchat.command("MSG %s Usage: !excuse <#1> <#2> <#3> - Generate a random excuse from three files (start, subject, problem)." %channel)
        hexchat.command("MSG %s Line: You can specify every entry no. for the three parts. '#' will use the latest entry." %channel)
        hexchat.command("MSG %s Line: Use 0 for random for any entry. Ex: !excuse 0 0 # for only latest problem entry, the rest random." %channel)
        hexchat.command("MSG %s Add: !add excuse <1/2/3> <string> - Add new line to one of the three excuse files." %channel)
        hexchat.command("MSG %s Rem: !rem excuse <1/2/3> <string/#> - Remove line (either string matching or entry no.) from one of the three excuse files." %channel)
        hexchat.command("MSG %s Each file is a portion of the excuse, <I couldn't X> <subject state-of-being verb> <reason>." %channel)
        

    elif cmd == "!add":
        hexchat.command("MSG %s Usage: !add <nick> <string>" %channel)
        hexchat.command("MSG %s Usage: !add whitelist <nick> - used to give permission for add/rem commands" %channel)
        hexchat.command("MSG %s Usage: !add link <alt-nick> <nick> - allows redirect so that doing !wb <alt-nick> does !wb <nick> instead" %channel)
        hexchat.command("MSG %s Usage: !add excuse <1:start 2:subject 3:problem> <string>" %channel)
    elif cmd == "!rem":
        hexchat.command("MSG %s Usage: !rem <nick> <#/string> - remove entry either by number or text matching from a file" %channel)
        hexchat.command("MSG %s You can also remove from 'whitelist' or 'link' if passed as <nick> " %channel)
        hexchat.command("MSG %s Usage: !rem excuse <1:start 2:subject 3:problem> <#/string>" %channel)

    # elif cmd == "!swap": <-- will always happen when improper parameters, so !swap help will still trigger
    elif cmd == "!SP":
        hexchat.command("MSG %s SP's only purpose in life: !wb, !excuse." %channel)
        hexchat.command("MSG %s Following requires extra permissions: !add, !rem, !swap." %channel)
        hexchat.command("MSG %s !<cmd> help - for more details." %channel)

#---------------------------------------------------------------------------------
#
# Description: Checks if <nick> exists in whitelist.txt
# Returns:     True or False
#
#---------------------------------------------------------------------------------
def whitelist(param_nick):
    channel = hexchat.get_info("channel")
    path = wbpath + channel + "\\"
    file = path + "whitelist.txt"
    name = linkcheck(param_nick)

    # Guarantee file exists
    try:
        fp = open(file)
    except IOError:
        return False
    fp.close()

    with open(file) as fp:
        for line in fp:
            if line.upper()[:-1] == name.upper():
                return True
    return False

#---------------------------------------------------------------------------------
#
# Description:  Check if <altnick> is a different name for a user
# Return:       Either the original <nick> if found, or unmodified <altnick>
# Note:         Database (link.txt) expects entries in the form of <altnick> <nick> per line
#
#---------------------------------------------------------------------------------
def linkcheck(param_altnick):
    channel = hexchat.get_info("channel")
    path = wbpath + channel + "\\"
    file = path + "link.txt"

    # Guarantee file exists
    try:
        fp = open(file)
    except IOError:
        return param_altnick
    fp.close()
    
    with open(file) as fp:
        for line in fp:
            if line.upper().find(param_altnick.upper()) is not -1:
                space = line.find(' ')
                if line.upper()[:space] == param_altnick.upper():
                    name = line[space + 1:-1]
                    return name
    return param_altnick


#---------------------------------------------------------------------------------
#
# Description:  Reads a <file> and returns a line. Can specify which line and search terms
# Return:       Line, (relative if key) line entry, total (key) lines, key line entry, total lines
#
#---------------------------------------------------------------------------------
def read_file_helper(param_file, param_count = None, param_key = None):
    lines = []
    keylines = []
    
    lineIt = 1
    keyIt = []

    # Guarantee file exists
    try:
        fp = open(param_file)
    except IOError:
        return None
    fp.close()

    with open(param_file) as fp:
        for line in fp: 
            if param_key is not None:
                if line.upper().find(param_key.upper()) is not -1:
                    keylines.append(line)
                    keyIt.append(lineIt);
            lines.append(line)
            lineIt += 1;

    totalcount = len(lines)    
    if totalcount is 0:
        if param_key is None:
            return ("No entries found", 0, 0)
        else:
            return ("No entries found", 0, 0, 0, 0)

    if param_key is None:
        if param_count is None:
            param_count = random.randint(0, totalcount)
        elif param_count is '#':            
            param_count = totalcount - 1
        elif param_count.isdigit():
            param_count = int(param_count) - 1
        else:
            return ("Invalid input. Expected digit.", 0, 0)
    else:
        totalcount = len(keylines)
        if totalcount is 0:
            return ("No occurences of '%s' could be found." %(param_key), -1, 0, 0, 0)

        if param_count is '#':
            param_count = random.randint(0, totalcount)
        elif param_count.isdigit():
            param_count = int(param_count) - 1
        else:
            return ("Invalid input. Expected digit.", 0, 0, 0, 0)
    
    if param_count >= totalcount:
        param_count = totalcount - 1;

    finalcount = param_count
    if param_key is not None:
        return (keylines[finalcount][:-1], finalcount + 1, totalcount, keyIt[finalcount], len(lines))

    return (lines[finalcount][:-1], finalcount + 1, totalcount)

##################################################################################
#ADD---------------------------------------------------------------------------ADD
##################################################################################
#---------------------------------------------------------------------------------
#
# Description:  Adds a line from <nick>.txt and wb.txt
# Return:       Success or failure message for adding
#
#---------------------------------------------------------------------------------
def wb_add(param_nick, param_entry, param_doMaster = True):    
    channel = hexchat.get_info("channel")
    path =  wbpath + channel + "\\"
    masterFile = path + "wb.txt"
    filename = path + param_nick + ".txt"    

    with open(filename, "a") as inputFile, open(masterFile, "a") as inputMaster:
        for i in range(3):
            try:
                inputFile.write(param_entry + "\n")
                break
            except OSError:
                print "Error writing to \"%s\"" %filename

        if param_doMaster:
            for i in range(3):
                try:
                    inputMaster.write(param_entry + "\n")
                    break
                except OSError:
                    print "Error writing to \"%s\"" %masterFile

    return "\035\00307Added to %s.txt: |%s|" %(param_nick, param_entry)

#---------------------------------------------------------------------------------
#
# Description:  Help decipher and split up text from the !add trigger
#
#---------------------------------------------------------------------------------
def decipher_add_string(param_string):      # param_string = !add <nick> <entry>
    channel = hexchat.get_info("channel")
    
    splitList = param_string.split(" ", 2)  # splitList = [!add, <nick>, <entry>]
    if len(splitList) < 3 or not splitList[2]:
        if len(splitList) == 2 and splitList[1] and splitList[1] == "help":
            help_message(splitList[0])
        else:
            hexchat.command("MSG %s Usage: !add <nick> <string>" %channel)
        return

    cmd, name, string = splitList

    if name == "whitelist":             # !add whitelist <nick>
        splitList = string.split()       #  splitList = [<nick>, garbage]
        string = splitList[0]           #  string = <nick>
    
    if name == "link":                              # !add link <alt-nick> <nick>
        splitList = string.split(" ", 1)             #  splitList = [<alt-nick>, <nick+garbage>]
        
        if len(splitList) != 2 or not splitList[1]:  #  no second half
            hexchat.command("MSG %s Usage: !add link <alt-nick> <nick>" %channel)

        altNick = splitList[0]              # altNick = <alt-nick>
        splitList = splitList[1].split()    # splitList = [<nick>, garbage]
        nick = splitList[0]                 # nick = <nick>

        string = altNick + " " + nick       # string = <alt-nick> <nick>

    if name == "excuse":                    # !add excuse <1/2/3> <string>
        splitList = string.split(" ", 1)    #  splitList = [<1/2/3>, <string>]
        if splitList[0].isdigit() is False: #  check to make sure is digit
            hexchat.command("MSG %s Usage: !add excuse <1:start 2:subject 3:problem> <string>" %channel)
            return
        excuseIndex = int(splitList[0])

        if len(splitList) != 2 or not splitList[1] or excuseIndex < 1 or excuseIndex > 3:  #  no second half
            hexchat.command("MSG %s Usage: !add excuse <1:start 2:subject 3:problem> <string>" %channel)
        
        excuseFiles = ["estart", "esubject", "eproblem"]
        name = excuseFiles[excuseIndex - 1] # name = <estart/esubject/eproblem>
        string = splitList[1]               # string = <string>

    excludeMasterCommands = ["whitelist", "link", "estart", "esubject", "eproblem"]
    doMaster = name not in excludeMasterCommands

    line = addwb_cmd(name, string, doMaster)      # Call addwb_cmd(<nick>, <string>)            
    hexchat.command("MSG %s %s" %(channel, line))

#---------------------------------------------------------------------------------
#
# Usage #1:     addwb_cmd(<nick>, <string>, boolean write to master file)
# Result:       Adds <string> to <nick>.txt and WB.txt
#
#---------------------------------------------------------------------------------
def addwb_cmd(param_nick, param_entry, param_doMaster = True):
    nick = linkcheck(param_nick)    
    #remove before adding to prevent duplicates
    print removewb_cmd(nick, param_entry, param_doMaster)
    return wb_add(nick, param_entry, param_doMaster)

##################################################################################
#REM---------------------------------------------------------------------------REM
##################################################################################
#---------------------------------------------------------------------------------
#
# Description:  Removes a line from <nick>.txt. Can specify which line and search terms
# Return:       Removed line
#
#---------------------------------------------------------------------------------
def wb_remove(param_nick, param_entry, param_doMaster = True):    
    channel = hexchat.get_info("channel")
    path = wbpath + channel + "\\"
    masterFile = path + "wb.txt"
    fileName = path + param_nick + ".txt"
    tempFile = path + "temp.txt"

    lineToBeRemoved = ""
    removeLastLine = False
    removeLineNo = 0
    lastLine = ""
    masterFileLineToBeRemoved = ""

    if param_entry == '#':
        removeLastLine = True
    elif param_entry.isdigit():
        removeLineNo = int(param_entry)
    else:
        lineToBeRemoved = param_entry

    # Guarantee file exists
    try:
        fp = open(fileName)
    except IOError:
        return None
    fp.close()

    # Copy all lines from <nick>.txt into temp.txt except the line we are removing
    with open(fileName) as inputFile:
        with open(tempFile, "w") as outputFile:
            lineCount = 0
            previousLine = ""        
            skip = False
            for line in inputFile:
                if len(previousLine) > 0:
                    if not removeLastLine and (lineCount == removeLineNo or lineToBeRemoved == previousLine[:-1]):
                        masterFileLineToBeRemoved = previousLine
                        skip = True                    
                        
                if not skip:
                    for i in range(3):
                        try:
                            outputFile.write(previousLine)
                            break
                        except OSError:
                            print "Failure at writing \"%s\" on attempt %s" %(previousLine, i)
                    

                lineCount += 1
                previousLine = line
                skip = False

                if removeLastLine or lineCount == removeLineNo or lineToBeRemoved == previousLine[:-1]:
                    masterFileLineToBeRemoved = line

            if not removeLastLine and lineCount != removeLineNo and lineToBeRemoved != previousLine[:-1]:
                for i in range(3):
                    try:
                        outputFile.write(previousLine)
                        break
                    except OSError:
                        print "Failure at writing \"%s\" on attempt %s" %(previousLine, i)
                

    # Delete <nick>.txt and rename temp.txt into <nick>.txt
    removed = False
    for i in range(3):
        try:
            if not removed:
                os.remove(fileName)
                removed = True
        except OSError:
            print "Error in removing \"%s\"" %fileName
            continue

        try:
            os.rename(tempFile, fileName)
            break
        except OSError:
            print "Error in renaming \"%s\"" %fileName

    if param_doMaster:
        # Copy all lines from wb.txt into temp.txt except the line we are removing
        with open(masterFile) as inputFile:
            with open(tempFile, "w") as outputFile:
                for line in inputFile:
                    if line == masterFileLineToBeRemoved:
                        continue
                    outputFile.write(line)

        # Delete wb.txt and rename temp.txt into wb.txt    
        removed = False
        for i in range(3):
            try:
                if not removed:
                    os.remove(masterFile)
                    removed = True
            except OSError:
                print "Error in removing %s" %masterFile
                continue

            try:
                os.rename(tempFile, masterFile)
                break
            except OSError:
                print "Error in renaming %s" %masterFile

    return masterFileLineToBeRemoved[:-1]

#---------------------------------------------------------------------------------
#
# Description:  Help decipher and split up text from the !rem trigger
#
#---------------------------------------------------------------------------------
def decipher_rem_string(param_string):      # param_string = !rem <nick> <entry>
    channel = hexchat.get_info("channel")
        
    splitList = param_string.split(" ", 2) 
    if len(splitList) != 3 or not splitList[2]:
        if len(splitList) == 2 and splitList[1] and splitList[1] == "help":
            help_message(splitList[0])
        else:
            hexchat.command("MSG %s Usage: !rem <nick> <entry# or string>" %channel)
        return

    cmd, name, string = splitList

    if name == "excuse":                    # !rem excuse <1/2/3> <string>
        splitList = string.split(" ", 1)     #  splitList = [<1/2/3>, <string>]
        excuseIndex = int(splitList[0])

        if len(splitList) != 2 or not splitList[1] or excuseIndex < 1 or excuseIndex > 3:  #  no second half
            hexchat.command("MSG %s Usage: !rem excuse <1:start 2:subject 3:problem> <entry# or string>" %channel)
        
        excuseFiles = ["estart", "esubject", "eproblem"]
        name = excuseFiles[excuseIndex - 1] # name = <estart/esubject/eproblem>
        string = splitList[1]               # string = <string>

    excludeMasterCommands = ["whitelist", "link", "excuse"]
    doMaster = name not in excludeMasterCommands

    line = removewb_cmd(name, string, doMaster)   # Call removewb_cmd(<nick>, <entry>)            
    hexchat.command("MSG %s %s" %(channel, line))

#---------------------------------------------------------------------------------
#
# Usage #1:     removewb_cmd(<nick>, <#>)
# Result:       Removes <#>-th line from <nick>.txt when an op, hop, or 
#                   user in the whitelist uses the function
#
# Usage #2:     removewb_cmd(<nick>, #)
# Result:       Removes last line from <nick>.txt
#
# Usage #3:     removewb_cmd(<nick>, <string>)
# Result:       Removes <string> from <nick>.txt
#
#---------------------------------------------------------------------------------
def removewb_cmd(param_nick, param_entry, param_doMaster = True):
    nick = linkcheck(param_nick)    
    line = wb_remove(nick, param_entry, param_doMaster)

    if line == None:
        return "File %s.txt does not exist" %nick

    if param_entry == '#':
        if len(line) > 0:
            return "\035\00307Removing last entry from %s.txt: |%s| " %(nick, line)    
        else:
            return "\035\00307No entries exist for %s.txt." %nick
    elif param_entry.isdigit():
        if len(line) > 0:
            return "\035\00307Removing line number %d from %s.txt: |%s| " %(int(param_entry), nick, line)
        else:
            return "\035\00307Entry number %d does not exist." %int(param_entry)
    else:
        if line and len(line) > 0:
            return "\035\00307Removing line from %s.txt: |%s|" %(nick, line)
        else:
            return "\035\00307Line does not exist in %s.txt. Already removed!" %(nick)

##################################################################################
#SWAP-------------------------------------------------------------------------SWAP
##################################################################################
#---------------------------------------------------------------------------------
#
# Description:  Reads a <file> and prints out a line. Can specify which line and search terms
# Return:       Formatted line dictating line entry
#
#---------------------------------------------------------------------------------
def wb_swap(param_file, param_line_1, param_line_2):

    if param_line_1 is 0 or param_line_2 is 0 or param_line_1 == param_line_2:
        return None
    line1 = param_line_1 - 1
    line2 = param_line_2 - 1

    lines = []

    channel = hexchat.get_info("channel")
    path = wbpath + channel + "\\"
    fileName = path + param_file + ".txt"
    tempFile = path + "temp.txt"

    # Guarantee file exists
    try:
        fp = open(fileName)
    except IOError:
        return None
    fp.close()

    with open(fileName) as fp:
        for line in fp:             
            lines.append(line)

    totalcount = len(lines)    
    if totalcount is 0:
        return None

    if line1 > totalcount or line2 > totalcount:
        return None

    # Copy all lines from <nick>.txt into temp.txt except the line we are removing
    with open(tempFile, "w") as outputFile:
        for lineCount in range(totalcount):        
            outputLine = lines[lineCount]

            if lineCount == line1:
                outputLine = lines[line2]
            elif lineCount == line2:
                outputLine = lines[line1]

            for i in range(3):
                try:
                    outputFile.write(outputLine)
                    break
                except OSError:
                    print "Failure at swapping \"%s\" on attempt %s" %(outputLine, i)        
                
    # Delete <nick>.txt and rename temp.txt into <nick>.txt
    removed = False
    for i in range(3):
        try:
            if not removed:
                os.remove(fileName)
                removed = True
        except OSError:
            print "Error in removing %s" %fileName
            continue

        try:
            os.rename(tempFile, fileName)
            break
        except OSError:
            print "Error in renaming %s" %fileName

    return lines[line1][:-1]

#---------------------------------------------------------------------------------
#
# Description:  Help decipher and split up text from the !swap trigger
#
#---------------------------------------------------------------------------------
def decipher_swap_string(param_string):      # param_string = !swap <nick> <line1> <line2>
    channel = hexchat.get_info("channel")
    
    splitList = param_string.split() 
    if len(splitList) != 4:
        hexchat.command("MSG %s Usage: !swap <nick> <#1> <#2>" %channel)
        return

    cmd, nick, line1, line2 = splitList

    line = swapwb_cmd(nick, line1, line2)      # Call swapwb_cmd(<nick>, <line1>, <line2)            
    hexchat.command("MSG %s %s" %(channel, line))

#---------------------------------------------------------------------------------
#
# Usage #1:     swapwb_cmd(<nick>, <#1>, <#2>)
# Result:       Swaps <#1>-th line with <#2>-th line from <nick>.txt when an op, hop, or 
#                   user in the whitelist uses the function
#
#---------------------------------------------------------------------------------
def swapwb_cmd(param_nick, param_line_1, param_line_2):
    nick = linkcheck(param_nick)
    line = None

    if param_line_1.isdigit() and param_line_2.isdigit():
        line = wb_swap(nick, int(param_line_1), int(param_line_2))
    else:
        return "Usage: !swap <nick> <#1> <#2>"        

    if line == None:
        line1 = int(param_line_1)
        line2 = int(param_line_2)
        if line1 == 0 or line2 == 0:
            return "Line entries should not be 0"
        elif line1 == line2:
            return "Sounds like a useless operation, fam"
        else:
            return "File %s.txt does not exist" %nick
    
    return "\035\00307New swapped line from %s.txt at position %d: |%s|" %(nick, int(param_line_2), line) 

##################################################################################
#READ-------------------------------------------------------------------------READ
##################################################################################
#---------------------------------------------------------------------------------
#
# Description:  Reads a <file> and prints out a line. Can specify which line and search terms
# Return:       Formatted line dictating line entry
#
#---------------------------------------------------------------------------------
def wb_read(param_file, param_count = None, param_key = None):

    if param_key is None:    
        result = read_file_helper(param_file, param_count)
        if result is not None:
            line = result[0]
            index = result[1]
            count = result[2]
        else:
            return None
    else:
        result = read_file_helper(param_file, param_count, param_key)
        if result is not None:
            line = result[0]
            index = result[1]
            count = result[2]
            keyIndex = result[3]
            keyCount = result[4]
        else:
            return None
    
    # No occurences of 'param_key' could be found
    if (index == -1):
        return line

    if param_key is not None:
        return "[%d/%d][%d/%d] %s" %(index, count, keyIndex, keyCount, line)

    return "[%d/%d] %s" %(index, count, line)

#---------------------------------------------------------------------------------
#
# Description:  Help decipher and split up text from the !wb trigger
#
#---------------------------------------------------------------------------------
def decipher_wb_string(param_string):       # param_string = !wb <nick> <#> <string>
    channel = hexchat.get_info("channel")

    splitList = param_string.split(" ", 1)      # splitList = [!wb, <nick> <#> <string>]
    cmd = splitList[0]
    if len(splitList) != 2 or not splitList[1]: # No other parameters
        line = wb_cmd()                         # Call wb_cmd() without any params
    else:
        splitList = splitList[1].split(" ", 1)              # splitList = [<nick>, <#> <string>]
        if splitList[0] is '#' or splitList[0].isdigit():   # in instance of [<#>, <string>]
            entryno = splitList[0]                          # entryno = <#>
            if len(splitList) != 2 or not splitList[1]:     # Only <#> as param
                line = wb_cmd(None, entryno)                # Call wb_cmd(wb, <#>)
            else:
                line = wb_cmd(None, entryno, splitList[1])  # Call wb_cmd(wb, <#>, <string>)
        else:
            nick = splitList[0]                             # nick = <nick>
            if nick == "help":
                help_message(cmd)                           # Get help message for cmd
                return
            elif len(splitList) != 2 or not splitList[1]:   # Only <nick> as a param
                line = wb_cmd(nick)                         # Call wb_cmd(<nick>)
            else:
                splitList = splitList[1].split(" ", 1)      # splitList = [<#>, <string>]
                entryno = splitList[0]
                if len(splitList) != 2 or not splitList[1]: # Only <nick> and <#>
                    line = wb_cmd(nick, entryno)            # Call wb_cmd(<nick>, <#>)
                else:
                    line = wb_cmd(nick, entryno, splitList[1]) # Call wb_cmd(<nick>, <#>, <string>)

    if line is None:
        line = "Not enough stupid things have been said yet."
    hexchat.command("MSG %s %s" %(channel, line))            

#---------------------------------------------------------------------------------
#
# Usage #1:     wb_cmd()
# Result:       Reads a random line from the comlete database: wb.txt
# Example:      wb_cmd()
# Output:       [5/34] <SP> Hello World!
#
# Usage #2:     wb_cmd(#)
# Result:       Reads the last line from the comlete database: wb.txt
# Example:      wb_cmd(#)
# Output:       [34/34] <Someone> This is my last test
#
# Usage #3:     wb_cmd(#, <string>)
# Result:       Reads a random line containing <string> from the comlete database: wb.txt
# Example:      wb_cmd(#, wbs)
# Output:       [3/7][20/34] <Someone> You have too much fun with WBs
#
# Usage #4:     wb_cmd(<#>)
# Result:       Reads the <#>-th line from the comlete database: wb.txt
# Example:      wb_cmd(7)
# Output:       [7/34] <Someone> What should I say here?
#
# Usage #5:     wb_cmd(<#>, <string>)
# Result:       Reads the <#>-th line containing <string> from the comlete database: wb.txt
# Example:      wb_cmd(5, wbs)
# Output:       [5/7][22/34] <Someone> I'm starting to think you live to add WBs
#
# Usage #6:     wb_cmd(<nick>)
# Result:       Reads a random line from <nick>.txt
# Example:      wb_cmd(SP)
# Output:       [2/6] <SP> Blarghhhhhh
#
# Usage #7:     wb_cmd(<nick>, #)
# Result:       Reads the last line from <nick>.txt
# Example:      wb_cmd(SP, #)
# Output:       [6/6] <SP> Running out of creativity here
#
# Usage #8:     wb_cmd(<nick>, #, <string>)
# Result:       Reads a random line containing <string> from <nick>.txt
# Example:      wb_cmd(SP, #, one occurence)
# Output:       [1/1][1/1] <SP> Notice that total count drops due to one occurence
#
# Usage #9:     wb_cmd(<nick>, <#>)
# Result:       Reads the <#>-th line from <nick>.txt
# Example:      wb_cmd(Someone, 4)
# Output:       [4/5] <Someone> Stop copying everything I say!
#
# Usage #10:    wb_cmd(<nick>, <#>, <string>)
# Result:       Reads the <#>-th line containing <string> from <nick>.txt
# Example:      wb_cmd(SP, 2, so Funny)
# Output:       [2/4][3/6] <SP> Something something so funny
#
#---------------------------------------------------------------------------------
def wb_cmd(param_name = None, param_entryno = None, param_search = None):
    channel = hexchat.get_info("channel")
    path = wbpath + channel + "\\"
    entryno = param_entryno
    search = param_search

    if param_name is None:
        file = path + "wb.txt"
    else:
        name = linkcheck(param_name)
        file = path + name + ".txt"

    if entryno is None:
        return wb_read(file)
    elif search is None:
        return wb_read(file, entryno)
    else:
        return wb_read(file, entryno, search)    


##################################################################################
#EXCUSE---------------------------------------------------------------------EXCUSE
##################################################################################
#---------------------------------------------------------------------------------
#
# Description:  Help decipher and split up text from the !excuse trigger
#
#---------------------------------------------------------------------------------
def decipher_excuse_string(param_string):       # param_string = !excuse <#1> <#2> <#2>
    channel = hexchat.get_info("channel")
    splitList = param_string.split() 
    splitCount = len(splitList)
    excuse = None
    startIndex = None
    subjectIndex = None
    problemIndex = None

    if splitCount >= 2:
        startIndex = splitList[1]               # startIndex = <#1>
        if startIndex == "help":
            help_message(splitList[0])
            return;
    if splitCount >= 3:
        subjectIndex = splitList[2]             # subjectIndex = <#2>
    if splitCount >= 4:
        problemIndex = splitList[3]             # problemIndex = <#3>

    if startIndex is None:
        excuse = excuse_cmd()                                           # excuse_cmd()
    elif subjectIndex is None:
        excuse = excuse_cmd(startIndex)                                 # excuse_cmd(<#1>)
    elif problemIndex is None:
        excuse = excuse_cmd(startIndex, subjectIndex)                   # excuse_cmd(<#1>, <#2>)
    else:
        excuse = excuse_cmd(startIndex, subjectIndex, problemIndex)     # excuse_cmd(<#1>, <#2>, <#3>)

    hexchat.command("MSG %s %s" %(hexchat.get_info("channel"), excuse))     

#---------------------------------------------------------------------------------
#
# Description:  Randomly generate an excuse based off a list of possiblilities
# Return:       An excuse from files estart.txt + esubject.txt + eproblem.txt
#
#---------------------------------------------------------------------------------
def excuse_cmd(startIndex = None, subjectIndex = None, problemIndex = None):
    channel = hexchat.get_info("channel")
    path = wbpath + channel + "\\"
    fileStart = path + "estart.txt" 
    fileSubject = path + "esubject.txt" 
    fileProblem = path + "eproblem.txt" 

    if startIndex == "0":
        startIndex = None
    if subjectIndex == "0":
        subjectIndex = None
    if problemIndex == "0":
        problemIndex = None

    try:
        start, startIndex, startTotal = read_file_helper(fileStart, startIndex) 
        subject, subjectIndex, subjectTotal = read_file_helper(fileSubject, subjectIndex) 
        problem, problemIndex, problemTotal = read_file_helper(fileProblem, problemIndex)
    except ValueError:
        return "Not all files exist"
    except TypeError:
        return "Not all files exist"

    return  "[%d/%d/%d] %s %s %s." %(startIndex, subjectIndex, problemIndex, start, subject, problem);            


##################################################################################
#CALLBACK-----------------------------------------------------------------CALLBACK
#CB-----------------------------------------------------------------------------CB
##################################################################################
#---------------------------------------------------------------------------------
#
# Description:  Manually ask for a welcome back message (for host to use) 
#
#---------------------------------------------------------------------------------
def cmd_wb_cb(word, word_eol, userdata):    
    argc = len(word)
    
    string = ""

    if argc == 1:
        string = wb_cmd()
    elif argc == 2:
        string = wb_cmd(word[1])
    elif argc == 3:
        string = wb_cmd(word[1], word[2])
    else:
        string = wb_cmd(word[1], word[2], word_eol[3])

    if (string is not None):
        hexchat.command("MSG %s %s" %(hexchat.get_info("channel"), string))
    return hexchat.EAT_ALL


#---------------------------------------------------------------------------------
#
# Description:  Manually remove a welcome back message (for host to use) 
#
#---------------------------------------------------------------------------------
def cmd_removewb_cb(word, word_eol, userdata):    
    decipher_rem_string(word_eol[1])
    return hexchat.EAT_ALL

#---------------------------------------------------------------------------------
#
# Description:  Manually add a welcome back message (for host to use) 
#
#---------------------------------------------------------------------------------
def cmd_addwb_cb(word, word_eol, userdata):    
    decipher_add_string(word_eol[1])
    return hexchat.EAT_ALL

#---------------------------------------------------------------------------------
#
# Description:  Manually swap a welcome back message (for host to use) 
#
#---------------------------------------------------------------------------------
def cmd_swapwb_cb(word, word_eol, userdata):    
    if len(word) >= 3:
        print swapwb_cmd(word[1], word[2], word[3])
    
    return hexchat.EAT_ALL

#---------------------------------------------------------------------------------
#
# Description:  Manually generate an excuse (for host to use) 
#
#---------------------------------------------------------------------------------
def cmd_excuse_cb(word, word_eol, userdata):        
    
    argc = len(word)
    
    string = None

    if argc == 1:
        string = excuse_cmd()
    elif argc == 2:
        string = excuse_cmd(word[1])
    elif argc == 3:
        string = excuse_cmd(word[1], word[2])
    else:
        string = excuse_cmd(word[1], word[2], word[3])

    if (string is not None):
        hexchat.command("MSG %s %s" %(hexchat.get_info("channel"), string))
    return hexchat.EAT_ALL

#---------------------------------------------------------------------------------
#
# Description:   Based on possible trigger events call corresponding functions
#
#---------------------------------------------------------------------------------
def msg_triggers_cb(word, word_eol, userdata):

    channel = hexchat.get_info("channel")
    allowedChannels = ["#pcasb", "#prettyanon", "#tsp"]
    if channel not in allowedChannels:
        return hexchat.EAT_NONE

    wb_trigger = "!wb"    
    removewb_trigger = "!rem"
    addwb_trigger = "!add"
    swapwb_trigger = "!swap"
    magicConch_trigger = "magic conch"
    semenDemon_trigger = "semen demon"
    excuse_trigger = "!excuse"
    sp_trigger = "!SP"

    if word[1].upper().find(sp_trigger.upper()) is 0:
        help_message(sp_trigger)

    if word[1].upper().find(wb_trigger.upper()) is 0:
        decipher_wb_string(word[1])
    
    if word[1].upper().find(magicConch_trigger.upper()) is 0:
        hexchat.command("MSG %s %s" %(hexchat.get_info("channel"), wb_cmd()))

    if word[1].upper().find(excuse_trigger.upper()) is 0:
        decipher_excuse_string(word[1])  

    if channel == "#pcasb":
        if word[1].upper().find(semenDemon_trigger.upper()) is not -1:
            hexchat.command("MSG %s %s" %(hexchat.get_info("channel"), wb_cmd("semendemon")))

    channelList = hexchat.get_list("channels")
    prefixList = []
    for i in channelList:
        if i.channel == channel:
            prefixList = i.nickprefixes
            break
    
    # prefixList[:-1] to remove last ranked (+v or +) users
    user = hexchat.strip(word[0], -1, 3)
    if (len(word) > 2 and prefixList.find(word[2]) is not -1) or whitelist(linkcheck(user)):        
        if word[1].upper().find(removewb_trigger.upper()) is 0:
            decipher_rem_string(word[1])

        if word[1].upper().find(addwb_trigger.upper()) is 0:
            decipher_add_string(word[1])

        if word[1].upper().find(swapwb_trigger.upper()) is 0:
            decipher_swap_string(word[1])

    return hexchat.EAT_NONE

#---------------------------------------------------------------------------------
#
# Description:   Static timer function to prevent spam
#
#---------------------------------------------------------------------------------

class JoinTimer:
    allowedChannels = ["#pcasb", "#prettyanon", "#tsp"]
    lastTimes = []

    for index in range(len(allowedChannels)):
        lastTimes.append(0)

    @classmethod
    def CheckTimer(JoinTimer, channel):
        currTime = time.time()
        index = JoinTimer.allowedChannels.index(channel)
        if (JoinTimer.lastTimes[index] + 2 <= currTime ):
            JoinTimer.lastTimes[index] = currTime
            return True
        return False


#---------------------------------------------------------------------------------
#
# Description:   Based on possible trigger events call corresponding functions
#
#---------------------------------------------------------------------------------

def join_triggers_cb(word, word_eol, userdata):    
    nick = word[0]
    channel = word[1]

    if channel in JoinTimer.allowedChannels:
        string = wb_cmd(nick)
        if string is not None:
            if JoinTimer.CheckTimer(channel):
                hexchat.command("MSG %s %s" %(hexchat.get_info("channel"), string))

    return hexchat.EAT_NONE
    
#-------------------------------------------------------------------------------
hexchat.hook_command("wb", cmd_wb_cb)
hexchat.hook_command("removewb", cmd_removewb_cb)
hexchat.hook_command("add", cmd_addwb_cb)
hexchat.hook_command("swap", cmd_swapwb_cb)
hexchat.hook_command("excuse", cmd_excuse_cb)
hexchat.hook_print("Channel Message", msg_triggers_cb)
hexchat.hook_print("Channel Msg Hilight", msg_triggers_cb)
hexchat.hook_print("Join", join_triggers_cb)
