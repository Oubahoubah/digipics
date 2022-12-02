#!/usr/bin/env python3
#
# digiimport.py - sort your pictures into year, month and if wished
# event folder

# Copyright (C) 2022 skrodzki@stevekist.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from pydoc import resolve
from typing import List
from exif import Image, DATETIME_STR_FORMAT
from datetime import datetime
import configargparse
import os
import os.path
import subprocess
import sys
import json
import re
import shutil

PICT_DATETIME_STR_FORMAT = "%Y%m%d_%H%M%S"
SUBPATH_DATETIME_STR_FORMAT = os.path.join("%Y","%m")
SIGNAL_DATETIME_STR_FORMAT = "%Y-%m-%d-%H%M%S"
WHATSAPP_DATETIME_STR_FORMAT = "%Y-%m-%d at %H.%M.%S"

def read_from_file(filepath):
    """
    reads data from file
    :param filepath:
    :return: data read from file
    """
    if os.path.isfile(filepath):
        with open(filepath) as file:
            data = file.read()
            return data
    else:
        print(f"File '{filepath}' is not existing")
        return None

def date_from_filename(f: str):
    desttime = None

    # now try if it is signal
    if f.startswith("signal"):
        finddate = re.match("signal-(\d+-\d+-\d+-\d+).jp.*g",f)
        if finddate:
            desttime = datetime.strptime(finddate.groups()[0], SIGNAL_DATETIME_STR_FORMAT)
            return desttime
        else:
            print(f"Signal image \'{f}\' has not the right convention ", end='')
            return None

    # now try What's app
    if f.startswith("WhatsApp Image"):
        finddate = re.match("WhatsApp Image (\d\d\d\d-\d\d-\d\d at \d\d.\d\d.\d\d).jp.*g",f)
        if finddate:
            desttime = datetime.strptime(finddate.groups()[0], WHATSAPP_DATETIME_STR_FORMAT)
            return desttime
        else:
            print(f"Whats App Image \'{f}\' has not the right convention ", end='')
            return None

    # last chance: maybe it is already the right filename?
    try:
        fileshortname, foo = os.path.splitext(f)
        desttime = datetime.strptime(fileshortname, PICT_DATETIME_STR_FORMAT)
        return desttime
    except:
        return None

def processdir(aktpath, sourcepath, destpath, subdir, nothing, keep):
    num = 0
    # print ("checking dir:",entry,"\n")
    createpath = ""
    entries = os.listdir(os.path.join(sourcepath, aktpath))
    subpathsingle = "_".join(aktpath.split(os.sep))
    destdir = os.path.join(destpath,subpathsingle)

    for f in entries:
        srcfile = os.path.join(sourcepath,aktpath,f)
        print(srcfile + " ", end='')
        file_name, file_extension = os.path.splitext(srcfile)
        file_extension = file_extension.lower()[1:]
        if os.path.isfile(srcfile) and (file_extension == "jpg" or file_extension == "jpeg" or file_extension =="png"):
            desttime = None
            with open(srcfile, 'rb') as image_file:
                my_image = Image(image_file)
                if my_image.has_exif:
                    try:                    #print(my_image.list_all())
                        desttime = datetime.strptime(my_image.datetime_original, DATETIME_STR_FORMAT)
                    except:
                        print("wrong exif data ", end='')
            if desttime is None:
                # now try if it is signal
                if f.startswith("signal"):
                    finddate = re.match("signal-(\d+-\d+-\d+-\d+).jp.*g",f)
                    if finddate:
                        desttime = datetime.strptime(finddate.groups()[0], SIGNAL_DATETIME_STR_FORMAT)
                    else:
                        print(f"{f} has not the right convention ", end='')
                # now try What's app
                elif f.startswith("WhatsApp Image"):
                    finddate = re.match("WhatsApp Image (\d\d\d\d-\d\d-\d\d at \d\d.\d\d.\d\d).jp.*g",f)
                    if finddate:
                        desttime = datetime.strptime(finddate.groups()[0], WHATSAPP_DATETIME_STR_FORMAT)
                    else:
                        print(f"{f} has not the right convention ", end='')
            # last chance: maybe it is already the right filename?
            if desttime is None:
                try:
                    fileshortname, foo = os.path.splitext(f)
                    desttime = datetime.strptime(fileshortname, PICT_DATETIME_STR_FORMAT)
                except:
                    desttime = None
            # ok, now process, if we have found something
            if desttime is not None:
                if file_extension == "jpeg":
                    # there is no reasion to keep jpeg as extension
                    file_extension = "jpg"
                destname = desttime.strftime(PICT_DATETIME_STR_FORMAT)
                fulldestpath = os.path.join(destpath, desttime.strftime(SUBPATH_DATETIME_STR_FORMAT))
                if subdir:
                    fulldestpath = os.path.join(fulldestpath, subdir)
                fulldestination = os.path.join(fulldestpath, destname+"."+file_extension)
                if not nothing:
                    # now really process
                    if not os.path.isdir(fulldestpath):
                        os.makedirs(fulldestpath)
                        print(f"Dir \'{fulldestpath}\' created. ", end='')
                    if keep:
                        shutil.copy(srcfile, fulldestination)
                    else:
                        shutil.move(srcfile, fulldestination)
                    num = num + 1
                print("->", fulldestination)
            else:
                print("-> unprocessed (rename to YYYYMMDD_hhmmss or set exif data)")
        else:
            print("no picture")
    return num

def main():
    num = 0
    cfgfile = os.path.expanduser("~/.digipics.cfg")
    parser = configargparse.ArgumentParser(description='Import your pictures into your collections', default_config_files = [ cfgfile ])

    parser.add_argument('--collection', help=f'the collection path (set from \'{cfgfile}\': \'\'', required=True)
    parser.add_argument('-n', '--nothing', help='do nothing (just show what would be done)', action='store_true')
    parser.add_argument('-k', '--keep', help='keep files in place (should not be necessary for regular use)', action='store_true')
    parser.add_argument('subdir', default='', help='subdir (e.g. event name)', nargs='?')

    args, unknown = parser.parse_known_args()

    ## main
    print(args)
    print(args.collection)

    sourcepath = os.path.abspath(os.getcwd())
    destpath = os.path.abspath(args.collection)

    num = processdir("", sourcepath, destpath, args.subdir, args.nothing, args.keep)

    print("Total pictures processed:", num)

if __name__ == "__main__":
    main()