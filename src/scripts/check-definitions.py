#!/usr/bin/env python
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
#
# check-definitions.py
#  This script checks the consistency between compiler definitions
# of the native part of CoreCLR and managed part (mscorlib.dll) of
# CoreCLR
#
# Usage:
#   $ ./check-definitions.py Definition_File String_of_Definitions [String_of_Ignored_Definitions]
#
#      Definition_File: the filename of a file containing the list of
#          compiler definitions of CMAKE, seperated by line.
#          (Mandatory)
#      String_of_Definitions: the list of managed code compiler
#          definitions, seperated by semicolon without spaces.
#          (Mandatory)
#      String_of_Ignored_Definitions: the list of compiler definitions
#          to be suppressed from emitting warnings, seperated by semicolon without spaces.
#          (Optional)
#
# (c) 2016 MyungJoo Ham <myungjoo.ham@samsung.com>

from __future__ import print_function

import sys
import re

debug = 0

# For the native part, return the sorted definition array.
def loadDefinitionFile(filename):
    result = []
    f = open(filename, 'r')
    for line in f:
        theLine = line.rstrip("\r\n").strip()
        if (len(theLine) > 0):
            result.append(theLine)

    f.close()
    result = sorted(result)
    return result


# For the managed part, return the sorted definition array.
def loadDefinitionString(string):
    splitted = string.split(';')
    result = []
    for line in splitted:
       theLine = line.strip()
       if (len(theLine) > 0):
           result.append(theLine)

    result = sorted(result)
    return result


def getDiff(arrNative, arrManaged):
    result = [[], []]
    iF = 0 # From file (native)
    nF = len(arrNative)

    iS = 0 # From string (managed)
    nS = len(arrManaged)

    while (iS < nS) and (iF < nF):
        if (arrNative[iF] == arrManaged[iS]):
            if (debug == 1):
                print("Both have " + arrNative[iF])
            iF = iF + 1
            iS = iS + 1
        elif (arrNative[iF] == (arrManaged[iS] + "=1")):
            if (debug == 1):
                print("Both have " + arrNative[iF] + "(=1)")
            iF = iF + 1
            iS = iS + 1
        elif (arrNative[iF] < arrManaged[iS]):
            if (debug == 1):
                print("--- Managed Omitted " + arrNative[iF])
            result[1].append(arrNative[iF])
            iF = iF + 1
        elif (arrNative[iF] > arrManaged[iS]):
            if (debug == 1):
                print("+++ Managed Added " + arrManaged[iS])
            result[0].append(arrManaged[iS])
            iS = iS + 1

    if (iS < nS):
        while iS < nS:
            if (debug == 1):
                print("+++ Managed Added " + arrManaged[iS])
            result[0].append(arrManaged[iS])
            iS = iS + 1
    elif (iF < nF):
        while iF < nF:
            if (debug == 1):
                print("--- Managed Omitted " + arrNative[iF])
            result[1].append(arrNative[iF])
            iF = iF + 1
    return result


def printPotentiallyCritical(arrDefinitions, referencedFilename, arrIgnore):
    f = open(referencedFilename, 'r')
    content = f.read()
    f.close()
    for keyword in arrDefinitions:
        skip = 0

        if (keyword[-2:] == "=1"):
            key = keyword[:-2]
        else:
            key = keyword

        if re.search("[^\\w]"+key+"[^\\w]", content):
            for ign in arrIgnore:
                if key == ign:
                    skip = 1
                    break
            if skip == 0:
                print(keyword)

# MAIN SCRIPT
if len(sys.argv) < 3:
    print("\nUsage:")
    print("$ check-definitions.py [Definition file] [String of definitions]")
    print("    Definition file contains the list of cmake (native) compiler definitions")
    print("      seperated by line.")
    print("    String of definitions contains the list of csproj (managed) definitions")
    print("      seperated by semicolons.")
    sys.exit(-1)

filename = sys.argv[1]
string = sys.argv[2]

arrayNative = loadDefinitionFile(filename)
arrayManaged = loadDefinitionString(string)
arrayIgnore = []

if len(sys.argv) > 3:
    arrayIgnore = loadDefinitionString(sys.argv[3])

arrays = getDiff(arrayNative, arrayManaged)
# arrays[0] = array of added in managed
# arrays[1] = array of omitted in managed (added in native)

print("Potentially Dangerous Compiler Definitions in clrdefinitions.cmake (omitted in native build):")
printPotentiallyCritical(arrays[0], "../../clrdefinitions.cmake", arrayIgnore)

print("Potentially Dangerous Compiler Definitions in clr.defines.targets (omitted in managed build):")
printPotentiallyCritical(arrays[1], "../../clr.defines.targets", arrayIgnore)

print("Definition Check Completed.")

