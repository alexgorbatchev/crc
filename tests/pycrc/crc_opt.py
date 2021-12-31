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
Option parsing library for pycrc.
use as follows:

   from crc_opt import Options

   opt = Options()
   opt.parse(sys.argv[1:])
"""

from optparse import OptionParser, Option, OptionValueError
from copy import copy
import sys
from crc_models import CrcModels


# Class Options
###############################################################################
class Options(object):
    """
    The options parsing and validating class.
    """

    # Program details
    ProgramName    = "pycrc"
    Version        = "0.8.1"
    VersionStr     = "%s v%s" % (ProgramName, Version)
    WebAddress     = "http://www.tty1.net/pycrc/"

    # Bitmap of the algorithms
    Algo_None               = 0x00
    Algo_Bit_by_Bit         = 0x01
    Algo_Bit_by_Bit_Fast    = 0x02
    Algo_Bitwise_Expression = 0x04
    Algo_Table_Driven       = 0x08

    Action_Check_String     = 0x01
    Action_Check_Hex_String = 0x02
    Action_Check_File       = 0x03
    Action_Generate_H       = 0x04
    Action_Generate_C       = 0x05
    Action_Generate_C_Main  = 0x06
    Action_Generate_Table   = 0x07


    # Class constructor
    ###############################################################################
    def __init__(self):
        self.Width          = None
        self.Poly           = None
        self.ReflectIn      = None
        self.XorIn          = None
        self.ReflectOut     = None
        self.XorOut         = None
        self.TableIdxWidth  = 8
        self.TableWidth     = 1 << self.TableIdxWidth
        self.Verbose        = False
        self.CheckString    = "123456789"
        self.MSB_Mask       = None
        self.Mask           = None

        self.Algorithm      = self.Algo_None
        self.SymbolPrefix   = "crc_"
        self.CrcType        = None
        self.IncludeFiles   = []
        self.OutputFile     = None
        self.Action         = self.Action_Check_String
        self.CheckFile      = None
        self.CStd           = None
        self.UndefinedCrcParameters = False


    # function parse
    ###############################################################################
    def parse(self, argv = None):
        """
        Parses and validates the options given as arguments
        """
        usage = """\
python %prog [OPTIONS]

To calculate the checksum of a string or hexadecimal data:
    python %prog [model] --check-string "123456789"
    python %prog [model] --check-hexstring "313233343536373839"

To calculate the checksum of a file:
    python %prog [model] --check-file filename

To generate the C source code and write it to filename:
    python %prog [model] --generate c -o filename

The model can be defined either with the --model switch or by specifying each
of the following parameters:
    --width --poly --reflect-in --xor-in --reflect-out --xor-out"""

        models = CrcModels()
        model_list = ", ".join(models.getList())
        parser = OptionParser(option_class=MyOption, usage=usage, version=self.VersionStr)
        parser.add_option("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="be more verbose; print the value of the parameters and the chosen model to stdout")
        parser.add_option("--check-string",
                        action="store", type="string", dest="check_string",
                        help="calculate the checksum of a string (default: '123456789')", metavar="STRING")
        parser.add_option("--check-hexstring",
                        action="store", type="string", dest="check_hexstring",
                        help="calculate the checksum of a hexadecimal number string", metavar="STRING")
        parser.add_option("--check-file",
                        action="store", type="string", dest="check_file",
                        help="calculate the checksum of a file", metavar="FILE")
        parser.add_option("--generate",
                        action="store", type="string", dest="generate", default=None,
                        help="generate C source code; choose the type from {h, c, c-main, table}", metavar="CODE")
        parser.add_option("--std",
                        action="store", type="string", dest="c_std", default="C99",
                        help="choose the C dialect of the generated code from {C89, ANSI, C99}", metavar="STD")
        parser.add_option("--algorithm",
                        action="store", type="string", dest="algorithm", default="all",
                        help="choose an algorithm from {bit-by-bit, bbb, bit-by-bit-fast, bbf, bitwise-expression, bwe, table-driven, tbl, all}", metavar="ALGO")
        parser.add_option("--model",
                        action="callback", callback=self.model_cb, type="string", dest="model", default=None,
                        help="choose a parameter set from {%s}" % model_list, metavar="MODEL")
        parser.add_option("--width",
                        action="store", type="hex", dest="width",
                        help="use NUM bits in the polynomial", metavar="NUM")
        parser.add_option("--poly",
                        action="store", type="hex", dest="poly",
                        help="use HEX as polynomial", metavar="HEX")
        parser.add_option("--reflect-in",
                        action="store", type="bool", dest="reflect_in",
                        help="reflect the octets in the input message", metavar="BOOL")
        parser.add_option("--xor-in",
                        action="store", type="hex", dest="xor_in",
                        help="use HEX as initial value", metavar="HEX")
        parser.add_option("--reflect-out",
                        action="store", type="bool", dest="reflect_out",
                        help="reflect the resulting checksum before applying the --xor-out value", metavar="BOOL")
        parser.add_option("--xor-out",
                        action="store", type="hex", dest="xor_out",
                        help="xor the final CRC value with HEX", metavar="HEX")
        parser.add_option("--table-idx-width",
                        action="store", type="int", dest="table_idx_width",
                        help="use NUM bits to index the CRC table; NUM must be one of the values {1, 2, 4, 8}", metavar="NUM")
        parser.add_option("--symbol-prefix",
                        action="store", type="string", dest="symbol_prefix",
                        help="when generating source code, use STRING as prefix to the exported C symbols", metavar="STRING")
        parser.add_option("--crc-type",
                        action="store", type="string", dest="crc_type",
                        help="when generating source code, use STRING as crc_t type", metavar="STRING")
        parser.add_option("--include-file",
                        action="append", type="string", dest="include_files",
                        help="when generating source code, include also FILE as header file; can be specified multiple times", metavar="FILE")
        parser.add_option("-o", "--output",
                        action="store", type="string", dest="output_file",
                        help="write the generated code to file instead to stdout", metavar="FILE")

        (options, args) = parser.parse_args(argv)

        undefined_params = []
        if options.width != None:
            self.Width = options.width
        else:
            undefined_params.append("--width")
        if options.poly != None:
            self.Poly = options.poly
        else:
            undefined_params.append("--poly")
        if options.reflect_in != None:
            self.ReflectIn = options.reflect_in
        else:
            undefined_params.append("--reflect-in")
        if options.xor_in != None:
            self.XorIn = options.xor_in
        else:
            undefined_params.append("--xor-in")
        if options.reflect_out != None:
            self.ReflectOut = options.reflect_out
        else:
            undefined_params.append("--reflect-out")
        if options.xor_out != None:
            self.XorOut = options.xor_out
        else:
            undefined_params.append("--xor-out")
        if options.table_idx_width != None:
            if options.table_idx_width == 1 or \
                    options.table_idx_width == 2 or \
                    options.table_idx_width == 4 or \
                    options.table_idx_width == 8:
                self.TableIdxWidth = options.table_idx_width
                self.TableWidth = 1 << options.table_idx_width
            else:
                sys.stderr.write("%s: error: unsupported table-idx-width %d\n" % (sys.argv[0], options.table_idx_width))
                sys.exit(1)

        if self.Width != None:
            if self.Width <= 0:
                sys.stderr.write("%s: error: Width must be strictly positive\n" % sys.argv[0])
                sys.exit(1)
            self.MSB_Mask = 0x1 << (self.Width - 1)
            self.Mask = ((self.MSB_Mask - 1) << 1) | 1
            if self.Poly != None:
                self.Poly = self.Poly & self.Mask
            if self.XorIn != None:
                self.XorIn = self.XorIn & self.Mask
            if self.XorOut != None:
                self.XorOut = self.XorOut & self.Mask
        else:
            self.MSB_Mask = None
            self.Mask = None

        if self.Width           == None or \
                self.Poly       == None or \
                self.ReflectIn  == None or \
                self.XorIn      == None or \
                self.ReflectOut == None or \
                self.XorOut     == None:
            self.UndefinedCrcParameters = True
        else:
            self.UndefinedCrcParameters = False

        if options.algorithm != None:
            alg = options.algorithm.lower()
            if alg in set(["bit-by-bit", "bbb", "all"]):
                self.Algorithm      |= self.Algo_Bit_by_Bit
            if alg in set(["bit-by-bit-fast", "bbf", "all"]):
                self.Algorithm      |= self.Algo_Bit_by_Bit_Fast
            if alg in set(["bitwise-expression", "bwe", "all"]):
                self.Algorithm      |= self.Algo_Bitwise_Expression
            if alg in set(["table-driven", "tbl", "all"]):
                self.Algorithm      |= self.Algo_Table_Driven
            if self.Algorithm == 0:
                sys.stderr.write("%s: error: unknown algorithm %s\n" % (sys.argv[0], options.algorithm))
                sys.exit(1)
        if self.Algorithm & self.Algo_Bitwise_Expression and self.UndefinedCrcParameters:
            if self.Algorithm == self.Algo_Bitwise_Expression:
                sys.stderr.write("Error: algorithm %s not applicable with undefined parameters\n" % options.algorithm)
                sys.exit(1)
            else:
                self.Algorithm &= ~(self.Algo_Bitwise_Expression)

        if options.c_std != None:
            std = options.c_std.upper()
            if std == "ANSI" or std == "C89":
                self.CStd = "C89"
            elif std == "C99":
                self.CStd = std
            else:
                sys.stderr.write("%s: error: unknown C standard %s\n" % (sys.argv[0], options.c_std))
                sys.exit(1)
        if options.symbol_prefix != None:
            self.SymbolPrefix = options.symbol_prefix
        if options.include_files != None:
            self.IncludeFiles = options.include_files
        if options.crc_type != None:
            self.CrcType = options.crc_type
        if options.output_file != None:
            self.OutputFile = options.output_file
        op_count = 0
        if options.check_string != None:
            self.Action         = self.Action_Check_String
            self.CheckString    = options.check_string
            self.Algorithm &= ~(self.Algo_Bitwise_Expression)
            op_count += 1
        if options.check_hexstring != None:
            self.Action         = self.Action_Check_Hex_String
            self.CheckString    = options.check_hexstring
            self.Algorithm &= ~(self.Algo_Bitwise_Expression)
            op_count += 1
        if options.check_file != None:
            self.Action         = self.Action_Check_File
            self.CheckFile      = options.check_file
            self.Algorithm &= ~(self.Algo_Bitwise_Expression)
            op_count += 1
        if options.generate != None:
            arg = options.generate.lower()
            if arg == 'h':
                self.Action = self.Action_Generate_H
            elif arg == 'c':
                self.Action = self.Action_Generate_C
            elif arg == 'c-main':
                self.Action = self.Action_Generate_C_Main
            elif arg == 'table':
                self.Action = self.Action_Generate_Table
            else:
                sys.stderr.write("%s: error: don't know how to generate %s\n" % (sys.argv[0], options.generate))
                sys.exit(1)
            op_count += 1

            if self.Action == self.Action_Generate_Table:
                if self.Algorithm & self.Algo_Table_Driven == 0:
                    sys.stderr.write("%s: error: the --generate table option is incompatible with the --algorithm option\n" % sys.argv[0])
                    sys.exit(1)
                self.Algorithm = self.Algo_Table_Driven
            elif self.Algorithm not in set([self.Algo_Bit_by_Bit, self.Algo_Bit_by_Bit_Fast, self.Algo_Bitwise_Expression, self.Algo_Table_Driven]):
                sys.stderr.write("%s: error: select an algorithm to be used in the generated file\n" % sys.argv[0])
                sys.exit(1)
        else:
            if self.TableIdxWidth != 8:
                sys.stderr.write("%s: warning: reverting to Table Index Width = 8 for internal CRC calculation\n" % sys.argv[0])
                self.TableIdxWidth = 8
                self.TableWidth = 1 << options.table_idx_width
        if op_count == 0:
            self.Action = self.Action_Check_String
        if op_count > 1:
            sys.stderr.write("%s: error: too many actions scecified\n" % sys.argv[0])
            sys.exit(1)

        if (self.Algorithm == self.Algo_Bitwise_Expression) and \
            (self.Action == self.Action_Check_String or self.Action == self.Action_Check_Hex_String or self.Action == self.Action_Check_File):
            sys.stderr.write("Error: algorithm %s is only applicable to generate source code\n" % options.algorithm)
            sys.exit(1)

        if len(args) != 0:
            sys.stderr.write("%s: error: unrecognized argument(s): %s\n" % (sys.argv[0], " ".join(args)))
            sys.exit(1)

        if self.UndefinedCrcParameters and self.Action in set((self.Action_Check_String, self.Action_Check_Hex_String, self.Action_Check_File, self.Action_Generate_Table)):
            sys.stderr.write("%s: error: undefined parameters: Add %s or use --model\n" % (sys.argv[0], ", ".join(undefined_params)))
            sys.exit(1)
        self.Verbose = options.verbose


    # function model_cb
    ##############################################################################
    def model_cb(self, option, opt_str, value, parser):
        """
        This function sets up the single parameters if the 'model' option has been selected
        by the user.
        """
        model_name = value.lower()
        models = CrcModels()
        model = models.getParams(model_name)
        if model != None:
            setattr(parser.values, 'width',         model['width'])
            setattr(parser.values, 'poly',          model['poly'])
            setattr(parser.values, 'reflect_in',    model['reflect_in'])
            setattr(parser.values, 'xor_in',        model['xor_in'])
            setattr(parser.values, 'reflect_out',   model['reflect_out'])
            setattr(parser.values, 'xor_out',       model['xor_out'])
        else:
            models = CrcModels()
            model_list = ", ".join(models.getList())
            raise OptionValueError("unsupported model %s.  Supported models are: %s." % (value, model_list))


# function check_hex
###############################################################################
def check_hex(option, opt, value):
    """
    Checks if a value is given in a decimal integer of hexadecimal reppresentation.
    Returns the converted value or rises an exception on error.
    """
    try:
        if value.lower().startswith("0x"):
            return int(value, 16)
        else:
            return int(value)
    except ValueError:
        raise OptionValueError("option %s: invalid integer or hexadecimal value: %r" % (opt, value))


# function check_bool
###############################################################################
def check_bool(option, opt, value):
    """
    Checks if a value is given as a boolean value (either 0 or 1 or "true" or "false")
    Returns the converted value or rises an exception on error.
    """
    if value.isdigit():
        return int(value, 10) != 0
    elif value.lower() == "false":
        return False
    elif value.lower() == "true":
        return True
    else:
        raise OptionValueError("option %s: invalid boolean value: %r" % (opt, value))


# Class MyOption
###############################################################################
class MyOption(Option):
    """
    New option parsing class extends the Option class
    """
    TYPES = Option.TYPES + ("hex", "bool")
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["hex"] = check_hex
    TYPE_CHECKER["bool"] = check_bool

