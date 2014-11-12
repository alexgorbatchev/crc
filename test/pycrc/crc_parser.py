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
Macro Language parser for pycrc.
use as follows:

    import sys
    from crc_opt import Options
    from crc_parser import MacroParser, ParseError

    opt = Options()
    opt.parse(sys.argv[1:])
    mp = MacroParser(opt)
    if mp.parse("Test 1 2 3"):
        print(mp.out_str)
"""

from crc_symtable import SymbolTable, SymbolLookupError
from crc_lexer import Lexer
import re
import sys


# Class ParseError
###############################################################################
class ParseError(Exception):
    """
    The exception class for the parser.
    """

    # Class constructor
    ###############################################################################
    def __init__(self, reason):
        self.reason = reason

    # function __str__
    ###############################################################################
    def __str__(self):
        return self.reason


# Class MacroParser
###############################################################################
class MacroParser(object):
    """
    The macro language parser and code generator class.
    """
    re_is_int = re.compile("^[-+]?[0-9]+$")
    #re_is_hex = re.compile("^(0[xX])?[0-9a-fA-F]+$")
    re_is_hex = re.compile("^0[xX][0-9a-fA-F]+$")


    # Class constructor
    ###############################################################################
    def __init__(self, opt):
        self.opt = opt
        self.sym = SymbolTable(opt)
        self.out_str = None
        self.lex = Lexer()

    # function parse
    #
    # The used grammar is:
    # data:           /* empty */
    #               | data GIBBERISH
    #               | data IDENTIFIER
    #               | data '{:' data ':}'
    #               | data if_block
    #               ;
    # 
    # if_block:     IF '(' exp_or ')' '{:' data ':}' elif_blocks else_block
    #               ;
    # 
    # elif_blocks:    /* empty */
    #               | elif_blocks ELIF '(' exp_or ')' '{:' data ':}'
    #               ;
    # 
    # else_block:     /* empty */
    #               | ELSE '{:' data ':}'
    #               ;
    # 
    # exp_or:         exp_and
    #               | exp_or TOK_OR exp_and
    #               ;
    # 
    # exp_and:        term
    #               | exp_and TOK_AND exp_comparison
    #               ;
    # 
    # exp_comparison: term TOK_COMPARISON term
    #               ;
    # 
    # term:           LITERAL
    #               | IDENTIFIER
    #               | '(' exp_or ')'
    #               ;
    ###############################################################################
    def parse(self, in_str):
        """
        Parse a macro string.
        """
        self.lex.set_str(in_str)
        self.out_str = ""
        self._parse_data(do_print = True)

        tok = self.lex.peek()
        if tok != self.lex.tok_EOF:
            raise ParseError("%s: error: misaligned closing block '%s'" % (sys.argv[0], self.lex.text))


    # function _parse_data
    ###############################################################################
    def _parse_data(self, do_print):
        """
        Private top-level parsing function.
        """
        tok = self.lex.peek()
        while tok != self.lex.tok_EOF:
            if tok == self.lex.tok_gibberish:
                self._parse_gibberish(do_print)
            elif tok == self.lex.tok_block_open:
                self._parse_data_block(do_print)
            elif tok == self.lex.tok_identifier and self.lex.text == "if":
                self._parse_if_block(do_print)
            elif tok == self.lex.tok_identifier:
                self._parse_identifier(do_print)
            elif tok == self.lex.tok_block_close:
                return
            else:
                raise ParseError("%s: error: wrong token '%s'" % (sys.argv[0], self.lex.text))
            tok = self.lex.peek()


    # function _parse_gibberish
    ###############################################################################
    def _parse_gibberish(self, do_print):
        """
        Parse gibberish.
        Actually, just print the characters in 'text' if do_print is True.
        """
        if do_print:
            self.out_str = self.out_str + self.lex.text
        self.lex.advance()


    # function _parse_identifier
    ###############################################################################
    def _parse_identifier(self, do_print):
        """
        Parse an identifier.
        """
        try:
            sym_value = self.sym.getTerminal(self.lex.text)
        except SymbolLookupError:
            raise ParseError("%s: error: unknown terminal '%s'" % (sys.argv[0], self.lex.text))
        self.lex.advance()
        if do_print:
            self.lex.prepend(sym_value)


    # function _parse_if_block
    ###############################################################################
    def _parse_if_block(self, do_print):
        """
        Parse an if block.
        """
        # parse the expression following the 'if' and the associated block.
        exp_res = self._parse_conditional_block(do_print)
        do_print = do_print and not exp_res

        # try $elif
        tok = self.lex.peek()
        while tok == self.lex.tok_identifier and self.lex.text == "elif":
            exp_res = self._parse_conditional_block(do_print)
            do_print = do_print and not exp_res
            tok = self.lex.peek()

        # try $else
        if tok == self.lex.tok_identifier and self.lex.text == "else":
            # get rid of the tok_identifier, 'else' and following spaces
            self.lex.advance()
            self.lex.delete_spaces()

            # expect a data block
            self._parse_data_block(do_print)



    # function _parse_conditional_block
    ###############################################################################
    def _parse_conditional_block(self, do_print):
        """
        Parse a conditional block (such as $if or $elif).
        Return the truth value of the expression.
        """
        # get rid of the tok_identifier, 'if' or 'elif'
        self.lex.advance()
        self.lex.set_state(self.lex.state_expr)

        # expect an open parenthesis
        tok = self.lex.peek()
        if tok != self.lex.tok_par_open:
            raise ParseError("%s: error: open parenthesis expected: '%s'" % (sys.argv[0], self.lex.text))
        self.lex.advance()

        # parse the boolean expression
        exp_res = self._parse_exp_or()

        # expect a closed parenthesis
        tok = self.lex.peek()
        if tok != self.lex.tok_par_close:
            raise ParseError("%s: error: closed parenthesis expected: '%s'" % (sys.argv[0], self.lex.text))
        self.lex.advance()

        # get rid of eventual spaces, and switch back to gibberish.
        self.lex.delete_spaces()
        self.lex.set_state(self.lex.state_gibberish)

        # expect a data block
        self._parse_data_block(do_print and exp_res)

        # get rid of eventual spaces
        # but only if followed by $if, $else or $elif
        self.lex.delete_spaces(skip_unconditional = False)

        return exp_res


    # function _parse_data_block
    ###############################################################################
    def _parse_data_block(self, do_print):
        """
        Parse a data block.
        """
        # expect an open block
        tok = self.lex.peek()
        if tok != self.lex.tok_block_open:
            raise ParseError("%s: error: open block expected: '%s'" % (sys.argv[0], self.lex.text))
        self.lex.advance(skip_nl = True)

        # more data follows...
        self._parse_data(do_print)

        # expect a closed block
        tok = self.lex.peek()
        if tok != self.lex.tok_block_close:
            raise ParseError("%s: error: closed block expected: '%s'" % (sys.argv[0], self.lex.text))
        self.lex.advance(skip_nl = True)


    # function _parse_exp_or
    ###############################################################################
    def _parse_exp_or(self):
        """
        Parse a boolean 'or' expression.
        """
        ret = False
        while True:
            ret = self._parse_exp_and() or ret

            # is the expression terminated?
            tok = self.lex.peek()
            if tok == self.lex.tok_par_close:
                return ret
            # expect an 'or' token.
            elif tok == self.lex.tok_or:
                self.lex.advance()
            # everything else is the end of the expression.
            # Let the caling function worry about error reporting.
            else:
                return ret
        return False


    # function _parse_exp_and
    ###############################################################################
    def _parse_exp_and(self):
        """
        Parse a boolean 'and' expression.
        """
        ret = True
        while True:
            ret = self._parse_exp_comparison() and ret

            # is the expression terminated?
            tok = self.lex.peek()
            if tok == self.lex.tok_par_close:
                return ret
            # expect an 'and' token.
            elif tok == self.lex.tok_and:
                self.lex.advance()
            # everything else is a parse error.
            else:
                return ret
        return False


    # function _parse_exp_comparison
    ###############################################################################
    def _parse_exp_comparison(self):
        """
        Parse a boolean comparison.
        """
        # left hand side of the comparison
        lhs = self._parse_exp_term()

        # expect a comparison
        tok = self.lex.peek()
        if tok != self.lex.tok_op:
            raise ParseError("%s: error: operator expected: '%s'" % (sys.argv[0], self.lex.text))
        operator = self.lex.text
        self.lex.advance()

        # right hand side of the comparison
        rhs = self._parse_exp_term()

        # if both operands ar numbers, convert them
        num_l = self._get_num(lhs)
        num_r = self._get_num(rhs)
        if num_l != None and num_r != None:
            lhs = num_l
            rhs = num_r

        # now calculate the result of the comparison, whatever that means
        if operator == "<=":
            ret = lhs <= rhs
        elif operator == "<":
            ret = lhs < rhs
        elif operator == "==":
            ret = lhs == rhs
        elif operator == "!=":
            ret = lhs != rhs
        elif operator == ">=":
            ret = lhs >= rhs
        elif operator == ">":
            ret = lhs > rhs
        else:
            raise ParseError("%s: error: unknow operator: '%s'" % (sys.argv[0], self.lex.text))
        return ret


    # function _parse_exp_term
    ###############################################################################
    def _parse_exp_term(self):
        """
        Parse a terminal.
        """
        tok = self.lex.peek()

        # identifier
        if tok == self.lex.tok_identifier:
            try:
                ret = self.sym.getTerminal(self.lex.text)
            except SymbolLookupError:
                raise ParseError("%s: error: unknown terminal '%s'" % (sys.argv[0], self.lex.text))
            if ret == None:
                ret = "Undefined"
        # string
        elif tok == self.lex.tok_str:
            ret = self.lex.text
        # number
        elif tok == self.lex.tok_num:
            ret = self.lex.text
        # parenthesised expression
        elif tok == self.lex.tok_par_open:
            self.lex.advance()
            ret = self._parse_exp_or()
            tok = self.lex.peek()
            if tok != self.lex.tok_par_close:
                raise ParseError("%s: error: closed parenthesis expected: '%s'" % (sys.argv[0], self.lex.text))
        self.lex.advance()
        return ret


    # function _get_num
    ###############################################################################
    def _get_num(self, in_str):
        """
        Check if in_str is a number and return the numeric value.
        """
        ret = None

        if in_str != None:
            m = self.re_is_int.match(in_str)
            if m != None:
                ret = int(in_str)

            m = self.re_is_hex.match(in_str)
            if m != None:
                ret = int(in_str, 16)

        return ret
