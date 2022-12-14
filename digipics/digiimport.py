#!/usr/bin/env python3
#
# digiimport - sort your pictures into year, month and if wished
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

from digipics import common
from pydoc import resolve
from typing import List, Optional
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
import pkg_resources  # part of setuptools
import textwrap


PICT_DATETIME_STR_FORMAT = "%Y%m%d_%H%M%S"
SUBPATH_DATETIME_STR_FORMAT = os.path.join("%Y", "%m")



def check_exif(filepath) -> Optional[datetime]:
    """
    reads data from file via exif
    :param filepath: full path to file
    :return: exif datetime_original from file
        None if nothing found
    """
    if os.path.isfile(filepath):
        with open(filepath, "rb") as image_file:
            my_image = Image(image_file)
            if my_image.has_exif:
                try:  # print(my_image.list_all())
                    desttime = datetime.strptime(
                        my_image.datetime_original, DATETIME_STR_FORMAT
                    )
                    return desttime
                except:
                    print("wrong exif data ", end="")
                    return None

    else:
        print(f"File '{filepath}' is not existing")
    return None

def check_signal(filename) -> Optional[datetime]:
    """checks if the filename is a signal filename and contains the datetime

    Args:
        filename (str): filename with no proceeding path

    Returns:
        datetime: timestamp from signal filename
        None if nothing found
    """
    SIGNAL_DATETIME_STR_FORMAT = "%Y-%m-%d-%H%M%S"
    if filename.startswith("signal"):
        finddate = re.match("signal-(\d+-\d+-\d+-\d+)(_\d\d\d)*.jp.*g", filename)
        if finddate:
            desttime = datetime.strptime(
                finddate.groups()[0], SIGNAL_DATETIME_STR_FORMAT
            )
            return desttime
        else:
            print(f"Signal image '{filename}' has not the right convention ", end="")
            return None
    return None


def check_whatsapp(filename: str) -> Optional[datetime]:
    """checks if the filename is a whatsapp filename and contains the datetime

    Args:
        filename (str): filename with no proceeding path

    Returns:
        datetime: timestamp from whatsapp filename
        None if nothing found
    """
    WHATSAPP_DATETIME_STR_FORMAT = "%Y-%m-%d at %H.%M.%S"
    if filename.startswith("WhatsApp Image"):
        finddate = re.match(
            "WhatsApp Image (\d\d\d\d-\d\d-\d\d at \d\d.\d\d.\d\d).jp.*g", filename
        )
        if finddate:
            desttime = datetime.strptime(
                finddate.groups()[0], WHATSAPP_DATETIME_STR_FORMAT
            )
            return desttime
        else:
            print(f"Whats App Image '{filename}' has not the right convention ", end="")
    return None


def check_filename(filename: str) -> Optional[datetime]:
    """checks if filename is the pure date (anroid?)

    Args:
        filename (str): filename with no proceeding path

    Returns:
        datetime: timestamp from filename
        None if nothing found
    """
    try:
        fileshortname, foo = os.path.splitext(filename)
        desttime = datetime.strptime(fileshortname, PICT_DATETIME_STR_FORMAT)
        return desttime
    except:
        return None


def processdir(
    aktpath,
    sourcepath,
    destpath,
    subdir="",
    nothing=False,
    keep=False,
    no_check_exif=False,
    no_check_whatsapp=False,
    no_check_signal=False,
    no_check_filename=False,
):
    num = 0
    # print ("checking dir:",entry,"\n")
    createpath = ""
    entries = os.listdir(os.path.join(sourcepath, aktpath))
    subpathsingle = "_".join(aktpath.split(os.sep))
    destdir = os.path.join(destpath, subpathsingle)

    for f in entries:
        srcfile = os.path.join(sourcepath, aktpath, f)
        print(srcfile + " ", end="")
        file_name, file_extension = os.path.splitext(srcfile)
        file_extension = file_extension.lower()[1:]
        if os.path.isfile(srcfile) and (
            file_extension == "jpg"
            or file_extension == "jpeg"
            or file_extension == "png"
        ):
            desttime = None
            if not no_check_exif:
                desttime = check_exif(srcfile)
            if desttime is None and not no_check_signal:
                desttime = check_signal(f)
            if desttime is None and not no_check_whatsapp:
                desttime = check_whatsapp(f)
            if desttime is None and not no_check_filename:
                desttime = check_filename(f)

            # ok, now process, if we have found something
            if desttime is not None:
                if file_extension == "jpeg":
                    # there is no reasion to keep jpeg as extension
                    file_extension = "jpg"
                destname = desttime.strftime(PICT_DATETIME_STR_FORMAT)
                fulldestpath = os.path.join(
                    destpath, desttime.strftime(SUBPATH_DATETIME_STR_FORMAT)
                )
                if subdir:
                    fulldestpath = os.path.join(fulldestpath, subdir)
                fulldestination = os.path.join(
                    fulldestpath, destname + "." + file_extension
                )
                if not nothing:
                    # now really process
                    if not os.path.isdir(fulldestpath):
                        os.makedirs(fulldestpath)
                        print(f"Dir '{fulldestpath}' created. ", end="")
                    destsize = 0
                    srcstats = os.stat(srcfile)
                    srcsize = srcstats.st_size
                    if os.path.isfile(fulldestination):
                        deststats = os.stat(fulldestination)
                        destsize = deststats.st_size
                        if destsize == srcsize:
                            print(" allready exists and has same size. Untouched.")
                        else:
                            print(" allready exists and has different size. Untouched.")
                            # at this point we should try to increase the timestamp e.g. by one second?
                    else:
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
    parser = configargparse.ArgumentParser(
        formatter_class=configargparse.RawDescriptionHelpFormatter,
        description="Import your pictures into your collections",
        epilog=common.EPILOG,
        default_config_files=[cfgfile],
    )

    parser.add_argument(
        "--collection",
        help=f"the collection path (set from '{cfgfile}': ''",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--nothing",
        help="do nothing (just show what would be done)",
        action="store_true",
    )
    parser.add_argument(
        "-k",
        "--keep",
        help="keep files in place (should not be necessary for regular use)",
        action="store_true",
    )
    parser.add_argument(
        "--no_check_exif",
        help="do not check for exif data",
        action="store_true",
    )
    parser.add_argument(
        "--no_check_signal",
        help="do not check for signal filename timestamp",
        action="store_true",
    )
    parser.add_argument(
        "--no_check_whatsapp",
        help="do not check for whatsapp filename timestamp",
        action="store_true",
    )
    parser.add_argument(
        "--no_check_filename",
        help="do not check for filename timestamp",
        action="store_true",
    )
    parser.add_argument(
        "subdir", default="", help="subdir (e.g. event name)", nargs="?"
    )

    args, unknown = parser.parse_known_args()

    ## main
    print(args)
    print(args.collection)

    sourcepath = os.path.abspath(os.getcwd())
    destpath = os.path.abspath(args.collection)

    num = processdir(
        "",
        sourcepath,
        destpath,
        args.subdir,
        args.nothing,
        args.keep,
        args.no_check_exif,
        args.no_check_whatsapp,
        args.no_check_signal,
        args.no_check_filename,
    )

    print("Total pictures processed:", num)


if __name__ == "__main__":
    main()
