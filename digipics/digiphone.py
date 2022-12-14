#!/usr/bin/env python3
#
# digiphone - convert your pics for a phone friendly file structure
# with sharing support for nextcloud

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
from typing import List
import configargparse
import os
import os.path
import subprocess
import sys
import json
from wand.image import Image
from wand.exceptions import ImageError

# uses: https://github.com/Dosugamea/NEXT-OCS-API-forPy just put it in the same folder

from digipics.NextCloud import NextCloud

def main():

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

    def nextcloud_set_share(newshare, path):
        if nxc is not None:
            shareset = False
            for share in sharelist["ocs"]["data"]:
                #print(share["path"], ":", share["share_with"])
                if share["path"] == path and share["share_with"] == newshare:
                    # print(f"Nextcloud Share for {newshare} already set on {path}")
                    shareset = True
            if not shareset:
                if args.nothing:
                    print(f"Would create Nextcloud Share for {newshare} on {path}")
                else:
                    print(f"Create Nextcloud Share for {newshare} on {path}")
                    nxc.createShare(path,1,shareWith=newshare)

    def processdir(aktpath):
        # print ("checking dir:",entry,"\n")
        createpath = ""
        entries = os.listdir(os.path.join(sourcepath, aktpath))
        subpathsingle = "_".join(aktpath.split(os.sep))
        destdir = os.path.join(destpath,subpathsingle)

        for f in entries:
            srcfile = os.path.join(sourcepath,aktpath,f)
            # print("Checking: ", srcfile)
            if os.path.isfile(srcfile) and (((f[-3:] == "jpg") or (f[-3:] == "png"))):
                destfile = os.path.join(destdir,f)
                destlist.append(destfile) ## add the file to the list, which will be checked later for deletion
                if (not os.path.isfile(destfile)): ## check, if destinationfile already exists
                    if (not os.path.isdir(destdir)): ## check if destination dir already exists
                        if (args.nothing):
                            print("Would create dir: ",destdir)
                        else:
                            print("Creating dir: ",destdir)
                            os.mkdir(destdir)
                    if (not args.nothing):
                        print("Converting: ", srcfile," -> ", destfile)
                        try:
                            with Image(filename=srcfile) as img:
                                img.transform(resize=f'{resize}>')
                                img.gamma(1.3)
                                img.save(filename=destfile)
                        except ImageError as e:
                            print(f"Could not convert image: \'{srcfile}\': {e}")
                        # subprocess.call(f"convert -gamma 1.3 -resize {resize} "+srcfile+" "+destfile, shell=True)
                    else:
                        print("Would convert: ", srcfile," -> ", destfile)
            if os.path.isdir(srcfile):
                processdir(os.path.join(aktpath,f))
        if ".ncshare" in entries:
            sharedwith = read_from_file(os.path.join(sourcepath,aktpath,".ncshare"))
            sharedwith = sharedwith.rstrip()
            #print(f"Dir {destdir} will be shared with {sharedwith}")
            nextcloud_set_share(sharedwith, "/"+args.ncbasepath+"/"+subpathsingle)

    cfgfile = os.path.expanduser("~/.digipics.cfg")

    destlist: List[str] = []
    parser = configargparse.ArgumentParser(
        formatter_class=configargparse.RawDescriptionHelpFormatter,
        description="Convert your pictures to a flat hierarchy with nextcloud and lespas support",
        epilog=common.EPILOG,
        default_config_files=[cfgfile],
    )

    parser.add_argument('-n', '--nothing', help='do nothing', action='store_true')
    parser.add_argument('--collection', help='the source path of your collection', required=True)
    parser.add_argument('--phone', help='the path to sync with the phone', required=True)
    parser.add_argument('--resize', type=str, help='resize string (default 1920x1080)', default="1920x1080")
    parser.add_argument('--gamma', type=float, help='gamma correction (default 1.3)', default=1.3)
    parser.add_argument('--ncurl', help='nextcloud base url')
    parser.add_argument('--ncbasepath', help='nextcloud base path')
    parser.add_argument('--ncuser', help='nextcloud user')
    parser.add_argument('--ncpasswd', help='nextcloud password')


    args, unknown = parser.parse_known_args()

    if args.resize:
        resize = args.resize

    nxc = None

    if args.ncurl and args.ncbasepath and args.ncuser and args.ncpasswd and args.ncurl != "" and args.ncpasswd != "" and args.ncuser != "":
        nxc = NextCloud(args.ncurl, args.ncuser, args.ncpasswd, True)
        sharelist = nxc.getShares()
        #print(sharelist)

    yetdone = 0

    ## main

    sourcepath = os.path.abspath(args.collection)
    destpath = os.path.abspath(args.phone)

    num = 0
    processdir("")

    ## now check if there are files that should be deleted

    for (dirpath, dirnames, filenames) in os.walk(destpath):
        for f in filenames:
            lookfile = os.path.join(dirpath, f) # this is the file we found
            if (destlist.count(lookfile) == 0):
                if lookfile[-4:] == "json":
                    # print("Ignore json file (from lespas?):", lookfile)
                    pass
                else:
                    if (args.nothing):
                        print("Would delete:",lookfile)
                    else:
                        print("Deleting:",lookfile)
                        os.remove(lookfile)

    print("Total pictures:",len(destlist))


if __name__ == "__main__":
    main()