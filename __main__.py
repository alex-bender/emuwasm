#!/usr/bin/env python3
"""Web assembly emulator\debugger"""

import os
import cmd, sys
import logging
import tempfile
from subprocess import call
from textwrap import indent

# Because of the current filemode logs will be overwritten each every launch
logger_config = {
    'format': '%(asctime)s %(message)s',
    'filename': 'ew.log',
    'filemode': 'w',
    'level': logging.DEBUG
}
logging.basicConfig(**logger_config)
logger = logging.getLogger('ew')

sections = [
    'type',
    'import',
    'function',
    'table',
    'memory',
    'global',
    'export',
    'start',
    'element',
    'code',
    'data'
]

required_sections = [
    'type',
    'function',
    'code'
]

__NOTES = """
    * WebAssembly page size, which is fixed to 64KiB
    * All load and store operators use little-endian byte order when translating 
    between values and bytes.
    * Size of a memory is an even multiple of the memory-page size, which is 64 KiB
    

    TYPE:
        The type section contains a list of each unique function signature
    used throughout the module. This includes any signatures of imported
    functions. The position in the list is the type signature’s unique index
    within the module.

    (i32 i32 -> i32)  // func_type #0 (i64 -> i64)      // func_type #1
    ( -> )            // func_type #2


    IMPORT:
        The import section declares any external dependencies by listing
    module name, field name and type for each function, value or data required:

    ("dumb-math", "quadruple", (func_type 1))        // func #0
    ("dumb-math", "pi", (global_type i64 immutable))


    FUNCTION:
        The function section declares indexes for each function that is later
    defined in the code section, where the position in the list is the function’s
    index and the value its type. The effective function index starts at number
    of func_type imports, meaning that the effective list of functions available
    in the module is the import section list filtered on function imports joined
    by the function-section list.

    (func_type 1)  // func #1
    (func_type 1)  // func #2
    (func_type 0)  // func #3


    TABLE:
        The table section defines any number of tables.


    MEMORY:
        The memory section defines the optional memory of the module by defining
    its initial size and optionally how large it is expected to expand. The data
    section can be used to initialize the memory.


    GLOBAL:
        The global section declares any number of mutable or immutable global
    variables for the module.


    EXPORT:
        The export section declares any parts of the module that can be
    accessed by the host environment, not including the special start function.


    START:
        The start section designates a function index for a function to be
    called when the module is loading and is the mechanism that can be used
    to make a module an executable program, or used to dynamically initialize
    globals or memory of a module.


    ELEMENT:
        The element section allows a module to initialize the contents of
    a table imported from the outside or defined in the table section.


    CODE:
        The code section is probably the bulk of most WebAssembly modules
    as it defines all code for all functions in the module.

"""

class EmptyException(Exception):
    """Error attempting to access an element from an empty stack."""


class Stack():
    """LIFO Stack"""
    debug = False

    def __init__(self, debug=False):
        """Create an empty stack."""
        if self.debug:
            logger.info('Stack is initialized')
        self._data = []

    def __len__(self):
        """Return the number of elements in the stack."""
        return len(self._data)

    def is_empty(self):
        """Return True if stack is empty."""
        return len(self._data) == 0

    def push(self, e):
        """Add element to the stack."""
        self._data.append(e)

    def top(self):
        """Return the element at the top of the stack.

        Raise EmptyException if the stack is empty.
        """
        if self.is_empty():
            raise EmptyException('Stack is empty')
        return self._data[-1]

    def pop(self):
        """Remove and return the elemet from the top of the stack.

        Raise EmptyException if the stack is empty.
        """
        if self.is_empty():
            raise EmptyException('Stack is empty')
        return self._data.pop()


class WasmShell(cmd.Cmd):
    """The base class."""

    intro = "Let's play the game?\n"
    mode = 'read'
    prompt = '({}): '.format('...')  # define some modes here 
    #style = # bin, s-type, c-like

    module = None

    def _exit(self, exit_code=0):
        """Clean up and exit."""
        logger.debug('Going to exit')
        os._exit(exit_code)

    def cmdloop(self, intro=None):
        print(self.intro)
        while True:
            try:
                super().cmdloop(intro="")
            except KeyboardInterrupt:
                print("Exiting")
                self._exit()
            except Exception as exp:
                logger.debug(f'Got an exception {exp}')

    def do_init(self, arg):
        """Init new empty stack."""
        self.stack = Stack()

    # DEBUG
    def do_go(self, arg):
        os.system('clear') 
        self.do_init('')
        self.do_push(1)
        self.do_push(2)
        self.do_load('add.wat')
        self.do_inspect()
    # DEBUG

    def do_inspect(self, arg=None):
        """Print stack values."""
        for kv in enumerate(self.stack._data):
            print(kv[0], kv[1])
        stack_lenght = len(self.stack)
        print(f'Stack lengh is {stack_lenght}')
        print('Module code is:\n')
        if self.module:
            print(indent(self.module, '\t'))

    def do_load(self, fname):
        if not fname:
            print('Provide the file name where to read from')
        print('Loading file {}'.format(fname))
        with open(fname, 'r') as module:
            content = module.read()
        self.module = content

    def do_enter(self, arg=None):
        """Enter wasm code into editor."""
        EDITOR = os.getenv('EDITOR')
        with tempfile.NamedTemporaryFile(suffix=".roamer") as temp:
            # To fill the file beforehand
            # content = content.encode('utf-8')
            # temp.write(content)
            # temp.flush()
            exit_code = call(EDITOR.split() + [temp.name])
            if exit_code != 0:
                sys.exit()
            temp.seek(0)
            output = temp.read()
            output = output.decode('UTF-8')
        self.module = content

    def do_exit(self, arg):
        """Exit from shell."""
        self._exit(0)

    do_quit = do_exit

    def do_push(self, el):
        """Push element onto stack."""
        logger.debug(f'Going to push {el} onto stack')
        self.stack.push(el)

    def do_pop(self, arg=None):
        el = self.stack.pop()
        logger.debug(f'Got {el} from stack')
        return el

def run():
    """Launch main loop."""
    WasmShell().cmdloop()
    return 0

if __name__ == "__main__":
    os._exit(run())
