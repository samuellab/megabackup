#!/usr/bin/env python

# Andy's MegaBackup script system
# 
# written by Andrew Leifer, leifer@fas.harvard.edu
# With code snippetts from Benjamin Schwartz, InnoboxDevices, Innobackup at 
#  http://github.com/InnoBox/innobackup
#  in file /overlay/usr/local/bin/innobox_perform_backup
#
#
# Given a desktop, a server and an external hard drive, this system will: 
#   - Make differential backups of directories from the server to the  external drive
#   - Make differential backups of directories on the desktop onto a secondary location on the desktop 
#   - Synchronize the server and the desktop
#	- Re-differential backup the server onto the external drive
#
#  These are the use cases I am interested in. 
#     There are two types of directories, "Data" directories that primarily reside on the server and 
#     are not used day to day and "Home" directories that a user will want easy access to on their local machine.
#
#   - "Data" added to the server from another machine should get propogated to the external backup drive. 
#
#   -  The "home" directory should always be up to date on the server so that a user may access their home directory
#      from their desktop, or off site and changes are propogated either way.
#
#   - Anything on the server should be backed up differentially. 
#
#
#  Q: Why are you making a differential backup of the users "home" directories rom one location on the
#     desktop to another location also on the desktop? This seems stupid.
# 
#  A: I am worried that automaticly synchronizing the home directory with the server directory could lose data. For example,
# 	  the automatic synchronization will likely be based on time stamps. Imagine that a user regularly changes files on his/her
#     desktop and then the synchronization, when works properly propogates those changes to the server because they have a
#     new timestamp. If the server's clock gets out of whack, the server may appear to have newer versions of files then 
#     the desktop, and now the users changes are overwritten. BUT if the user also has a local differential backup, the user will
#     eventually figure out that their data is whack and they will be able to go back to their differential backup and pull out
#     the correct version and fix the clock on the server. No data lost.
#
#  There are two main parts to this script. An incremental backup utility and a synchronization/merge utility..
#
#   Requirements: 
#		rdiff-backup.exe from http://www.nongnu.org/rdiff-backup/
#  		unison.exe from http://www.cis.upenn.edu/~bcpierce/unison/
#       Python from http://www.python.org/download/

# Globals
# Note, use forward slashes even for windows.. 
RDIFF_BACKUP='C:/Windows/rdiff-backup.exe'
UNISON = 'C:/Program Files/Unison/Unison.exe'



server_home='//labnas1/andy/'
server_data='//stewart/DLP/'

desktop_home='C:/Documents and Settings/andy/My Documents/'
desktop_home_backup='D:/LocalBackup/'

external_drive_home='F:/MegaBackup/andy/'
external_drive_data='F:/MegaBackup/data/'

# List the directories you want to backup here, leave blank to backup all directories
Data_Directories=[]
Home_Directories=['Posters' ,'Presentations' ,'Proposals' ,'Publication','Graphics','ConferenceLogistics']


#Files to Ignore
ignore=['.unison', 'rdiff-backup-data', '.DS_STORE']

def path_exists(fpath):
	from os import access, F_OK, path
	print('Checking path: '+ path.normpath(fpath))
	return access(path.normpath(fpath), F_OK)

def log_error(errmsg):
	print('MegaBackup ERROR: '+errmsg)
	return
	
def sync(source,dest,pathlist,ignore):
	from os import path
	u_args=['-auto','-batch']#,'-times','-prefer','newer']# '-batch'
	u_paths=[]
	for each in pathlist:
		u_paths.extend(['-path', path.normpath(each)])
		
	u_ignore=[]
	for each in ignore:
		u_ignore.extend(['-ignore', 'Name '+path.normpath(each)])
	cmd = [path.normpath(UNISON),path.normpath(source),path.normpath(dest)]+u_args+u_ignore+u_paths
	from subprocess import Popen
	p 	= Popen(cmd)
	p.communicate() #wait for sync to finish
	return p.returncode == 0
	

def rdiff_backup(source,target,include,ignore):
	from os import path

	rdiff_exclude=[]
	if len(ignore)>0:
		for each in ignore:
			print(each)
			rdiff_exclude.extend(['--exclude', '**'+path.normpath(each)])
	
	#OK. THere are two cases. The case where we have are specifying a list of folders to include
	# And the case where we are just copying everythiung in the subdirectory
	if len(include)>0:
		rdiff_include=[]
		for each in include:
			rdiff_include.extend(['--include', '**'+path.normpath(each)])
		if len(ignore)>0:
			cmd = [RDIFF_BACKUP,'-v','9'] +rdiff_include + rdiff_exclude + ['--exclude','**', path.normpath(source),path.normpath(target)]
		else:
			cmd = [RDIFF_BACKUP,'-v','9'] +rdiff_include + ['--exclude','**', path.normpath(source),path.normpath(target)]
	else: # we should just copy everything
		if len(ignore)>0:
			cmd = [RDIFF_BACKUP,'-v','9'] + rdiff_exclude + [ path.normpath(source),path.normpath(target)]
		else:
			cmd = [RDIFF_BACKUP,'-v','9', path.normpath(source),path.normpath(target)]
	from subprocess import Popen
	p 	= Popen(cmd)
	p.communicate() #wait for backup to finish
	return p.returncode == 0
	
	
def do_backup(source,dest,path_list,ignore):
	if path_exists(dest) and path_exists(source):
		if rdiff_backup(source,dest,path_list,ignore):
			return True
		else:
			log_error('Backup from: '+source +' to: '+dest+' FAILED!')
	else:
		log_error('Path not found: '+source+' or '+dest)
		log_error(source+' not backed up')
	return False
	
	
print('Starting ..')
server_home_backup=0
desktop_home_backup=0

#Incrementally backup home directory from server to external drive
server_home_backup=do_backup(server_home,external_drive_home,Home_Directories,ignore)

exit()

	


	
if server_home_backup and desktop_home_backup:	
	sync(desktop_home,server_home,Home_Directories,ignore)
else:
	log_error('Desktop and server home directory sync not attempted.')
	