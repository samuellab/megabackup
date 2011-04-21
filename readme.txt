A simple backup script to be run on a windows desktop that synchronizes and differentially backs up a desktop, a network storage device and an external hard drive. Data can be injected into either the network storage device or the desktop and changes will be synchronized and propogated in such a way that data should not be lost or overwritten.

Under the hood this scrip uses python, rdiff-backup and unison.

See megabackup.py for details.
