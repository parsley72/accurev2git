#!/usr/bin/python2

# ################################################################################################ #
# Git utility script                                                                               #
# Author: Lazar Sumar                                                                              #
# Date:   03/12/2014                                                                               #
#                                                                                                  #
# This script is a library that is intended to expose a Python API for the git commands and        #
# command result data structures.                                                                  #
# ################################################################################################ #

import sys
import os
import subprocess
import xml.etree.ElementTree as ElementTree
import datetime
import re
import types

gitCmd = u'git'

class GitStatus(object):
    # Regular expressions used in fromgitoutput classmethod for parsing the different git lines.
    branchRe        = re.compile("^On branch (\\w)$")
    blankRe         = re.compile("^\\s*$")
    commentRe       = re.compile("^\\s+\\(.*\\)$")
    fileRe          = re.compile("^\\s+(new file|modified|deleted):\\s+(\\S+)\\s*$")
    untrackedFileRe = re.compile("^\\s+(\\S+)\\s*$")
        
    def __init__(self, branch=None, staged=[], changed=[], untracked=[]):
        self.branch    = branch    # Name of the branch.
        self.staged    = staged    # A list of (filename, file_status) tuples
        self.changed   = changed   # A list of (filename, file_status) tuples
        self.untracked = untracked # A list of (filename,) tuples

    def __repr__(self):
        str  = "On branch {0}\n".format(self.branch)
        if self.staged is not None and len(self.staged) > 0:
            str += "Changes to be committed:\n\n"
            for file, status in self.staged:
                str += " {0}: {1}\n".format(status, file)
            str += "\n"
        if self.changed is not None and len(self.changed) > 0:
            str += "Changes not staged for commit:\n\n"
            for file, status in self.changed:
                str += " {0}: {1}\n".format(status, file)
            str += "\n"
        if self.untracked is not None and len(self.untracked) > 0:
            str += "Untracked files:\n\n"
            for file in self.untracked:
                str += " {0}\n".format(file[0])
            str += "\n"
        return str
    
    @classmethod
    def fromgitoutput(cls, gitOutput):
        lines = gitOutput.split('\n')
        # git status output example
        # On branch <branch name>
        # Changes to be committed:
        #   (use "git reset HEAD <file>..." to unstage)
        #  
        #  new file:   file1.ext
        #  modified:   file2.ext
        #  deleted:    file3.ext
        #  
        # Changes not staged for commit:
        #   (use git add <file>..." to update what will be committed)
        #   (use "git checkout -- <file>..." to discard changes in working directory)
        #  
        #  modified:    file2.ext
        #  deleted:     file4.ext
        #  
        # Untracked files:
        #   (use "git add <file>..." to include in what will be committed)
        #  
        #  file5.ext
        #  file6.ext
        
        # Parse the branch
        branchName    = None
        branchSpec    = lines.pop(0)
        branchReMatch = GitStatus.branchRe.match(branchSpec)
        if branchReMatch:
            branchName = branchReMatch.group(1)
        
        stagedFiles = []
        changedFiles = []
        untrackedFiles = []
        
        lastHeading = lines.pop(0)
        while len(lines) > 0:
            if lastHeading == "Changes to be committed:":
                # Find the first blank line
                nextLine = lines.pop(0)
                while not GitStatus.blankRe.match(nextLine) and len(lines) > 0:
                    nextLine = lines.pop(0)
                # Parse files until blank line
                nextLine = lines.pop(0)
                while not GitStatus.blankRe.match(nextLine) and len(lines) > 0:
                    fileMatch = GitStatus.fileRe.match(nextLine)
                    if not fileMatch:
                        raise Exception("Line [{0}] did not match [{1}]".format(nextLine, GitStatus.fileRe.pattern))
                    fileStatus = fileMatch.group(1)
                    fileName   = fileMatch.group(2)
                    stagedFiles.append((fileName, fileStatus))
                    
                    nextLine = lines.pop(0)
            elif lastHeading == "Changes not staged for commit:":
                # Find the first blank line
                nextLine = lines.pop(0)
                while not GitStatus.blankRe.match(nextLine) and len(lines) > 0:
                    nextLine = lines.pop(0)
                # Parse files until blank line
                nextLine = lines.pop(0)
                while not GitStatus.blankRe.match(nextLine) and len(lines) > 0:
                    fileMatch = GitStatus.fileRe.match(nextLine)
                    if not fileMatch:
                        raise Exception("Line [{0}] did not match [{1}]".format(nextLine, GitStatus.fileRe.pattern))
                    fileStatus = fileMatch.group(1)
                    fileName   = fileMatch.group(2)
                    changedFiles.append((fileName, fileStatus))
                    
                    nextLine = lines.pop(0)
            elif lastHeading == "Untracked files:":
                # Find the first blank line
                nextLine = lines.pop(0)
                while not GitStatus.blankRe.match(nextLine) and len(lines) > 0:
                    nextLine = lines.pop(0)
                # Parse files until blank line
                nextLine = lines.pop(0)
                while not GitStatus.blankRe.match(nextLine) and len(lines) > 0:
                    fileMatch = GitStatus.untrackedFileRe.match(nextLine)
                    if not fileMatch:
                        raise Exception("Line [{0}] did not match [{1}]".format(nextLine, GitStatus.untrackedFileRe.pattern))
                    fileName   = fileMatch.group(1)
                    untrackedFiles.append((fileName,))
                    
                    nextLine = lines.pop(0)
            
            if len(lines) > 0:
                lastHeading = lines.pop(0)
        
        # stagedFiles and changedFiles are lists of tuples containing two items: (filename, file_status)
        # untracked is also a list of tuples containing two items but the second items is always empty: (filename,)
        return cls(branch=branchName, staged=stagedFiles, changed=changedFiles, untracked=untrackedFiles)

# GitBranchListItem is an object serialization of a single branch output when the git branch -vv
# command is run.
class GitBranchListItem(object):
    branchVVRe = re.compile("^(?P<iscurrent>\\*)?\\s+(?P<name>\\S+)\\s+(?P<hash>\\S+)\\s+(?:(?P<remote>\\[\\S+\\])\\s+)?(?P<comment>.*)$")
    def __init__(self, name, shortHash, remote, shortComment, isCurrent):
        self.name = name
        self.shortHash = shortHash
        self.remote = remote
        self.shortComment = shortComment
        self.isCurrent = isCurrent
    
    def __repr__(self):
        if self.isCurrent:
            str = "*"
        else:
            str = " "
        str += " {0} {1}".format(self.name, self.shortHash)
        if self.remote is not None:
            str += " {0}".format(self.remote)
        str += " {0}".format(self.shortComment)
        
        return str
        
    def __eq__(self, other):
        if type(other) == GitBranchListItem:
            return (self.name == other.name and self.shortHash == other.shortHash)
        raise Exception("Can't compare {0} with {1}".format(type(self), type(other)))
        
    @classmethod
    def fromgitbranchoutput(cls, outputLine):
        branchVVMatch = GitBranchListItem.branchVVRe.match(outputLine)
        if branchVVMatch is not None:
            name = branchVVMatch.group("name")
            shortHash = branchVVMatch.group("hash")
            comment = branchVVMatch.group("comment")
            remote =  branchVVMatch.group("remote")
            isCurrent = branchVVMatch.group("iscurrent")
            isCurrent = (isCurrent is not None)
            
            return cls(name=name, shortHash=shortHash, remote=remote, shortComment=comment, isCurrent=isCurrent)
        return None
    
class repo(object):
    def __init__(self, path):
        self.path = path
        self._cwdQueue = []
        self.lastError = None
        
    def _pushd(self, newPath):
        self._cwdQueue.insert(0, os.getcwd())
        os.chdir(newPath)
    
    def _popd(self):
        os.chdir(self._cwdQueue.pop(0))
    
    def _docmd(self, cmd):
        try:
            #strCmd = ' '.join(cmd)
            self._pushd(self.path)
            output = subprocess.check_output(cmd)
            self._popd()
        except subprocess.CalledProcessError as e:
            self.lastError = e
            return None
        return output
        
    def checkout(self, branchName=None, isNewBranch=False):
        cmd = [ gitCmd, u'checkout' ]
        
        if isNewBranch:
            cmd.append(u'-b')
        
        if branchName is not None:
            cmd.append(branchName)
        
        return self._docmd(cmd)

    def branch(self):
        pass
    
    def rm(self, fileList = []):
        if len(fileList) > 0:
            cmd = [ gitCmd, u'rm', u'--' ]
            cmd.extend(fileList)
            
            output = self._docmd(cmd)
            
            return (output is not None)
        else:
            raise Exception(u'Error, tried to add empty file list')
    
    def add(self, fileList = [], force=False, update=False):
        cmd = [ gitCmd, u'add' ]
        
        if force:
            cmd.append(u'-f')
        
        if update:
            cmd.append(u'-u')
        
        if fileList is not None and len(fileList) > 0:
            cmd.append(u'--')
            if isinstance(fileList, list):
                cmd.extend(fileList)
            else:
                cmd.append(unicode(fileList))
        
        output = self._docmd(cmd)
        
        return (output is not None)
    
    def commit(self, message=None, messageFile=None, author=None, date=None, committer=None, committer_date=None):
        cmd = [ gitCmd, u'commit' ]
        
        if author is not None:
            cmd.append(u'--author="{0}"'.format(author))
        
        if date is not None:
            if isinstance(date, datetime.datetime):
                date = date.isoformat()
            cmd.append(u'--date="{0}"'.format(date))
        
        if message is not None and len(message) > 0:
            cmd.extend([ u'-m', unicode(message) ])
        elif messageFile is not None:
            cmd.extend([ u'-F', unicode(messageFile) ])
        else:
            raise Exception(u'Error, tried to commit with empty message')
        
        # Backup the existing commiter information
        oldCommitterName = None
        if os.environ['GIT_COMMITTER_NAME'] is not None:
            oldCommitterName = os.environ['GIT_COMMITTER_NAME']
        oldCommitterEmail = None
        if os.environ['GIT_COMMITTER_EMAIL']:
            oldCommitterEmail = os.environ['GIT_COMMITTER_EMAIL']
        oldCommitterDate = None
        if os.environ['GIT_COMMITTER_DATE']:
            oldCommitterDate = os.environ['GIT_COMMITTER_DATE']
        
        # Set the new commiter information
        if committer is not None:
            m = re.search('(.*?)<(.*?)>', committer)
            if m is not None:
                committerName = m.group(0).strip()
                committerEmail = m.group(1).strip()
                os.environ['GIT_COMMITTER_NAME'] = committerName
                os.environ['GIT_COMMITTER_EMAIL'] = committerEmail
        
        if committer_date is not None:
            if committer_date is not None:
                if isinstance(committer_date, datetime.datetime):
                    committer_date = committer_date.isoformat()
            os.environ['GIT_COMMITTER_DATE'] = '{0}'.format(committer_date)
        
        # Execute the command
        output = self._docmd(cmd)
        
        # Restore backed up environment variables
        if oldCommitterName is not None:
            os.environ['GIT_COMMITTER_NAME'] = oldCommitterName
        if oldCommitterEmail is not None:
            os.environ['GIT_COMMITTER_EMAIL'] = oldCommitterEmail
        if oldCommitterDate is not None:
            os.environ['GIT_COMMITTER_DATE'] = oldCommitterDate
        
        return (output is not None)
    
    def branch_list(self):
        cmd = [ gitCmd, u'branch', u'-vv' ]
            
        output = self._docmd(cmd)
        
        if output is not None:
            branchList = []
            outputLines = output.split(u'\n')
            for line in outputLines:
                if len(line.strip()) > 0:
                    branchList.append(GitBranchListItem.fromgitbranchoutput(line))
            return branchList
        return None

    def status(self):
        cmd = [ gitCmd, u'status' ]
            
        output = self._docmd(cmd)
        if output is not None:
            return GitStatus.fromgitoutput(output)
        return None

    def reset(self, branch=None, isHard=False, isSoft=False):
        cmd = [ gitCmd, u'reset' ]
        
        if isHard:
            cmd.append(u'--hard')
        if isSoft:
            cmd.append(u'--soft')
        
        if branch is not None:
            cmd.append(branch)
        
        return self._docmd(cmd)
    
    def clean(self, force=False):
        cmd = [ gitCmd, u'clean' ]
    
        if force:
            cmd.append(u'-f')
        
        return self._docmd(cmd)
        
def isRepo(path=None):
    if path is not None and os.path.isdir(path):
        if os.path.isdir(os.path.join(path, ".git")):
            return True
    return False

def init(isBare=False, path=None):
    try:
        cmd = [ gitCmd, u'init' ]
        if isBare:
            cmd.append(u'--bare')
        if path is not None:
            cmd.append(str(path))
        
        output = subprocess.check_output(cmd)
    except:
        return None
    return repo(path)

def open(path):
    if isRepo(path):
        return repo(path=path)
    return None

def delete(path=None):
    if path is None:
        path = os.getcwd()
    if isRepo(path=path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        return True
    return False

