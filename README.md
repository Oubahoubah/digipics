# digipics

Scripts to handle your digital pictures

## Introduction

Over the years you will collect a lot of memories in the pictures you have taken. You have perhaps started early with digital imaging or you have converted analog pictures by scanning them... in the end your picture collection is rather big and hard to overwatch. There are tools around, which help you to find the pictures in your collection, but they may be only on mobile or only on desktop...

So an idea of rather basically organizing pictures is not a bad one.

## Folder Structure

The structure choosen here is a folder structure:

```
YYYY /
      MM
      MM /
           EVENT
```
e.g.

```
2001 /
      01
      02 /
           Party_in_Hamburg
```
If there is an event to mention it may reside in the month folder where it happened - if this event lasts over to months, there will be an event folder in each month.

The pictures are all renamed to their date stamp when they have been taken: 20010623_173401.jpg
Right now, there was no need for two pictures taken at the same second...

This all does not change the _payload_ of the picture nor it's EXIF (Metadata). Pictures are only renamed and moved to their destination location. All this action is done by the script `digiimport`.

## The scripts
### digiimport
`digiimport` is a short script to move your pictures - with no content changed at all, not exif not data - to a collection structured by YYYY/MM and optional event.

## digiphone

`digiphone` is the script to convert the nested folder hierarchy as created above to a flat folder structure and resized pictures. Only files ending with .jpg and .png are converted.

It is designed to provide the right structure for the famous FOSS library viewer Les Pas: https://github.com/scubajeff/lespas

By this, you are able to sync all your pictures with your mobile phone: while the local collection eats up around 29G, the reduced sizes dir needs 6,2G... 

You have also the possibility to share a folder with a Nextcloud group by writing the Name of this Group in  the folder in a file called `.ncshare`

For installation, put the script in your bin path and put also the NextCloud.py library from https://github.com/Dosugamea/NEXT-OCS-API-forPy there.

Start the script with: 

```
digiphone --collection source/path/ --phone destination/path --ncurl https://nextcloud.example.com --ncuser theuser --ncpasswd joshua42 --ncbasepath lespas
```

starting with -n would show you, what the script would do. 
The --nc* parameters are only necessary if you want to use Nextcloud shares. 
Perhaps try it first with just a few folders, which you copy to a test location.

The easiest way to achieve that all users who use lespas get added folders automagically is to set the standard shared folder in NextCloud to 'lespas'. This can be achieved by adding:

```
'share_folder' => '/lespas',
```

to nextclouds config.php

Otherwise, the users of the group which get the shares, will have to move their shared folders also to an own lespas folder.

### My Workflow looks like this (or: The user story)

I have on my PC a folder called "/home/steve/pictures/incoming" and my collection should be under "/home/steve/pictures/collection". Then I start in the folder incoming this script with (assume it is in your path) `digiimport --collection /home/steve/pictures/collection` and the magic starts. The script detects EXIF dates, Signal picture naming conventions, What's app naming conventions, android generic naming conventions and gets the date the pictures was made from that. The picture will then be renamed to YYYYMMDD_HHMMSS and moved to a folder inside your collection called YYYY/MM.

Now you have organized all your pictures in a structure on your PC. But you want to have the possibility to show your memories to your friends and browse them yourself while you are on travel and perhaps even not connected to the internet. Could this be possible although you have collected your memories over 30 years and more?

Yes it is, just with some help of technology.

e.g. an uncompressed collection with approx 18000 pics eats up 30GB. After compressing/resizing the pics, the collection eats up 6,3GB

*It is very important to understand, that the original pictures content will not (never!) be touched! Only the filename can change.*

So the workflow to have your whole memories on your phone tablet is:

1. convert/resize your collection (from now called phone collection)
2. upload/sync your phone collection to your mobile device
3. choose a fast picture viewer

Now for all that there are perfect tools:

1. resizing: see digiphone below
2. syncing: use Nextcloud / LesPas (Android)
3. Picture viewer: LesPas (Android)

## Installation

Create a virtual environment:
```
$ python3 -m venv ~/.venv/digipics
```

Activate it:
```
$ source ~/.venv/digipics/bin/activate
```

Install pipx:
```
$ pip3 install pipx
```

Clone the repository:
```
$ cd Downloads
$ git clone https://github.com/Oubahoubah/digipics.git
```

And finally this should build the app:
```
$ cd digipics
$ pipx install -e .
```
