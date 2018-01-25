import sys
from dbm import error as dbmError
from notes import *


def main(args):
    arg_len = len(args)-1

    if arg_len > 5 or arg_len == 0:
        return -1

    if args[1] == "-n" or args[1] == "--note":

        if arg_len == 3:
            new_note(args[2], args[3])
        elif arg_len == 5 and (args[4] == "-p" or args[4] == "--encrypt"):
            cipher = AESCipher(args[5])
            new_note(args[2], cipher.encrypt(args[3]))
        elif arg_len == 4 and (args[3] == "-u" or args[3] == "--decrypt"):
            cipher = AESCipher(args[4])
            cipher.decrypt(args[2])
        else:
            return -1

#    elif args[1] == "-r" or args[1] == "--remainder":
#        if arg_len != 5:
#            return -1

    elif args[1] == "-l" or args[1] == "--list":
        if arg_len != 1:
            return -1

        show_all_notes()

    elif args[1] == "-s" or args[1] == "--search":
        if arg_len != 2:
            return -1

        search_note(args[2])

    elif args[1] == "-d" or args[1] == "--delete":
        if arg_len != 2:
            return -1

        del_note(args[2])

    elif args[1] == "-D" or args[1] == "--delete-all":
        if arg_len != 1:
            return -1

        del_all()
    else:
        return -1

    return 0


if __name__ == "__main__":
    try:
        if main(sys.argv) == -1:
            nterm_usage()
    except FileNotFoundError:
        print("\nThere are no notes nor reminders available")
    except dbmError:
        print("\nThere are no notes nor reminders available")
