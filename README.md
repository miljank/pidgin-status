pidgin-status
=============

A python script that sets Pidgin status message

How to run program
==================

pidgin_status.py -m 'My new status message'                   # sets status to '-> My new status message'
pidgin_status.py -s 'My Favorite Band - My Favorite Song'     # sets status to '_| My Favorite Band - My Favorite Song'
pidgin_status.py -f /home/myself/quote/my_favorite_quotes.txt # sets message to a random line from the specified file

Daemon mode
=============

'-d' argument specifies that program should run in daemon mode. This means the program will go in background
and periodically change your status message. This is most useful with '-f' option (see above).

Additionally you can specify the time interval in which the status can be changed.
'-t 5' will change status every 5 minutes. Default time interval is 10 minutes.

To change message every 15 minutes to a random line from file /home/me/file.txt you would need to run this command.
pidgin_status.py -d -t 15 -f /home/me/file.txt

You can kill the daemon by running the program with '--stop' argument.
piding_status.py --stop