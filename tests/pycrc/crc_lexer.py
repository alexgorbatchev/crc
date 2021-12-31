#  pycrc -- parameterisable CRC calculation utility and C source code generator
#
#  Copyright (c) 2006-2013  Thomas Pircher  <tehpeh@gmx.net>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.


"""
Lexical analyzer for pycrc. This module is used internally by pycrc for the
macro processing and code generation.

A basic example of how the lexer is used:

    from crc_lexer import Lexer

    input_str = "the input string to parse"
    lex = Lexer()
    lex.set_str(input_str)
    while True:
        tok = lex.peek()
        if tok == lex.tok_EOF:
            break
        else:
            print("%4d: %s\n" % (tok, lex.text))
            lex.advance()
"""

from __future__ import print_function
import re


# Class Lexer
###############################################################################
class Lexer(object):
    """
    A lexical analyser base class.
    """
    # Tokens.
    tok_unknown     = 0
    tok_EOF         = 1
    tok_gibberish   = 10
    tok_identifier  = 11
    tok_block_open  = 12
    tok_block_close = 13
    tok_num         = 20
    tok_str         = 21
    tok_par_open    = 22
    tok_par_close   = 23
    tok_op          = 24
    tok_and         = 25
    tok_or          = 26

    # States of the lexer.
    state_gibberish = 0
    state_expr      = 1

    # Regular Expressions used by the parser.
    re_id = re.compile("^\\$[a-zA-Z][a-zA-Z0-9_-]*")
    re_num = re.compile("^(0[xX][0-9a-fA-F]+|[0-9]+)")
    re_op = re.compile("<=|<|==|!=|>=|>")
    re_str = re.compile("\"?([a-zA-Z0-9_-]+)\"?")


    # Class constructor
    ###############################################################################
    def __init__(self, input_str = ""):
        """
        The class constructor.
        """
        self.set_str(input_str)
        self.state = self.state_gibberish


    # function set_str
    ###############################################################################
    def set_str(self, input_str):
        """
        Set the parse input string.
        """
        self.input_str = input_str
        self.text = ""
        self.next_token = None


    # function peek
    ###############################################################################
    def peek(self):
        """
        Return the next token, without taking it away from the input_str.
        """
        if self.next_token == None:
            self.next_token = self._parse_next()
        return self.next_token


    # function advance
    ###############################################################################
    def advance(self, skip_nl = False):
        """
        Discard the current symbol from the input stream and advance to the
        following characters.  If skip_nl is True, then skip also a following
        newline character.
        """
        self.next_token = None
        if skip_nl and  len(self.input_str) > 1 and self.input_str[0] == "\n":
            self.input_str = self.input_str[1:]


    # function delete_spaces
    ###############################################################################
    def delete_spaces(self, skip_unconditional = True):
        """
        Delete spaces in the input string.
        If skip_unconditional is False, then skip the spaces only if followed
        by $if() $else() or $elif().
        """
        new_input = self.input_str.lstrip(" \t")

        # check for an identifier
        m = self.re_id.match(new_input)
        if m != None:
            text = m.group(0)[1:]
            # if the identifier is a reserved keyword, skip the spaces.
            if (text == "if" or text == "elif" or text == "else"):
                skip_unconditional = True
        if skip_unconditional:
            self.next_token = None
            self.input_str = new_input


    # function prepend
    ###############################################################################
    def prepend(self, in_str):
        """
        Prepend the parameter to to the input string.
        """
        self.input_str = in_str + self.input_str


    # function set_state
    ###############################################################################
    def set_state(self, new_state):
        """
        Set the new state for the lexer.
        This changes the behaviour of the lexical scanner from normal operation
        to expression scanning (within $if () expressions) and back.
        """
        self.state = new_state
        self.next_token = None


    # function _parse_next
    ###############################################################################
    def _parse_next(self):
        """
        Parse the next token, update the state variables and take the consumed
        text from the imput stream.
        """
        if len(self.input_str) == 0:
            return self.tok_EOF

        if self.state == self.state_gibberish:
            return self._parse_gibberish()
        if self.state == self.state_expr:
            return self._parse_expr()
        return self.tok_unknown


    # function _parse_gibberish
    ###############################################################################
    def _parse_gibberish(self):
        """
        Parse the next token, update the state variables and take the consumed
        text from the imput stream.
        """
        # check for an identifier
        m = self.re_id.match(self.input_str)
        if m != None:
            self.text = m.group(0)[1:]
            self.input_str = self.input_str[m.end():]
            return self.tok_identifier

        if len(self.input_str) > 1:
            # check for "{:"
            if self.input_str[0:2] == "{:":
                self.text = self.input_str[0:2]
                self.input_str = self.input_str[2:]
                return self.tok_block_open
            # check for ":}"
            if self.input_str[0:2] == ":}":
                self.text = self.input_str[0:2]
                self.input_str = self.input_str[2:]
                return self.tok_block_close
            # check for "$$"
            if self.input_str[0:2] == "$$":
                self.text = self.input_str[0:1]
                self.input_str = self.input_str[2:]
                return self.tok_gibberish
            # check for malformed "$"
            if self.input_str[0] == "$":
                self.text = self.input_str[0:1]
                return self.tok_unknown

        # the character is gibberish.
        # find the position of the next special character.
        pos = self.input_str.find("$")
        tmp = self.input_str.find("{:")
        if pos < 0 or (tmp >= 0 and tmp < pos):
            pos = tmp
        tmp = self.input_str.find(":}")
        if pos < 0 or (tmp >= 0 and tmp < pos):
            pos = tmp

        if pos < 0 or len(self.input_str) == 1:
            # neither id nor block start nor block end found:
            # the whole text is just gibberish.
            self.text = self.input_str
            self.input_str = ""
        else:
            self.text = self.input_str[:pos]
            self.input_str = self.input_str[pos:]
        return self.tok_gibberish


    # function _parse_expr
    ###############################################################################
    def _parse_expr(self):
        """
        Parse the next token, update the state variables and take the consumed
        text from the imput stream.
        """
        # skip whitespaces
        pos = 0
        while pos < len(self.input_str) and self.input_str[pos] == ' ':
            pos = pos + 1
        if pos > 0:
            self.input_str = self.input_str[pos:]

        if len(self.input_str) == 0:
            return self.tok_EOF

        m = self.re_id.match(self.input_str)
        if m != None:
            self.text = m.group(0)[1:]
            self.input_str = self.input_str[m.end():]
            return self.tok_identifier

        m = self.re_num.match(self.input_str)
        if m != None:
            self.text = m.group(0)
            self.input_str = self.input_str[m.end():]
            return self.tok_num

        m = self.re_op.match(self.input_str)
        if m != None:
            self.text = m.string[:m.end()]
            self.input_str = self.input_str[m.end():]
            return self.tok_op

        if self.input_str[:4] == "and ":
            self.text = "and"
            self.input_str = self.input_str[len(self.text) + 1:]
            return self.tok_and

        if self.input_str[:3] == "or ":
            self.text = "or"
            self.input_str = self.input_str[len(self.text) + 1:]
            return self.tok_or

        m = self.re_str.match(self.input_str)
        if m != None:
            self.text = m.group(1)
            self.input_str = self.input_str[m.end():]
            return self.tok_str

        if self.input_str[0] == "(":
            self.text = self.input_str[0]
            self.input_str = self.input_str[len(self.text):]
            return self.tok_par_open

        if self.input_str[0] == ")":
            self.text = self.input_str[0]
            self.input_str = self.input_str[len(self.text):]
            return self.tok_par_close

        return self.tok_unknown
