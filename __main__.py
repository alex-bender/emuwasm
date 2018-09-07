#!/usr/bin/env python3
"""Web assembly emulator"""
import os
import cmd, sys


class WasmShell(cmd.Cmd):
    """The base class."""
    intro = "Let's play the game?\n"
    mode = 'read'
    prompt = '({}): '.format('bin')  # define some modes here 
    #style = # bin, s-type, c-like

    module = None

    def do_load(self, arg):
        if not arg:
            print('Provide module name')
        print('Loading file {}'.format(arg))

def run():
    """Launch main loop."""
    WasmShell().cmdloop()
    return 0

if __name__ == "__main__":
    os._exit(run())
