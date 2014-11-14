#!/usr/bin/python2

# ################################################################################################ #
# AccuRev utility script                                                                           #
# Author: Lazar Sumar                                                                              #
# Date:   06/11/2014                                                                               #
#                                                                                                  #
# This script is a library that is intended to expose a Python API to the AccuRev commands and     #
# command result data structures.                                                                  #
# ################################################################################################ #

import sys
import subprocess
import xml.etree.ElementTree as ElementTree

# ################################################################################################ #
# Script Globals                                                                                   #
# ################################################################################################ #


# ################################################################################################ #
# Script Classes                                                                                   #
# ################################################################################################ #
def GetXmlContents(xmlElement):
    if xmlElement is not None:
        return xmlElement.text + ''.join(ElementTree.tostring(e) for e in xmlElement)
    return None

class AccuRevWorkspace(object):
    def __init__(self, storage, host, targetTransaction, fileModTime, EOL, type):
        self.storage           = storage
        self.host              = host
        self.targetTransaction = targetTransaction
        self.fileModTime       = fileModTime
        self.EOL               = EOL
        self.type              = type
        
    def __repr__(self):
        str = "AccuRevWorkspace(storage=" + repr(self.storage)
        str += ", host="               + repr(self.host)
        str += ", targetTransaction="  + repr(self.targetTransaction)
        str += ", fileModTime="        + repr(self.fileModTime)
        str += ", EOL="                + repr(self.EOL)
        str += ", type="               + repr(self.type)
        str += ")"
        
        return str
    
    @classmethod
    def fromxmlelement(cls, xmlElement):
        if xmlElement is not None and xmlElement.tag == 'wspace':
            storage                = xmlElement.attrib.get('Storage')
            host                   = xmlElement.attrib.get('Host')
            targetTransaction      = xmlElement.attrib.get('Target_trans')
            fileModTime            = xmlElement.attrib.get('fileModTime')
            EOL                    = xmlElement.attrib.get('EOL')
            type                   = xmlElement.attrib.get('Type')
            
            return cls(storage, host, targetTransaction, fileModTime, EOL, type)
        
        return None
    
class AccuRevStream(object):
    def __init__(self, name, streamNumber, depotName, type, basis=None, basisStreamNumber=None, time=None, prevTime=None, prevBasis=None, prevBasisStreamNumber=None, workspace=None, startTime=None, isDynamic=None, hasDefaultGroup=None):
        self.name                  = name
        self.streamNumber          = streamNumber
        self.depotName             = depotName
        self.type                  = type
        self.basis                 = basis
        self.basisStreamNumber     = basisStreamNumber
        self.time                  = time
        self.prevTime              = prevTime
        self.prevBasis             = prevBasis
        self.prevBasisStreamNumber = prevBasisStreamNumber
        self.workspace             = workspace
        self.startTime             = startTime
        self.isDynamic             = isDynamic
        self.hasDefaultGroup       = hasDefaultGroup
        
    def __repr__(self):
        str = "AccuRevStream(name="       + repr(self.name)
        str += ", streamNumber="          + repr(self.streamNumber)
        str += ", depotName="             + repr(self.depotName)
        str += ", type="                  + repr(self.type)
        str += ", basis="                 + repr(self.basis)
        str += ", basisStreamNumber="     + repr(self.basisStreamNumber)
        str += ", time="                  + repr(self.time)
        str += ", prevTime="              + repr(self.prevTime)
        str += ", prevBasis="             + repr(self.prevBasis)
        str += ", prevBasisStreamNumber=" + repr(self.prevBasisStreamNumber)
        str += ", workspace="             + repr(self.workspace)
        str += ", startTime="             + repr(self.startTime)
        str += ", isDynamic="             + repr(self.isDynamic)
        str += ", hasDefaultGroup="       + repr(self.hasDefaultGroup)
        str += ")"
        
        return str
    
    @classmethod
    def fromxmlelement(cls, xmlElement):
        if xmlElement is not None and xmlElement.tag == 'stream':
            name                      = xmlElement.attrib.get('name')
            streamNumber              = xmlElement.attrib.get('streamNumber')
            depotName                 = xmlElement.attrib.get('depotName')
            type                      = xmlElement.attrib.get('type')
            basis                     = xmlElement.attrib.get('basis')
            basisStreamNumber         = xmlElement.attrib.get('basisStreamNumber')
            time                      = xmlElement.attrib.get('time')
            prevTime                  = xmlElement.attrib.get('prevTime')
            prevBasis                 = xmlElement.attrib.get('prevBasis')
            prevBasisStreamNumber     = xmlElement.attrib.get('prevBasisStreamNumber')
            startTime                 = xmlElement.attrib.get('startTime')
            isDynamic                 = xmlElement.attrib.get('isDynamic')
            hasDefaultGroup           = xmlElement.attrib.get('hasDefaultGroup')
            
            wspaceElement = xmlElement.find('wspace')
            workspace = AccuRevWorkspace.fromxmlelement(wspaceElement)
            
            return cls(name, streamNumber, depotName, type, basis, basisStreamNumber, time, prevTime, prevBasis, prevBasisStreamNumber, workspace, startTime, isDynamic, hasDefaultGroup)
        
        return None
    
class AccuRevMove(object):
    def __init__(self, dest = None, source = None):
        self.dest   = dest
        self.source = source
        
    def __repr__(self):
        str = "AccuRevMove(dest=" + repr(self.dest)
        str += ", source="        + repr(self.source)
        str += ")"
        
        return str
    
    @classmethod
    def fromxmlelement(cls, xmlElement):
        if xmlElement is not None and xmlElement.tag == 'move':
            dest                      = xmlElement.attrib.get('dest')
            source                    = xmlElement.attrib.get('source')
            
            return cls(dest, source)
        
        return None
    
class AccuRevVersion(object):
    def __init__(self, stream=None, version=None):
        self.stream  = stream
        self.version = version
    
    def __repr__(self):
        return '{0}/{1}'.format(self.stream, self.version)
        
    @classmethod
    def fromstring(cls, versionString):
        if versionString is not None:
            versionParts = versionString.split('/')
            if len(versionParts) == 2:
                stream  = versionParts[0]
                version = versionParts[1]
                
                return cls(stream, version)
        
        return None
    
class AccuRevElementVersion(object):
    def __init__(self, path, eid, virtual, real, virtualNamedVersion, realNamedVersion, ancestor=None, ancestorNamedVersion=None, mergedAgainst=None, mergedAgainstNamedVersion=None, elemType=None, dir=None):
        self.path                      = path
        self.eid                       = eid
        self.virtual                   = AccuRevVersion.fromstring(virtual)
        self.real                      = AccuRevVersion.fromstring(real)
        self.virtualNamedVersion       = AccuRevVersion.fromstring(virtualNamedVersion)
        self.realNamedVersion          = AccuRevVersion.fromstring(realNamedVersion)
        self.ancestor                  = AccuRevVersion.fromstring(ancestor)
        self.ancestorNamedVersion      = AccuRevVersion.fromstring(ancestorNamedVersion)
        self.mergedAgainst             = AccuRevVersion.fromstring(mergedAgainst)
        self.mergedAgainstNamedVersion = AccuRevVersion.fromstring(mergedAgainstNamedVersion)
        self.elemType                  = elemType
        self.dir                       = dir
    
    def __repr__(self):
        str = "AccuRevElementVersion(path="    + repr(self.path)
        str += ", eid="                 + repr(self.eid)
        str += ", virtual="             + repr(self.virtual)
        str += ", real="                + repr(self.real)
        str += ", virtualNamedVersion=" + repr(self.virtualNamedVersion)
        str += ", realNamedVersion="    + repr(self.realNamedVersion)
        if self.ancestor is not None or self.ancestorNamedVersion is not None:
            str += ", ancestor="    + repr(self.ancestor)
            str += ", ancestorNamedVersion="    + repr(self.ancestorNamedVersion)
        if self.mergedAgainst is not None or self.mergedAgainstNamedVersion is not None:
            str += ", mergedAgainst="    + repr(self.mergedAgainst)
            str += ", mergedAgainstNamedVersion="    + repr(self.mergedAgainstNamedVersion)
        str += ", elemType="            + repr(self.elemType)
        str += ", dir="                 + repr(self.dir)
        str += ")"
        
        return str
    
    @classmethod
    def fromxmlelement(cls, xmlElement):
        if xmlElement is not None and xmlElement.tag == 'version':
            path                      = xmlElement.attrib.get('path')
            eid                       = xmlElement.attrib.get('eid')
            virtual                   = xmlElement.attrib.get('virtual')
            real                      = xmlElement.attrib.get('real')
            virtualNamedVersion       = xmlElement.attrib.get('virtualNamedVersion')
            realNamedVersion          = xmlElement.attrib.get('realNamedVersion')
            ancestor                  = xmlElement.attrib.get('ancestor')
            ancestorNamedVersion      = xmlElement.attrib.get('ancestorNamedVersion')
            mergedAgainst             = xmlElement.attrib.get('merged_against')
            mergedAgainstNamedVersion = xmlElement.attrib.get('mergedAgainstNamedVersion')
            elemType                  = xmlElement.attrib.get('elem_type')
            dir                       = xmlElement.attrib.get('dir')
            
            return cls(path, eid, virtual, real, virtualNamedVersion, realNamedVersion, ancestor, ancestorNamedVersion, mergedAgainst, mergedAgainstNamedVersion, elemType, dir)
        
        return None
        
class AccuRevTransaction(object):
    def __init__(self, id, type, time, user, comment, versions = [], moves = [], stream = None):
        self.id       = id
        self.type     = type
        self.time     = time
        self.user     = user
        self.comment  = comment
        self.versions = versions
        self.moves    = moves
        self.stream   = stream
        
    def __repr__(self):
        str = "AccuRevTransaction(id=" + repr(self.id)
        str += ", type="               + repr(self.type)
        str += ", time="               + repr(self.time)
        str += ", user="               + repr(self.user)
        str += ", comment="            + repr(self.comment)
        if len(self.versions) > 0:
            str += ", versions="       + repr(self.versions)
        if len(self.moves) > 0:
            str += ", moves="          + repr(self.moves)
        if self.stream is not None:
            str += ", stream="          + repr(self.stream)
        str += ")"
        
        return str
    
    @classmethod
    def fromxmlelement(cls, xmlElement):
        if xmlElement is not None and xmlElement.tag == 'transaction':
            id   = xmlElement.attrib.get('id')
            type = xmlElement.attrib.get('type')
            time = xmlElement.attrib.get('time')
            user = xmlElement.attrib.get('user')
            comment = GetXmlContents(xmlElement.find('comment'))
            
            versions = []
            for versionElement in xmlElement.findall('version'):
                versions.append(AccuRevElementVersion.fromxmlelement(versionElement))
            
            moves = []
            for moveElement in xmlElement.findall('move'):
                moves.append(AccuRevMove.fromxmlelement(moveElement))
            
            streamElement = xmlElement.find('stream')
            stream = AccuRevStream.fromxmlelement(streamElement)
            
            return cls(id, type, time, user, comment, versions, moves, stream)
        
        return None
    
class AccuRevHistory(object):
    def __init__(self, taskId = None, transactions = [], streams = []):
        self.taskId       = taskId
        self.transactions = transactions
        self.streams      = streams
    
    def __repr__(self):
        str = "AccuRevTransaction(taskId=" + repr(self.taskId)
        str += ", transactions="           + repr(self.transactions)
        str += ", streams="                + repr(self.streams)
        str += ")"
        
        return str
        
    @classmethod
    def fromxmlstring(cls, xmlText):
        # Load the XML
        xmlRoot = ElementTree.fromstring(xmlText)
        #xpathPredicate = ".//AcResponse[@Command='hist']"
        
        if xmlRoot is not None and xmlRoot.tag == "AcResponse" and xmlRoot.get("Command") == "hist":
            # Build the class
            taskId = xmlRoot.attrib.get('TaskId')
            
            transactions = []
            for transactionElement in xmlRoot.findall('transaction'):
                transactions.append(AccuRevTransaction.fromxmlelement(transactionElement))
            
            streams = []
            streamsElement = xmlRoot.find('streams')
            if streamsElement is not None:
                for streamElement in streamsElement:
                    streams.append(AccuRevStream.fromxmlelement(streamElement))
            
            
            return cls(taskId=taskId, transactions=transactions, streams=streams)
        else:
            # Invalid XML for an AccuRev hist command response.
            return None

class AccuRevUser(object):
    def __init__(self, number = None, name = None, kind = None):
        self.number = number
        self.name   = name
        self.kind   = kind
        
    def __repr__(self):
        str = "AccuRevUser(number=" + repr(self.number)
        str += ", name="            + repr(self.name)
        str += ", kind="            + repr(self.kind)
        str += ")"
        
        return str
    
    @classmethod
    def fromxmlelement(cls, xmlElement):
        if xmlElement is not None and xmlElement.tag == 'Element':
            number = xmlElement.attrib.get('Number')
            name   = xmlElement.attrib.get('Name')
            kind   = xmlElement.attrib.get('Kind')
            
            return cls(number, name, kind)
        
        return None
            
class AccuRevShowUsers(object):
    def __init__(self, taskId = None, users = []):
        self.taskId = taskId
        self.users  = users
    
    def __repr__(self):
        str = "AccuRevShowUsers(taskId=" + repr(self.taskId)
        str += ", users="                  + repr(self.users)
        str += ")"
        
        return str
        
    @classmethod
    def fromxmlstring(cls, xmlText):
        # Load the XML
        xmlRoot = ElementTree.fromstring(xmlText)
        #xpathPredicate = ".//AcResponse[@Command='hist']"
        
        if xmlRoot is not None and xmlRoot.tag == "AcResponse" and xmlRoot.get("Command") == "show users":
            # Build the class
            taskId = xmlRoot.attrib.get('TaskId')
            
            users = []
            for userElement in xmlRoot.findall('Element'):
                users.append(AccuRevUser.fromxmlelement(userElement))
            
            return cls(taskId=taskId, users=users)
        else:
            # Invalid XML for an AccuRev hist command response.
            return None
            
class AccuRevDepot(object):
    def __init__(self, number=None, name=None, slice=None, exclusiveLocking=None, case=None, locWidth=None, replStatus=None):
        self.number           = number
        self.name             = name
        self.slice            = slice
        self.exclusiveLocking = exclusiveLocking
        self.case             = case
        self.locWidth         = locWidth
        self.replStatus       = replStatus
        
    def __repr__(self):
        str = "AccuRevDepot(number="  + repr(self.number)
        str += ", name="              + repr(self.name)
        str += ", slice="             + repr(self.slice)
        str += ", exclusiveLocking="  + repr(self.exclusiveLocking)
        str += ", case="              + repr(self.case)
        str += ", locWidth="          + repr(self.locWidth)
        str += ", replStatus="        + repr(self.replStatus)
        str += ")"
        
        return str
    
    @classmethod
    def fromxmlelement(cls, xmlElement):
        if xmlElement is not None and xmlElement.tag == 'Element':
            number           = xmlElement.attrib.get('Number')
            name             = xmlElement.attrib.get('Name')
            slice            = xmlElement.attrib.get('Slice')
            exclusiveLocking = xmlElement.attrib.get('exclusiveLocking')
            case             = xmlElement.attrib.get('case')
            locWidth         = xmlElement.attrib.get('locWidth')
            replStatus       = xmlElement.attrib.get('ReplStatus')
            
            return cls(number, name, slice, exclusiveLocking, case, locWidth, replStatus)
        
        return None
            
class AccuRevShowDepots(object):
    def __init__(self, taskId = None, depots = []):
        self.taskId = taskId
        self.depots = depots
    
    def __repr__(self):
        str = "AccuRevShowDepots(taskId=" + repr(self.taskId)
        str += ", depots="                + repr(self.depots)
        str += ")"
        
        return str
        
    @classmethod
    def fromxmlstring(cls, xmlText):
        # Load the XML
        xmlRoot = ElementTree.fromstring(xmlText)
        #xpathPredicate = ".//AcResponse[@Command='hist']"
        
        if xmlRoot is not None and xmlRoot.tag == "AcResponse" and xmlRoot.get("Command") == "show depots":
            # Build the class
            taskId = xmlRoot.attrib.get('TaskId')
            
            depots = []
            for depotElement in xmlRoot.findall('Element'):
                depots.append(AccuRevDepot.fromxmlelement(depotElement))
            
            return cls(taskId=taskId, depots=depots)
        else:
            # Invalid XML for an AccuRev hist command response.
            return None
            
class AccuRevShowStreams(object):
    def __init__(self, taskId = None, streams = []):
        self.taskId = taskId
        self.streams = streams
    
    def __repr__(self):
        str = "AccuRevShowStreams(taskId=" + repr(self.taskId)
        str += ", streams="                + repr(self.streams)
        str += ")"
        
        return str
        
    @classmethod
    def fromxmlstring(cls, xmlText):
        # Load the XML
        xmlRoot = ElementTree.fromstring(xmlText)
        #xpathPredicate = ".//AcResponse[@Command='hist']"
        
        if xmlRoot is not None and xmlRoot.tag == "AcResponse" and xmlRoot.get("Command") == "show streams":
            # Build the class
            taskId = xmlRoot.attrib.get('TaskId')
            
            streams = []
            for streamElement in xmlRoot.findall('stream'):
                streams.append(AccuRevStream.fromxmlelement(streamElement))
            
            return cls(taskId=taskId, streams=streams)
        else:
            # Invalid XML for an AccuRev hist command response.
            return None

# The raw class namespaces raw accurev commands that return text output directly from the terminal.
class raw(object):
    # The __lastCommand is used to access the return code that the last command had generated in most
    # cases.
    _lastCommand = None
    
    @staticmethod
    def _RunCommand(cmd, outputFilename=None):
        accurevCommand = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        
        outputFile = None
        if outputFilename is not None:
            outputFile = open(outputFilename, "w")
        
        xmlOutput = ''
        accurevCommand.poll()
        while accurevCommand.returncode is None:
            stdoutdata, stderrdata = accurevCommand.communicate()
            if outputFile is None:
                xmlOutput += stdoutdata
            else:
                outputFile.write(stdoutdata)
            accurevCommand.poll()
        
        raw._lastCommand = accurevCommand
        
        if outputFile is None:
            return xmlOutput
        else:
            return 'Written to ' + outputFilename

    @staticmethod
    def GetAcSync():
        # http://www.accurev.com/download/ac_current_release/AccuRev_WebHelp/AccuRev_Admin/wwhelp/wwhimpl/common/html/wwhelp.htm#href=timewarp.html&single=true
        # The AC_SYNC environment variable controls whether your machine clock being out of sync with
        # the AccuRev server time generates an error or not. Allowed states:
        #   * Not set or set to ERROR   ->   an error occurs and a message appears.
        #   * Set to WARN               ->   a warning is displayed but the command executes.
        #   * Set to IGNORE             ->   no error/warning, command executes.
        return os.environ.get('AC_SYNC')
        
    @staticmethod
    def SetAcSync(value):
        os.environ['AC_SYNC'] = value

    @staticmethod
    def Login(username = None, password = None):
        if username is not None and password is not None:
            accurevCommand = subprocess.Popen([ "accurev", "login" ], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            accurevCommand.communicate(username + '\n' + password + '\n')
            accurevCommand.wait()
            
            return (accurevCommand.returncode == 0)
        
        return False
        
    @staticmethod
    def Logout():
        accurevCommand = subprocess.Popen([ "accurev", "logout" ])
        accurevCommand.wait()
        
        return (accurevCommand.returncode == 0)

    @staticmethod
    def History(depot=None, stream=None, timeSpec=None, listFile=None, isListFileXml=False, elementList=None, allElementsFlag=False, elementId=None, transactionKind=None, commentString=None, username=None, isXmlOutput=False, outputFilename=None):
        cmd = [ "accurev", "hist" ]
        
        # Interpret options
        if depot is not None:
            cmd.extend([ "-p", depot ])
        if stream is not None:
            cmd.extend([ "-s", stream ])
        if timeSpec is not None:
            cmd.extend([ "-t", timeSpec ])
        if listFile is not None:
            if isListFileXml:
                cmd.append("-Fx")
            cmd.extend([ "-l", listFile ])
        if elementList is not None:
            cmd.extend(elementList)
        if allElementsFlag:
            cmd.append("-a")
        if elementId is not None:
            cmd.extend([ "-e", elementId ])
        if transactionKind is not None:
            cmd.extend([ "-k", transactionKind ])
        if commentString is not None:
            cmd.extend([ "-c", commentString ])
        if username is not None:
            cmd.extend([ "-u", username ])
        if isXmlOutput:
            cmd.append("-fx")
        
        return raw._RunCommand(cmd, outputFilename)

    @staticmethod
    def Populate(isRecursive=False, isOverride=False, verSpec=None, location=None, dontBuildDirTree=False, timeSpec=None, isXmlOutput=False, listFile=None, elementList=None):
        cmd = [ "accurev", "pop" ]
        
        if isOverride:
            cmd.append("-O")
        if isRecursive:
            cmd.append("-R")
        
        if location is not None and verSpec is not None:
            cmd.extend(["-v", verSpec, "-L", location])
            if dontBuildDirTree:
                cmd.append("-D")
        elif location is not None or verSpec is not None:
            raise Exception("""AccuRev populate command must have either both the <ver-spec> and <location>
    supplied or neither. We can infer the <ver-spec> but <location>
    must be specified if it is provided""")
        
        if timeSpec is not None:
            cmd.extend(["-t", timeSpec])
        
        if isXmlOutput:
            cmd.append("-fx")
        
        if listFile is not None:
            cmd.extend(["-l", listFile])
        elif elementList is not None:
            cmd.append(elementList)
        
        return raw._RunCommand(cmd)

    class Show(object):
        @staticmethod
        def _GetShowBaseCommand(isXmlOutput=False, includeDeactivatedItems=False, includeOldDefinitions=False, addKindColumnForUsers=False, includeHasDefaultGroupAttribute=False):
            # See: http://www.accurev.com/download/ac_current_release/AccuRev_WebHelp/wwhelp/wwhimpl/js/html/wwhelp.htm#href=AccuRev_User_CLI/cli_ref_show.html
            # for usage.
            cmd = [ "accurev", "show" ]
            
            flags = ''
            
            if includeDeactivatedItems and includeOldDefinitions:
                flags += 'I'
            elif includeDeactivatedItems:
                flags += 'i'
            
            if addKindColumnForUsers:
                flags += 'v'
            
            if includeHasDefaultGroupAttribute:
                # This option forces the XML output.
                flags += 'xg'
            elif isXmlOutput:
                flags += 'x'
            
            if len(flags) > 0:
                flags = '-f' + flags
                cmd.append('-f{0}'.format(flags))
            
            return cmd
    
        @staticmethod
        def _RunSimpleShowSubcommand(subcommand, isXmlOutput=False, includeDeactivatedItems=False):
            if subcommand is not None:
                cmd = raw.Show._GetShowBaseCommand(isXmlOutput=isXmlOutput, includeDeactivatedItems=includeDeactivatedItems)
                cmd.append(subcommand)
                return raw._RunCommand(cmd)
                
            return None
    
        @staticmethod
        def Users(isXmlOutput=False, includeDeactivatedItems=False, addKindColumnForUsers=False):
            return raw.Show._RunSimpleShowSubcommand(subcommand="users", isXmlOutput=isXmlOutput, includeDeactivatedItems=includeDeactivatedItems, addKindColumnForUsers=addKindColumnForUsers)
        
        @staticmethod
        def Depots(isXmlOutput=False, includeDeactivatedItems=False):
            return raw.Show._RunSimpleShowSubcommand(subcommand="depots", isXmlOutput=isXmlOutput, includeDeactivatedItems=includeDeactivatedItems)
        
        @staticmethod
        def Streams(depot=None, timeSpec=None, stream=None, matchType=None, listFile=None, listPathAndChildren=False, listChildren=False, listImmediateChildren=False, nonEmptyDefaultGroupsOnly=False, isXmlOutput=False, includeDeactivatedItems=False, includeOldDefinitions=False, includeHasDefaultGroupAttribute=False):
            cmd = raw.Show._GetShowBaseCommand(isXmlOutput=isXmlOutput, includeDeactivatedItems=includeDeactivatedItems, includeOldDefinitions=includeOldDefinitions, includeHasDefaultGroupAttribute=includeHasDefaultGroupAttribute)
            
            if depot is not None:
                cmd.extend([ "-p", depot ])
            if timeSpec is not None:
                cmd.extend([ "-t", timeSpec ])
            if stream is not None:
                cmd.extend([ "-s", stream ])
            if matchType is not None:
                cmd.extend([ "-m", matchType ])
            if listFile is not None:
                cmd.extend([ "-l", listFile ])
            
            if listPathAndChildren:
                cmd.append("-r")
            elif listChildren:
                cmd.append("-R")
            elif listImmediateChildren:
                cmd.append("-1")
                
            cmd.append("streams")
            
            return raw._RunCommand(cmd)
    
# ################################################################################################ #
# Script Functions                                                                                 #
# ################################################################################################ #
def GetAcSync():
    return raw.GetAcSync()
        
def SetAcSync(value):
    raw.SetAcSync(value)

def Login(username = None, password = None):
    return raw.Login(username, password)
    
def Logout():
    return raw.Logout()

def History(depot=None, stream=None, timeSpec=None, listFile=None, isListFileXml=False, elementList=None, allElementsFlag=False, elementId=None, transactionKind=None, commentString=None, username=None, outputFilename=None):
    xmlOutput = raw.History(depot=depot, stream=stream, timeSpec=timeSpec, listFile=listFile, isListFileXml=isListFileXml, elementList=elementList, allElementsFlag=allElementsFlag, elementId=elementId, transactionKind=transactionKind, commentString=commentString, username=username, isXmlOutput=True, outputFilename=outputFilename)
    return AccuRevHistory.fromxmlstring(xmlOutput)

def Populate(isRecursive=False, isOverride=False, verSpec=None, location=None, dontBuildDirTree=False, timeSpec=None, listFile=None, elementList=None):
    output = raw.Populate(isRecursive=isRecursive, isOverride=isOverride, verSpec=verSpec, location=location, dontBuildDirTree=dontBuildDirTree, timeSpec=timeSpec, isXmlOutput=True, listFile=listFile, elementList=elementList)
    
    xmlElement = ElementTree.fromstring(output)
    if xmlElement is not None:
        message = xmlElement.find('message')
        if message is not None:
            errorAttrib = message.attrib.get('error')
            if errorAttrib is not None:
                sys.stderr.write("accurev populate error:\n{0}\n".format(message.text))
    
    if raw._lastCommand is not None:
        return (raw._lastCommand.returncode == 0)
    return None

class Show(object):
    @staticmethod
    def Users():
        xmlOutput = raw.Show.Users(isXmlOutput=True)
        return AccuRevShowUsers.fromxmlstring(xmlOutput)
    
    @staticmethod
    def Depots():
        xmlOutput = raw.Show.Depots(isXmlOutput=True)
        return AccuRevShowDepots.fromxmlstring(xmlOutput)

    @staticmethod
    def Streams(depot=None, timeSpec=None, stream=None, matchType=None, listFile=None, listPathAndChildren=False, listChildren=False, listImmediateChildren=False, nonEmptyDefaultGroupsOnly=False, includeDeactivatedItems=False, includeOldDefinitions=False):
        xmlOutput = raw.Show.Streams(depot=depot, timeSpec=timeSpec, stream=stream, matchType=matchType, listFile=listFile, listPathAndChildren=listPathAndChildren, listChildren=listChildren, listImmediateChildren=listImmediateChildren, nonEmptyDefaultGroupsOnly=nonEmptyDefaultGroupsOnly, isXmlOutput=True, includeDeactivatedItems=includeDeactivatedItems, includeOldDefinitions=includeOldDefinitions, includeHasDefaultGroupAttribute=True)
        return AccuRevShowStreams.fromxmlstring(xmlOutput)
        
# ################################################################################################ #
# Script Main                                                                                      #
# ################################################################################################ #
if __name__ == "__main__":
    print "This script is not intended to be run directly..."