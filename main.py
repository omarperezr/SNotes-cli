from sys import argv
from notes import *


def main(args):
    arg_len = len(args)-1

    if arg_len > 5 or arg_len == 0:
        return -1

    if args[1] in ("-n", "--note"):

        if arg_len == 3:
            new_note(args[2], args[3])
        elif arg_len == 5 and args[4] in ("-p", "--encrypt"):
            cipher = AESCipher(args[5])
            new_note(args[2], cipher.encrypt(args[3]))
        elif arg_len == 4 and args[3] in ("-u", "--decrypt"):
            cipher = AESCipher(args[4])
            cipher.decrypt(args[2])
        else:
            return -1

    elif args[1] in ("-m", "--modify"):
        if arg_len != 2:
            return -1

        modify_note(args[2])

    elif args[1] in ("-l", "--list"):
        if arg_len != 1:
            return -1

        show_all_notes()

    elif args[1] in ("-s", "--search"):
        if arg_len != 2:
            return -1

        search_note(args[2])

    elif args[1] in ("-d", "--delete"):
        if arg_len != 2:
            return -1

        del_note(args[2])

    elif args[1] in ("-D", "--delete-all"):
        if arg_len != 1:
            return -1

        del_all()
    else:
        return -1

    return 0


if __name__ == "__main__":
    try:
        if main(argv) == -1:
            usage()
    except FileNotFoundError:
        print("\nThere are no notes nor reminders available")
    except dbmError:
        print("\nThere are no notes nor reminders available")
