A simple backup script to be run on a windows desktop that synchronizes and differentially backs up a desktop, a network storage device and an external hard drive. Data can be injected into either the network storage device or the desktop and changes will be synchronized and propogated in such a way that data should not be lost or overwritten.

Under the hood this scrip uses python, rdiff-backup and unison.

See megabackup.py for details.

# written by Andrew Leifer, leifer@fas.harvard.edu
# With code snippetts from Benjamin Schwartz, InnoboxDevices, Innobackup at
# http://github.com/InnoBox/innobackup
# in file /overlay/usr/local/bin/innobox_perform_backup

# Requirements:
# rdiff-backup.exe from http://www.nongnu.org/rdiff-backup/
# unison.exe from http://www.cis.upenn.edu/~bcpierce/unison/
# Python from http://www.python.org/download/

# Given a desktop, a server and an external hard drive, this system will:
# - Make differential backups of directories from the server to the external drive
# - Make differential backups of directories on the desktop onto a secondary location on the desktop
# - Synchronize the server and the desktop
# - Re-differential backup the server onto the external drive
#
# These are the use cases I am interested in.
# There are two types of directories, "Data" directories that primarily reside on the server and
# are not used day to day and "Home" directories that a user will want easy access to on their local machine.
#
# - "Data" added to the server from another machine should get propogated to the external backup drive.
#
# - The "home" directory should always be up to date on the server so that a user may access their home directory
# from their desktop, or off site and changes are propogated either way.
#
# - Anything on the server should be backed up differentially.
#
#
# Q: Why are you making a differential backup of the users "home" directories rom one location on the
# desktop to another location also on the desktop? This seems stupid.
#
# A: I am worried that automaticly synchronizing the home directory with the server directory could lose data. For example,
# the automatic synchronization will likely be based on time stamps. Imagine that a user regularly changes files on his/her
# desktop and then the synchronization, when works properly propogates those changes to the server because they have a
# new timestamp. If the server's clock gets out of whack, the server may appear to have newer versions of files then
# the desktop, and now the users changes are overwritten. BUT if the user also has a local differential backup, the user will
# eventually figure out that their data is whack and they will be able to go back to their differential backup and pull out
# the correct version and fix the clock on the server. No data lost.
#
