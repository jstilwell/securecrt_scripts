# $language = "python"
# $interface = "1.0"

"""
screen-manager.py
Jesse Stilwell <jesse.stilwell@gmail.com>

A SecureCRT script to help make screen easier to use and
also sets any new screens to self destruct to cut down on
orphaned screens.

Usage:

Bind to a hotkey or button in SecureCRT.

NOTE: If you don't want to run the screen as root (I usually need to) then  find the comment below:

# Remove sudo from the line below to run this screen as a regular user.

And remove sudo from the line below it.

"""

import datetime

# User defined variables you should change
expire_in = '7 days'  # minutes/hours/days/weeks/months/years
initials = 'js'  # Your initials for screen title prefix
default_name = 'random'  # Default screen name if none is supplied.

# Other variables you shouldn't change
tab = crt.GetScriptTab()
tab.Screen.Synchronous = True
tab.Screen.IgnoreEscape = True
bash_prompts = ['$ ', '# ']
tday = datetime.datetime.now()
tday = tday.strftime('_%m%d%Y')

# Check to make sure script is being run in an active session.
if not tab.Session.Connected:
    usage = "\n".join([
        "Error.",
        "This script was designed to be launched after a valid ",
        "connection is established.",
        "Please connect to a remote machine before running this script."])
    crt.Dialog.MessageBox(usage)


def clean_list(astring):
    """
    Strips everything out of the screen -ls output except for the screen_id.name
    :param astring:
    :return:
    """

    stripped = ' '.join(astring.split())
    stripped = stripped.replace(" (Detached) ", "\n")
    stripped = stripped.replace(" (Attached) ", "\n")
    cleaned = stripped.split("[")[0]

    return cleaned.split('\n')


def find_sid(schoice, spos):
    """
    Strip out everything but screen ID so we can use it to attach.
    :return:
    """

    x = schoice[spos].split('.')[0][3:]
    return str(x)


def screen_attach(screen_id):
    """
    Takes the screen ID chosen from screen_menu() and attaches to it.
    :param screen_id:
    :return:
    """

    scmd = 'sudo screen -rx '
    tab.Screen.Send(scmd + screen_id + '\r\n')


def screen_create():
    """
    If no choice passed by user in screen_menu(), we need to create a new screen.
    :return:
    """
    # echo "screen -S SCREEN_NAME -X quit" | at now + 1 minute
    in_name = crt.Dialog.Prompt('Create screen with name: \n(Leave blank for default or Q to quit.)')

    # If no name is supplied, set in_name var to user defined default name + timestamp.
    if in_name == '':
        in_name = default_name + tday
    elif in_name == 'q':
        return
    else:
        pass

    # Build commands to create screen and self destruct w/ user input & user defined variables.
    nuke_it = 'echo "screen -S {}_{} -X quit" | at now + {}'.format(initials, in_name.replace(' ', '_'), expire_in)
    # Remove sudo from the line below to run this screen as a regular user.
    to_create = 'sudo screen -S {}_{}'.format(initials, in_name.replace(' ', '_'))
    # Names with periods break the script, so we replace with underscores.
    nuke_it = nuke_it.replace('.', '_')
    to_create = to_create.replace('.', '_')
    # Create screen and self destruct timer.
    tab.Screen.Send(to_create)
    tab.Screen.Send(chr(13))
    tab.Screen.Send(nuke_it)
    tab.Screen.Send(chr(13))

    return


def screen_menu(screen_name):
    """
    Uses the list of screens from the terminal to create a menu of choices for the user.
    :param screen_name:
    :return:
    """

    screens = []
    # Turn list of screens into numbered list of screens.
    for snum, sname in enumerate(screen_name):
        screens.append(str(snum+1) + ") " + "".join(sname))
    # If there aren't any screens, create a new one.
    if len(screens) == 0:
        screen_create()
    else:
        schoice = crt.Dialog.Prompt('SELECTION:\n\n0) NEW SCREEN (or blank)\n' + '\n'.join(screens), "Screen Manager")

        # Get length of tuple for number of screens and +1 to offset index.
        ns = len(screens) + 1

        # User menu selections
        if schoice == "":
            screen_create()
        if schoice == "0":
            screen_create()
        # Limit choices to dynamic range based on length of screen list.
        elif schoice > "0" and schoice < str(ns):
            x = int(schoice) - 1
            screen_attach(find_sid(screens, x))
        else:
            if schoice == "":
                pass
            else:
                crt.Dialog.MessageBox('Invalid choice')


def main():

    screen_ls = "sudo screen -ls | grep '^\s'"
    tab.Screen.Send(screen_ls + '\r\n')
    tab.Screen.WaitForString(screen_ls + '\r\n')
    ls_results = tab.Screen.ReadString(bash_prompts)

    # Sudu
    if 'password' in ls_results:
        # Re-run main() if sudo needs a password because SecureCRT is wonky.
        main()
    else:
        list_out = clean_list(ls_results)
        list_out = filter(None, list_out)
        screen_menu(list_out)


main()
