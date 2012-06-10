#!/usr/bin/python

"""
=====================================================
=                                                   =
=  D-BUS script for changing Piding status message  =
=                                                   =
=  v.4 / 2008-10-04 / Miljan Karadzic               =
=  WWW:    http://www.miljan.org/                   =
=  E-Mail: miljank@gmail.com                        =
=                                                   =
=  Released free under "I Don't Care" license       =
=                                                   =
=====================================================
"""

import os
import sys
import dbus
from   time import sleep
from   random import randint
from   optparse import OptionParser

# File where we store daemon PID
pid_file = "/var/tmp/pidgin_status.pid"

# Initialize command line parser
cmd_line = OptionParser ()

"""
Function:
  set_cmd_line_opts()
    Sets and parses command line arguments
    If all necessary parameters are not set it 
    will print error message and exit.
In:
  N/A
Out:
  opt
    Command line arguments
Calls:
  N/A
"""
def set_cmd_line_opts ():
    cmd_line.add_option ("-m", "--message", dest="message", help="Status message.")
    cmd_line.add_option ("-s", "--song",    dest="song", help="Set status to song name.")
    cmd_line.add_option ("-f", "--file",    dest="file", help="File from which we read random line.")
    cmd_line.add_option ("-d", "--daemon",  action="store_true", dest="daemon", default=False, help="Run program in the background.")
    cmd_line.add_option ("-t", "--time",    type="int", dest="time", default="10", help="Time frame for changing the status (in minutes).")
    cmd_line.add_option ("--stop",          action="store_true", dest="stop", default=False, help="Stop daemon.")
    
    (opt, args) = cmd_line.parse_args ()

    # Check if we have all necessary arguments
    if not opt.message and not opt.song and not opt.file and not opt.stop:
        cmd_line.error ("This program requires arguments. Please use -h for help.\n")
    opt.time = opt.time * 60

    if opt.file and not opt.file.startswith('/'):
        opt.file = os.path.join(os.getcwd(), opt.file)

    return opt

"""
Function:
  get_dbus()
    We need pidgin D-BUS session and objects in order 
    to change status message.
In:
  N/A
Out:
  purple
    Pidgin D-BUS object
Calls:
  N/A
"""
def get_dbus ():
    bus = dbus.SessionBus()
    obj = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
    purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

    return purple

"""
Function:
  pidgin_status()
    Sets new status message.
    It uses old message type (available, away, etc) and sets new message.
In:
  message
    New message
  icon
    Icon type (music note or arrow)
  putple
    Pidgin D-BUS object
Out:
  N/A
Calls:
  N/A
"""
def pidgin_status(message, icon, purple):
    old_status = purple.PurpleSavedstatusGetCurrent()               # get current status
    status_type = purple.PurpleSavedstatusGetType(old_status)       # get current status type
    new_status = purple.PurpleSavedstatusNew("", status_type)       # create new status with old status type
    purple.PurpleSavedstatusSetMessage(new_status, icon + message)  # fill new status with status message
    purple.PurpleSavedstatusActivate(new_status)                    # activate new status

"""
Function:
  start_daemon()
    Detaches from the console and creates a standalone daemon.
    We need to fork two times to avoid creating zombie processes.
    PID number is written into the pid_file so we can easily stop the daemon latter.
In:
  N/A
Out:
  N/A
Calls:
  N/A
"""
def start_daemon ():
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0) 
    except OSError, e: 
        sys.stderr.write("Fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)


    os.chdir("/") 
    os.setsid() 
    os.umask(0) 
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0) 
    except OSError, e: 
        sys.stderr.write("Fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1) 

    f = open (pid_file, "w")
    f.write (str(os.getpid()))
    f.close ()
    print "Daemon started."
    return (True)

"""
Function:
  stop_daemon()
    Reads PID from pid_file and tries to kill the daemon process.
In:
  N/A
Out:
  Bool
Calls:
  N/A
"""
def stop_daemon ():
    try:
        f = open (pid_file, "r")
        pid = f.readline ()
        f.close ()
    except IOError:
        print "PID file empty. Aborting..."
        return (False)

    try:
        i = os.kill (int(pid), 15)
        if i == None:
            os.remove (pid_file)
            print "Daemon stopped."
            return (True)

        print "Could not stop daemon."
        return (False)
    except:
        os.remove (pid_file)
        print "PID doesn't exist. Aborting..."
        return (False)

"""
Function:
  get_quote()
    Reads file, finds and returns random line
In:
  file
    File from which we should get the status message
Out:
  quote
    Random line from file
Calls:
  N/A
"""
def get_quote(file):                # function reads a file and gets random line
    num_lines = 0
    rand_line = 0
    l = 0

    if os.path.isfile(file):        # is file really there
        f = open(file, "r")         # open the file
        for line in f:              # go through the file and count the lines
            num_lines += 1
    else:
        sys.exit(1)

    rand_line = randint(0, num_lines - 1) # get the random line
    f.seek(0)                             # go to the begining of the file
    for line in f:                        # loop on the file till we get to the correct line
        if l == rand_line:                # if line correct
            quote = line.strip()          # get the line content
            break
        else:
            l += 1

    f.close()                             # close the file and return the line
    return quote

"""
Function:
  set_status()
    Determains what kind of message we need to set
      - Song
      - Quote from file
      - "Normal" message
    and according to this sets proper icon and message value.
In:
  purple
    Pidgin D-BUS object
Out:
  N/A
Calls:
  pidgin_status()
    Function for setting the pidgin status message
"""
def set_status(purple):
    if opt.message:
        icon = u'\u21e8 '
        msg = opt.message
    elif opt.song:
        icon = u'\u266C '
        msg = opt.song
    elif opt.file:
        icon = u'\u21e8 '
        msg = get_quote (opt.file)

    pidgin_status (msg, icon, purple)

# Main program
if __name__ == "__main__":
    # Get command line options
    opt = set_cmd_line_opts ()

    # Get pidgin D-BUS session
    purple = get_dbus ()

    # Are we are called to stop the daemon?
    if opt.stop:
        # Stop the daemon and exit
        if stop_daemon ():
            sys.exit (0)
        else:
            sys.exit (17)

    # Should we go to daemon mode?
    if opt.daemon and start_daemon():
        # If yes, loop to infinity
        while (1):
            # Set new status
            set_status (purple)
            # and wait for the required time
            sleep (opt.time)
    # If not in daemon mode just set the status and exit
    else:
        set_status (purple)