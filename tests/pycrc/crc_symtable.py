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
Symbol table for the macro processor used by pycrc.
use as follows:

    from crc_opt import Options
    from crc_symtable import SymbolTable

    opt = Options("0.6")
    sym = SymbolTable(opt)

    str = " ....  "
    terminal = sym.getTerminal(str)
"""

from crc_algorithms import Crc
from qm import QuineMcCluskey
import time
import os


# Class SymbolLookupError
###############################################################################
class SymbolLookupError(Exception):
    """The exception class for the sumbol table.
    """

    # Class constructor
    ###############################################################################
    def __init__(self, reason):
        self.reason = reason

    # function __str__
    ###############################################################################
    def __str__(self):
        return self.reason


# Class SymbolTable
###############################################################################
class SymbolTable:
    """
    The symbol table class.
    """


    # Class constructor
    ###############################################################################
    def __init__(self, opt):
        """
        The class constructor.
        """
        self.opt = opt
        self.table = {}
        self.table["nop"] = ""
        self.table["datetime"] = time.asctime()
        self.table["program_version"] = self.opt.VersionStr
        self.table["program_url"] = self.opt.WebAddress
        if self.opt.OutputFile == None:
            self.table["filename"] = "pycrc_stdout"
        else:
            self.table["filename"] = os.path.basename(self.opt.OutputFile)
        self.table["header_filename"] = self.__pretty_header_filename(self.opt.OutputFile)

        self.table["crc_width"] = self.__pretty_str(self.opt.Width)
        self.table["crc_poly"] = self.__pretty_hex(self.opt.Poly, self.opt.Width)
        self.table["crc_reflect_in"] = self.__pretty_bool(self.opt.ReflectIn)
        self.table["crc_xor_in"] = self.__pretty_hex(self.opt.XorIn, self.opt.Width)
        self.table["crc_reflect_out"] = self.__pretty_bool(self.opt.ReflectOut)
        self.table["crc_xor_out"] = self.__pretty_hex(self.opt.XorOut, self.opt.Width)
        self.table["crc_table_idx_width"] = str(self.opt.TableIdxWidth)
        self.table["crc_table_width"] = str(1 << self.opt.TableIdxWidth)
        self.table["crc_table_mask"] = self.__pretty_hex(self.opt.TableWidth - 1, 8)
        self.table["crc_mask"] = self.__pretty_hex(self.opt.Mask, self.opt.Width)
        self.table["crc_msb_mask"] = self.__pretty_hex(self.opt.MSB_Mask, self.opt.Width)
        if self.opt.Algorithm in set([self.opt.Algo_Table_Driven, self.opt.Algo_Bitwise_Expression]) \
                and (self.opt.Width == None or self.opt.Width < 8):
            if self.opt.Width == None:
                self.table["crc_shift"] = self.__pretty_str(None)
            else:
                self.table["crc_shift"] = self.__pretty_str(8 - self.opt.Width)
        else:
            self.table["crc_shift"] = self.__pretty_str(0)

        self.table["cfg_width"] = "$if ($crc_width != Undefined) {:$crc_width:} $else {:cfg->width:}"
        self.table["cfg_poly"] = "$if ($crc_poly != Undefined) {:$crc_poly:} $else {:cfg->poly:}"
        self.table["cfg_poly_shifted"] = "$if ($crc_shift != 0) {:($cfg_poly << $cfg_shift):} $else {:$cfg_poly:}"
        self.table["cfg_reflect_in"] = "$if ($crc_reflect_in != Undefined) {:$crc_reflect_in:} $else {:cfg->reflect_in:}"
        self.table["cfg_xor_in"] = "$if ($crc_xor_in != Undefined) {:$crc_xor_in:} $else {:cfg->xor_in:}"
        self.table["cfg_reflect_out"] = "$if ($crc_reflect_out != Undefined) {:$crc_reflect_out:} $else {:cfg->reflect_out:}"
        self.table["cfg_xor_out"] = "$if ($crc_xor_out != Undefined) {:$crc_xor_out:} $else {:cfg->xor_out:}"
        self.table["cfg_table_idx_width"] = "$if ($crc_table_idx_width != Undefined) {:$crc_table_idx_width:} $else {:cfg->table_idx_width:}"
        self.table["cfg_table_width"] = "$if ($crc_table_width != Undefined) {:$crc_table_width:} $else {:cfg->table_width:}"
        self.table["cfg_mask"] = "$if ($crc_mask != Undefined) {:$crc_mask:} $else {:cfg->crc_mask:}"
        self.table["cfg_mask_shifted"] = "$if ($crc_shift != 0) {:($cfg_mask << $cfg_shift):} $else {:$cfg_mask:}"
        self.table["cfg_msb_mask"] = "$if ($crc_msb_mask != Undefined) {:$crc_msb_mask:} $else {:cfg->msb_mask:}"
        self.table["cfg_msb_mask_shifted"] = "$if ($crc_shift != 0) {:($cfg_msb_mask << $cfg_shift):} $else {:$cfg_msb_mask:}"
        self.table["cfg_shift"] = "$if ($crc_shift != Undefined) {:$crc_shift:} $else {:cfg->crc_shift:}"

        self.table["undefined_parameters"] = self.__pretty_bool(self.opt.UndefinedCrcParameters)
        self.table["use_cfg_t"] = self.__pretty_bool(self.opt.UndefinedCrcParameters)
        self.table["c_std"] = self.opt.CStd
        self.table["c_bool"] = "$if ($c_std == C89) {:int:} $else {:bool:}"
        self.table["c_true"] = "$if ($c_std == C89) {:1:} $else {:true:}"
        self.table["c_false"] = "$if ($c_std == C89) {:0:} $else {:false:}"

        self.table["underlying_crc_t"] = self.__get_underlying_crc_t()
        self.table["include_files"] = self.__get_include_files()

        self.table["crc_prefix"] = self.opt.SymbolPrefix
        self.table["crc_t"] = self.opt.SymbolPrefix + "t"
        self.table["cfg_t"] = self.opt.SymbolPrefix + "cfg_t"
        self.table["crc_reflect_function"] = self.opt.SymbolPrefix + "reflect"
        self.table["crc_bitwise_expression_function"] = self.opt.SymbolPrefix + "bitwise_expression"
        self.table["crc_table_gen_function"] = self.opt.SymbolPrefix + "table_gen"
        self.table["crc_init_function"] = self.opt.SymbolPrefix + "init"
        self.table["crc_update_function"] = self.opt.SymbolPrefix + "update"
        self.table["crc_finalize_function"] = self.opt.SymbolPrefix + "finalize"

    # function getTerminal
    ###############################################################################
    def getTerminal(self, id):
        """
        Return the expanded terminal, if it exists or None otherwise.
        """
        if id != None:
            if id == "":
                return ""
            if id in self.table:
                return self.table[id]
            key = self.__getTerminal(id)
            if key != None:
                self.table[id] = key
                return key
        raise SymbolLookupError


    # function __getTerminal
    ###############################################################################
    def __getTerminal(self, id):
        """
        Return the expanded terminal, if it exists or None otherwise.
        """
        if id == "constant_crc_init":
            if self.__get_init_value() == None:
                return  self.__pretty_bool(False)
            else:
                return   self.__pretty_bool(True)

        if id == "constant_crc_table":
            if self.opt.Width != None and self.opt.Poly != None and self.opt.ReflectIn != None:
                return  self.__pretty_bool(True)
            else:
                return   self.__pretty_bool(False)

        elif id == "simple_crc_update_def":
            if self.opt.Algorithm in set([self.opt.Algo_Bit_by_Bit, self.opt.Algo_Bit_by_Bit_Fast]):
                if self.opt.Width != None and self.opt.Poly != None and self.opt.ReflectIn != None:
                    return  self.__pretty_bool(True)
            elif self.opt.Algorithm in set([self.opt.Algo_Bitwise_Expression, self.opt.Algo_Table_Driven]):
                if self.opt.Width != None and self.opt.ReflectIn != None:
                    return  self.__pretty_bool(True)
            return  self.__pretty_bool(False)

        elif id == "inline_crc_finalize":
            if self.opt.Algorithm in set([self.opt.Algo_Bit_by_Bit_Fast, self.opt.Algo_Bitwise_Expression, self.opt.Algo_Table_Driven]) and \
                    (self.opt.Width != None and self.opt.ReflectIn != None and self.opt.ReflectOut != None and self.opt.XorOut != None):
                return  self.__pretty_bool(True)
            else:
                return  self.__pretty_bool(False)

        elif id == "simple_crc_finalize_def":
            if self.opt.Algorithm == self.opt.Algo_Bit_by_Bit:
                if self.opt.Width != None and self.opt.Poly != None and self.opt.ReflectOut != None and self.opt.XorOut != None:
                    return  self.__pretty_bool(True)
            elif self.opt.Algorithm == self.opt.Algo_Bit_by_Bit_Fast:
                if self.opt.Width != None and self.opt.ReflectOut != None and self.opt.XorOut != None:
                    return  self.__pretty_bool(True)
            elif self.opt.Algorithm in set([self.opt.Algo_Bitwise_Expression, self.opt.Algo_Table_Driven]):
                if self.opt.Width != None and self.opt.ReflectIn != None and self.opt.ReflectOut != None and self.opt.XorOut != None:
                    return  self.__pretty_bool(True)
            return  self.__pretty_bool(False)

        elif id == "use_reflect_func":
            if self.opt.ReflectOut == False and self.opt.ReflectIn == False:
                return  self.__pretty_bool(False)
            else:
                return  self.__pretty_bool(True)

        elif id == "static_reflect_func":
            if self.opt.Algorithm in set([self.opt.Algo_Bitwise_Expression, self.opt.Algo_Table_Driven]):
                return  self.__pretty_bool(False)
            elif self.opt.ReflectOut != None and self.opt.Algorithm == self.opt.Algo_Bit_by_Bit_Fast:
                return  self.__pretty_bool(False)
            else:
                return  self.__pretty_bool(True)

        elif id == "crc_algorithm":
            if self.opt.Algorithm == self.opt.Algo_Bit_by_Bit:
                return  "bit-by-bit"
            elif self.opt.Algorithm == self.opt.Algo_Bit_by_Bit_Fast:
                return  "bit-by-bit-fast"
            elif self.opt.Algorithm == self.opt.Algo_Bitwise_Expression:
                return "bitwise-expression"
            elif self.opt.Algorithm == self.opt.Algo_Table_Driven:
                return  "table-driven"
            else:
                return  "UNDEFINED"

        elif id == "crc_table_init":
            return  self.__get_table_init()
        elif id == "crc_table_core_algorithm_nonreflected":
            return  self.__get_table_core_algorithm_nonreflected()
        elif id == "crc_table_core_algorithm_reflected":
            return  self.__get_table_core_algorithm_reflected()

        elif id == "header_protection":
            return  self.__pretty_hdrprotection()

        elif id == "crc_init_value":
            ret = self.__get_init_value()
            if ret == None:
                return  ""
            else:
                return  ret

        elif id == "crc_bitwise_expression":
            return self.__get_crc_bwe_expression()

        elif id == "crc_final_value":
            return  """\
$if ($crc_algorithm == "bitwise-expression" or $crc_algorithm == "table-driven") {:
$if ($crc_reflect_in == $crc_reflect_out) {:
$if ($crc_shift != 0) {:(crc >> $cfg_shift):} $else {:crc:} ^ $crc_xor_out\
:} $else {:
$crc_reflect_function($if ($crc_shift != 0) {:(crc >> $cfg_shift):} $else {:crc:}, $crc_width) ^ $crc_xor_out\
:}:} $elif ($crc_reflect_out == True) {:
$crc_reflect_function(crc, $crc_width) ^ $crc_xor_out\
:} $else {:
crc ^ $crc_xor_out\
:}"""
        elif id == "h_template":
            return  """\
$source_header
#ifndef $header_protection
#define $header_protection

$if ($include_files != Undefined) {:
$include_files
:}
#include <stdlib.h>
$if ($c_std != C89) {:
#include <stdint.h>
:}
$if ($undefined_parameters == True and $c_std != C89) {:
#include <stdbool.h>
:}

#ifdef __cplusplus
extern "C" {
#endif


/**
 * The definition of the used algorithm.
 *****************************************************************************/
$if ($crc_algorithm == "bit-by-bit") {:
#define CRC_ALGO_BIT_BY_BIT 1
:} $elif ($crc_algorithm == "bit-by-bit-fast") {:
#define CRC_ALGO_BIT_BY_BIT_FAST 1
:} $elif ($crc_algorithm == "bitwise-expression") {:
#define CRC_ALGO_BITWISE_EXPRESSION 1
:} $elif ($crc_algorithm == "table-driven") {:
#define CRC_ALGO_TABLE_DRIVEN 1
:} $else {:
#define CRC_ALGO_UNKNOWN 1
:}


/**
 * The type of the CRC values.
 *
 * This type must be big enough to contain at least $cfg_width bits.
 *****************************************************************************/
typedef $underlying_crc_t $crc_t;


$if ($undefined_parameters == True) {:
/**
 * The configuration type of the CRC algorithm.
 *****************************************************************************/
typedef struct {
$if ($crc_width == Undefined) {:
    unsigned int width;     /*!< The width of the polynomial */
:}
$if ($crc_poly == Undefined) {:
    $crc_t poly;             /*!< The CRC polynomial */
:}
$if ($crc_reflect_in == Undefined) {:
    $c_bool reflect_in;         /*!< Whether the input shall be reflected or not */
:}
$if ($crc_xor_in == Undefined) {:
    $crc_t xor_in;           /*!< The initial value of the algorithm */
:}
$if ($crc_reflect_out == Undefined) {:
    $c_bool reflect_out;        /*!< Wether the output shall be reflected or not */
:}
$if ($crc_xor_out == Undefined) {:
    $crc_t xor_out;          /*!< The value which shall be XOR-ed to the final CRC value */
:}
$if ($crc_width == Undefined) {:

    /* internal parameters */
    $crc_t msb_mask;             /*!< a bitmask with the Most Significant Bit set to 1
                                     initialise as (crc_t)1u << (width - 1) */
    $crc_t crc_mask;             /*!< a bitmask with all width bits set to 1
                                     initialise as (cfg->msb_mask - 1) | cfg->msb_mask */
    unsigned int crc_shift;     /*!< a shift count that is used when width < 8
                                     initialise as cfg->width < 8 ? 8 - cfg->width : 0 */
:}
} $cfg_t;


:}
$if ($use_reflect_func == True and $static_reflect_func != True) {:
$crc_reflect_doc
$crc_reflect_function_def;


:}
$if ($crc_algorithm == "table-driven" and $constant_crc_table != True) {:
$crc_table_gen_doc
$crc_table_gen_function_def;


:}
$crc_init_doc
$if ($constant_crc_init == False) {:
$crc_init_function_def;
:} $elif ($c_std == C89) {:
#define $crc_init_function()      ($crc_init_value$if ($crc_shift != 0) {: << $cfg_shift:})
:} $else {:
static inline $crc_init_function_def$nop
{
    return $crc_init_value$if ($crc_shift != 0) {: << $cfg_shift:};
}
:}


$crc_update_doc
$crc_update_function_def;


$crc_finalize_doc
$if ($inline_crc_finalize == True) {:
$if ($c_std == C89) {:
#define $crc_finalize_function(crc)      ($crc_final_value)
:} $else {:
static inline $crc_finalize_function_def$nop
{
    return $crc_final_value;
}
:}
:} $else {:
$crc_finalize_function_def;
:}


#ifdef __cplusplus
}           /* closing brace for extern "C" */
#endif

#endif      /* $header_protection */
"""

        elif id == "source_header":
            return  """\
/**
 * \\file $filename
 * Functions and types for CRC checks.
 *
 * Generated on $datetime,
 * by $program_version, $program_url
 * using the configuration:
 *    Width        = $crc_width
 *    Poly         = $crc_poly
 *    XorIn        = $crc_xor_in
 *    ReflectIn    = $crc_reflect_in
 *    XorOut       = $crc_xor_out
 *    ReflectOut   = $crc_reflect_out
 *    Algorithm    = $crc_algorithm
 *****************************************************************************/\
"""

        elif id == "crc_reflect_doc":
            return  """\
/**
 * Reflect all bits of a \\a data word of \\a data_len bytes.
 *
 * \\param data         The data word to be reflected.
 * \\param data_len     The width of \\a data expressed in number of bits.
 * \\return             The reflected data.
 *****************************************************************************/\
"""

        elif id == "crc_reflect_function_def":
            return  """\
$crc_t $crc_reflect_function($crc_t data, size_t data_len)\
"""

        elif id == "crc_reflect_function_gen":
            return  """\
$if ($use_reflect_func == True) {:
$if ($crc_reflect_in == Undefined or $crc_reflect_in == True or $crc_reflect_out == Undefined or $crc_reflect_out == True) {:
$crc_reflect_doc
$crc_reflect_function_def$nop
{
    unsigned int i;
    $crc_t ret;

    ret = data & 0x01;
    for (i = 1; i < data_len; i++) {
        data >>= 1;
        ret = (ret << 1) | (data & 0x01);
    }
    return ret;
}


:}
:}"""

        elif id == "crc_init_function_gen":
            return  """\
$if ($constant_crc_init == False) {:
$crc_init_doc
$crc_init_function_def$nop
{
$if ($crc_algorithm == "bit-by-bit") {:
    unsigned int i;
    $c_bool bit;
    $crc_t crc = $cfg_xor_in;
    for (i = 0; i < $cfg_width; i++) {
        bit = crc & 0x01;
        if (bit) {
            crc = ((crc ^ $cfg_poly) >> 1) | $cfg_msb_mask;
        } else {
            crc >>= 1;
        }
    }
    return crc & $cfg_mask;
:} $elif ($crc_algorithm == "bit-by-bit-fast") {:
    return $cfg_xor_in & $cfg_mask;
:} $elif ($crc_algorithm == "bitwise-expression" or $crc_algorithm == "table-driven") {:
$if ($crc_reflect_in == Undefined) {:
    if ($cfg_reflect_in) {
        return $crc_reflect_function($cfg_xor_in & $cfg_mask, $cfg_width)$if ($crc_shift != 0) {: << $cfg_shift:};
    } else {
        return $cfg_xor_in & $cfg_mask$if ($crc_shift != 0) {: << $cfg_shift:};
    }
:} $elif ($crc_reflect_in == True) {:
    return $crc_reflect_function($cfg_xor_in & $cfg_mask, $cfg_width)$if ($crc_shift != 0) {: << $cfg_shift:};
:} $else {:
    return $cfg_xor_in & $cfg_mask$if ($crc_shift != 0) {: << $cfg_shift:};
:}
:}
}


:}"""

        elif id == "crc_update_function_gen":
            return  """\
$crc_bitwise_expression_function_gen
$crc_table_driven_func_gen
$crc_update_doc
$crc_update_function_def$nop
{
$if ($crc_algorithm == "bit-by-bit") {:
    unsigned int i;
    $c_bool bit;
    unsigned char c;

    while (data_len--) {
$if ($crc_reflect_in == Undefined) {:
        if ($cfg_reflect_in) {
            c = $crc_reflect_function(*data++, 8);
        } else {
            c = *data++;
        }
:} $elif ($crc_reflect_in == True) {:
        c = $crc_reflect_function(*data++, 8);
:} $else {:
        c = *data++;
:}
        for (i = 0; i < 8; i++) {
            bit = $if ($c_std == C89) {:!!(crc & $cfg_msb_mask):} $else {:crc & $cfg_msb_mask:};
            crc = (crc << 1) | ((c >> (7 - i)) & 0x01);
            if (bit) {
                crc ^= $cfg_poly;
            }
        }
        crc &= $cfg_mask;
    }
    return crc & $cfg_mask;
:} $elif ($crc_algorithm == "bit-by-bit-fast") {:
    unsigned int i;
    $c_bool bit;
    unsigned char c;

    while (data_len--) {
$if ($crc_reflect_in == Undefined) {:
        if ($cfg_reflect_in) {
            c = $crc_reflect_function(*data++, 8);
        } else {
            c = *data++;
        }
:} $else {:
        c = *data++;
:}
$if ($crc_reflect_in == True) {:
        for (i = 0x01; i & 0xff; i <<= 1){::}
:} $else {:
        for (i = 0x80; i > 0; i >>= 1){::}
:} {
            bit = $if ($c_std == C89) {:!!(crc & $cfg_msb_mask):} $else {:crc & $cfg_msb_mask:};
            if (c & i) {
                bit = !bit;
            }
            crc <<= 1;
            if (bit) {
                crc ^= $cfg_poly;
            }
        }
        crc &= $cfg_mask;
    }
    return crc & $cfg_mask;
:} $elif ($crc_algorithm == "bitwise-expression" or $crc_algorithm == "table-driven") {:
    unsigned int tbl_idx;

$if ($crc_reflect_in == Undefined) {:
    if (cfg->reflect_in) {
        while (data_len--) {
$crc_table_core_algorithm_reflected
            data++;
        }
    } else {
        while (data_len--) {
$crc_table_core_algorithm_nonreflected
            data++;
        }
    }
:} $else {:
    while (data_len--) {
$if ($crc_reflect_in == True) {:
$crc_table_core_algorithm_reflected
:} $elif ($crc_reflect_in == False) {:
$crc_table_core_algorithm_nonreflected
:}
        data++;
    }
:}
    return crc & $cfg_mask_shifted;
:}
}


"""

        elif id == "crc_finalize_function_gen":
            return  """\
$if ($inline_crc_finalize != True) {:
$crc_finalize_doc
$crc_finalize_function_def$nop
{
$if ($crc_algorithm == "bit-by-bit") {:
    unsigned int i;
    $c_bool bit;

    for (i = 0; i < $cfg_width; i++) {
        bit = $if ($c_std == C89) {:!!(crc & $cfg_msb_mask):} $else {:crc & $cfg_msb_mask:};
        crc = (crc << 1) | 0x00;
        if (bit) {
            crc ^= $cfg_poly;
        }
    }
$if ($crc_reflect_out == Undefined) {:
    if ($cfg_reflect_out) {
        crc = $crc_reflect_function(crc, $cfg_width);
    }
:} $elif ($crc_reflect_out == True) {:
    crc = $crc_reflect_function(crc, $cfg_width);
:}
    return (crc ^ $cfg_xor_out) & $cfg_mask;
:} $elif ($crc_algorithm == "bit-by-bit-fast") {:
$if ($crc_reflect_out == Undefined) {:
    if (cfg->reflect_out) {
        crc = $crc_reflect_function(crc, $cfg_width);
    }
:} $elif ($crc_reflect_out == True) {:
    crc = $crc_reflect_function(crc, $cfg_width);
:}
    return (crc ^ $cfg_xor_out) & $cfg_mask;
:} $elif ($crc_algorithm == "bitwise-expression" or $crc_algorithm == "table-driven") {:
$if ($crc_shift != 0) {:
    crc >>= $cfg_shift;
:}
$if ($crc_reflect_in == Undefined or $crc_reflect_out == Undefined) {:
$if ($crc_reflect_in == Undefined and $crc_reflect_out == Undefined) {:
    if (cfg->reflect_in == !cfg->reflect_out):}
 $elif ($crc_reflect_out == Undefined) {:
    if ($if ($crc_reflect_in == True) {:!:}cfg->reflect_out):}
 $elif ($crc_reflect_in == Undefined) {:
    if ($if ($crc_reflect_out == True) {:!:}cfg->reflect_in):} {
        crc = $crc_reflect_function(crc, $cfg_width);
    }
:} $elif ($crc_reflect_in != $crc_reflect_out) {:
    crc = $crc_reflect_function(crc, $cfg_width);
:}
    return (crc ^ $cfg_xor_out) & $cfg_mask;
:}
}


:}"""

        elif id == "crc_table_driven_func_gen":
            return  """\
$if ($crc_algorithm == "table-driven" and $constant_crc_table != True) {:
$crc_table_gen_doc
$crc_table_gen_function_def
{
    $crc_t crc;
    unsigned int i, j;

    for (i = 0; i < $cfg_table_width; i++) {
$if ($crc_reflect_in == Undefined) {:
        if (cfg->reflect_in) {
            crc = $crc_reflect_function(i, $cfg_table_idx_width);
        } else {
            crc = i;
        }
:} $elif ($crc_reflect_in == True) {:
        crc = $crc_reflect_function(i, $cfg_table_idx_width);
:} $else {:
        crc = i;
:}
$if ($crc_shift != 0) {:
        crc <<= ($cfg_width - $cfg_table_idx_width + $cfg_shift);
:} $else {:
        crc <<= ($cfg_width - $cfg_table_idx_width);
:}
        for (j = 0; j < $cfg_table_idx_width; j++) {
            if (crc & $cfg_msb_mask_shifted) {
                crc = (crc << 1) ^ $cfg_poly_shifted;
            } else {
                crc = crc << 1;
            }
        }
$if ($crc_reflect_in == Undefined) {:
        if (cfg->reflect_in) {
$if ($crc_shift != 0) {:
            crc = $crc_reflect_function(crc >> $cfg_shift, $cfg_width) << $cfg_shift;
:} $else {:
            crc = $crc_reflect_function(crc, $cfg_width);
:}
        }
:} $elif ($crc_reflect_in == True) {:
$if ($crc_shift != 0) {:
        crc = $crc_reflect_function(crc >> $cfg_shift, $cfg_width) << $cfg_shift;
:} $else {:
        crc = $crc_reflect_function(crc, $cfg_width);
:}
:}
        crc_table[i] = crc & $cfg_mask_shifted;
    }
}


:}"""

        elif id == "crc_bitwise_expression_function_gen":
            return  """\
$if ($crc_algorithm == "bitwise-expression") {:
$crc_bitwise_expression_doc
$crc_bitwise_expression_function_def
{
    $crc_t bits = ($crc_t)tbl_idx;

    return $crc_bitwise_expression;
}

:}"""

        elif id == "crc_bitwise_expression_doc":
            return  """\
/**
 * Calculate the logical equivalent of the crc table at tbl_idx with by a
 * boolean expression.
 *
 * \\return     the logical equivalent of the crc table at tbl_idx.
 *****************************************************************************/\
"""

        elif id == "crc_bitwise_expression_function_def":
            return  """\
static $if ($c_std != C89) {:inline :}$crc_t $crc_bitwise_expression_function(int tbl_idx)\
"""

        elif id == "crc_table_gen_doc":
            return  """\
/**
 * Populate the private static crc table.
 *
 * \\param cfg  A pointer to a initialised $cfg_t structure.
 * \\return     void
 *****************************************************************************/\
"""

        elif id == "crc_table_gen_function_def":
            return  """\
void $crc_table_gen_function(const $cfg_t *cfg)\
"""

        elif id == "crc_init_doc":
            return  """\
/**
 * Calculate the initial crc value.
 *
$if ($use_cfg_t == True) {:
 * \\param cfg  A pointer to a initialised $cfg_t structure.
:}
 * \\return     The initial crc value.
 *****************************************************************************/\
"""

        elif id == "crc_init_function_def":
            return  """\
$if ($constant_crc_init == False) {:
$crc_t $crc_init_function(const $cfg_t *cfg)\
:} $else {:
$crc_t $crc_init_function(void)\
:}\
"""

        elif id == "crc_update_doc":
            return  """\
/**
 * Update the crc value with new data.
 *
 * \\param crc      The current crc value.
$if ($simple_crc_update_def != True) {:
 * \\param cfg      A pointer to a initialised $cfg_t structure.
:}
 * \\param data     Pointer to a buffer of \\a data_len bytes.
 * \\param data_len Number of bytes in the \\a data buffer.
 * \\return         The updated crc value.
 *****************************************************************************/\
"""

        elif id == "crc_update_function_def":
            return  """\
$if ($simple_crc_update_def != True) {:
$crc_t $crc_update_function(const $cfg_t *cfg, $crc_t crc, const unsigned char *data, size_t data_len)\
:} $else {:
$crc_t $crc_update_function($crc_t crc, const unsigned char *data, size_t data_len)\
:}\
"""

        elif id == "crc_finalize_doc":
            return  """\
/**
 * Calculate the final crc value.
 *
$if ($simple_crc_finalize_def != True) {:
 * \\param cfg  A pointer to a initialised $cfg_t structure.
:}
 * \\param crc  The current crc value.
 * \\return     The final crc value.
 *****************************************************************************/\
"""

        elif id == "crc_finalize_function_def":
            return  """\
$if ($simple_crc_finalize_def != True) {:
$crc_t $crc_finalize_function(const $cfg_t *cfg, $crc_t crc)\
:} $else {:
$crc_t $crc_finalize_function($crc_t crc)\
:}\
"""

        elif id == "c_template":
            return  """\
$source_header
$if ($include_files != Undefined) {:
$include_files
:}
#include "$header_filename"     /* include the header file generated with pycrc */
#include <stdlib.h>
$if ($c_std != C89) {:
#include <stdint.h>
$if ($undefined_parameters == True or $crc_algorithm == "bit-by-bit" or $crc_algorithm == "bit-by-bit-fast") {:
#include <stdbool.h>
:}
:}

$if ($use_reflect_func == True and $static_reflect_func == True) {:
static $crc_reflect_function_def;

:}
$c_table_gen\
$crc_reflect_function_gen\
$crc_init_function_gen\
$crc_update_function_gen\
$crc_finalize_function_gen\
"""

        elif id == "c_table_gen":
            return  """\
$if ($crc_algorithm == "table-driven") {:
/**
 * Static table used for the table_driven implementation.
$if ($undefined_parameters == True) {:
 * Must be initialised with the $crc_init_function function.
:}
 *****************************************************************************/
$if ($constant_crc_table != True) {:
static $crc_t crc_table[$crc_table_width];
:} $else {:
static const $crc_t crc_table[$crc_table_width] = {
$crc_table_init
};
:}

:}"""

        elif id == "main_template":
            return  """\
$if ($include_files != Undefined) {:
$include_files
:}
#include <stdio.h>
#include <getopt.h>
$if ($undefined_parameters == True) {:
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
:}
$if ($c_std != C89) {:
#include <stdbool.h>
:}
#include <string.h>

static char str[256] = "123456789";
static $c_bool verbose = $c_false;

void print_params($if ($undefined_parameters == True) {:const $cfg_t *cfg:} $else {:void:});
$getopt_template

void print_params($if ($undefined_parameters == True) {:const $cfg_t *cfg:} $else {:void:})
{
    char format[20];

$if ($c_std == C89) {:
    sprintf(format, "%%-16s = 0x%%0%dlx\\n", (unsigned int)($cfg_width + 3) / 4);
    printf("%-16s = %d\\n", "width", (unsigned int)$cfg_width);
    printf(format, "poly", (unsigned long int)$cfg_poly);
    printf("%-16s = %s\\n", "reflect_in", $if ($crc_reflect_in == Undefined) {:$cfg_reflect_in ? "true": "false":} $else {:$if ($crc_reflect_in == True) {:"true":} $else {:"false":}:});
    printf(format, "xor_in", (unsigned long int)$cfg_xor_in);
    printf("%-16s = %s\\n", "reflect_out", $if ($crc_reflect_out == Undefined) {:$cfg_reflect_out ? "true": "false":} $else {:$if ($crc_reflect_out == True) {:"true":} $else {:"false":}:});
    printf(format, "xor_out", (unsigned long int)$cfg_xor_out);
    printf(format, "crc_mask", (unsigned long int)$cfg_mask);
    printf(format, "msb_mask", (unsigned long int)$cfg_msb_mask);
:} $else {:
    snprintf(format, sizeof(format), "%%-16s = 0x%%0%dllx\\n", (unsigned int)($cfg_width + 3) / 4);
    printf("%-16s = %d\\n", "width", (unsigned int)$cfg_width);
    printf(format, "poly", (unsigned long long int)$cfg_poly);
    printf("%-16s = %s\\n", "reflect_in", $if ($crc_reflect_in == Undefined) {:$cfg_reflect_in ? "true": "false":} $else {:$if ($crc_reflect_in == True) {:"true":} $else {:"false":}:});
    printf(format, "xor_in", (unsigned long long int)$cfg_xor_in);
    printf("%-16s = %s\\n", "reflect_out", $if ($crc_reflect_out == Undefined) {:$cfg_reflect_out ? "true": "false":} $else {:$if ($crc_reflect_out == True) {:"true":} $else {:"false":}:});
    printf(format, "xor_out", (unsigned long long int)$cfg_xor_out);
    printf(format, "crc_mask", (unsigned long long int)$cfg_mask);
    printf(format, "msb_mask", (unsigned long long int)$cfg_msb_mask);
:}
}

/**
 * C main function.
 *
 * \\return     0 on success, != 0 on error.
 *****************************************************************************/
int main(int argc, char *argv[])
{
$if ($undefined_parameters == True) {:
    $cfg_t cfg = {
$if ($crc_width == Undefined) {:
            0,      /* width */
:}
$if ($crc_poly == Undefined) {:
            0,      /* poly */
:}
$if ($crc_xor_in == Undefined) {:
            0,      /* xor_in */
:}
$if ($crc_reflect_in == Undefined) {:
            0,      /* reflect_in */
:}
$if ($crc_xor_out == Undefined) {:
            0,      /* xor_out */
:}
$if ($crc_reflect_out == Undefined) {:
            0,      /* reflect_out */
:}
$if ($crc_width == Undefined) {:

            0,      /* crc_mask */
            0,      /* msb_mask */
            0,      /* crc_shift */
:}
    };
:}
    $crc_t crc;

$if ($undefined_parameters == True) {:
    get_config(argc, argv, &cfg);
:} $else {:
    get_config(argc, argv);
:}
$if ($crc_algorithm == "table-driven" and $constant_crc_table != True) {:
    $crc_table_gen_function(&cfg);
:}
    crc = $crc_init_function($if ($constant_crc_init != True) {:&cfg:});
    crc = $crc_update_function($if ($simple_crc_update_def != True) {:&cfg, :}crc, (unsigned char *)str, strlen(str));
    crc = $crc_finalize_function($if ($simple_crc_finalize_def != True) {:&cfg, :}crc);

    if (verbose) {
        print_params($if ($undefined_parameters == True) {:&cfg:});
    }
$if ($c_std == C89) {:
    printf("0x%lx\\n", (unsigned long int)crc);
:} $else {:
    printf("0x%llx\\n", (unsigned long long int)crc);
:}
    return 0;
}
"""

        elif id == "getopt_template":
            return  """\
$if ($crc_reflect_in == Undefined or $crc_reflect_out == Undefined) {:
static $c_bool atob(const char *str);
:}
$if ($crc_poly == Undefined or $crc_xor_in == Undefined or $crc_xor_out == Undefined) {:
static crc_t xtoi(const char *str);
:}
static int get_config(int argc, char *argv[]$if ($undefined_parameters == True) {:, $cfg_t *cfg:});


$if ($crc_reflect_in == Undefined or $crc_reflect_out == Undefined) {:
$c_bool atob(const char *str)
{
    if (!str) {
        return 0;
    }
    if (isdigit(str[0])) {
        return ($c_bool)atoi(str);
    }
    if (tolower(str[0]) == 't') {
        return $c_true;
    }
    return $c_false;
}

:}
$if ($crc_poly == Undefined or $crc_xor_in == Undefined or $crc_xor_out == Undefined) {:
crc_t xtoi(const char *str)
{
    crc_t ret = 0;

    if (!str) {
        return 0;
    }
    if (str[0] == '0' && tolower(str[1]) == 'x') {
        str += 2;
        while (*str) {
            if (isdigit(*str))
                ret = 16 * ret + *str - '0';
            else if (isxdigit(*str))
                ret = 16 * ret + tolower(*str) - 'a' + 10;
            else
                return ret;
            str++;
        }
    } else if (isdigit(*str)) {
        while (*str) {
            if (isdigit(*str))
                ret = 10 * ret + *str - '0';
            else
                return ret;
            str++;
        }
    }
    return ret;
}


:}
static int get_config(int argc, char *argv[]$if ($undefined_parameters == True) {:, $cfg_t *cfg:})
{
    int c;
    int option_index;
    static struct option long_options[] = {
$if ($crc_width == Undefined) {:
        {"width",           1, 0, 'w'},
:}
$if ($crc_poly == Undefined) {:
        {"poly",            1, 0, 'p'},
:}
$if ($crc_reflect_in == Undefined) {:
        {"reflect-in",      1, 0, 'n'},
:}
$if ($crc_xor_in == Undefined) {:
        {"xor-in",          1, 0, 'i'},
:}
$if ($crc_reflect_out == Undefined) {:
        {"reflect-out",     1, 0, 'u'},
:}
$if ($crc_xor_out == Undefined) {:
        {"xor-out",         1, 0, 'o'},
:}
        {"verbose",         0, 0, 'v'},
        {"check-string",    1, 0, 's'},
$if ($crc_width == Undefined) {:
        {"table-idx-with",  1, 0, 't'},
:}
        {0, 0, 0, 0}
    };

    while (1) {
        option_index = 0;

        c = getopt_long(argc, argv, "w:p:n:i:u:o:s:vt", long_options, &option_index);
        if (c == -1)
            break;

        switch (c) {
            case 0:
                printf("option %s", long_options[option_index].name);
                if (optarg)
                    printf(" with arg %s", optarg);
                printf("\\n");
$if ($crc_width == Undefined) {:
            case 'w':
                cfg->width = atoi(optarg);
                break;
:}
$if ($crc_poly == Undefined) {:
            case 'p':
                cfg->poly = xtoi(optarg);
                break;
:}
$if ($crc_reflect_in == Undefined) {:
            case 'n':
                cfg->reflect_in = atob(optarg);
                break;
:}
$if ($crc_xor_in == Undefined) {:
            case 'i':
                cfg->xor_in = xtoi(optarg);
                break;
:}
$if ($crc_reflect_out == Undefined) {:
            case 'u':
                cfg->reflect_out = atob(optarg);
                break;
:}
$if ($crc_xor_out == Undefined) {:
            case 'o':
                cfg->xor_out = xtoi(optarg);
                break;
:}
            case 's':
                memcpy(str, optarg, strlen(optarg) < sizeof(str) ? strlen(optarg) + 1 : sizeof(str));
                str[sizeof(str) - 1] = '\\0';
                break;
            case 'v':
                verbose = $c_true;
                break;
$if ($crc_width == Undefined) {:
            case 't':
                /* ignore --table_idx_width option */
                break;
:}
            case '?':
                return -1;
            case ':':
                fprintf(stderr, "missing argument to option %c\\n", c);
                return -1;
            default:
                fprintf(stderr, "unhandled option %c\\n", c);
                return -1;
        }
    }
$if ($crc_width == Undefined) {:
    cfg->msb_mask = (crc_t)1u << (cfg->width - 1);
    cfg->crc_mask = (cfg->msb_mask - 1) | cfg->msb_mask;
    cfg->crc_shift = cfg->width < 8 ? 8 - cfg->width : 0;
:}

$if ($crc_poly == Undefined) {:
    cfg->poly &= $cfg_mask;
:}
$if ($crc_xor_in == Undefined) {:
    cfg->xor_in &= $cfg_mask;
:}
$if ($crc_xor_out == Undefined) {:
    cfg->xor_out &= $cfg_mask;
:}
    return 0;
}\
"""


    # function __pretty_str
    ###############################################################################
    def __pretty_str(self, value):
        """
        Return a value of width bits as a pretty string.
        """
        if value == None:
            return "Undefined"
        return str(value)


    # function __pretty_hex
    ###############################################################################
    def __pretty_hex(self, value, width = None):
        """
        Return a value of width bits as a pretty hexadecimal formatted string.
        """
        if value == None:
            return "Undefined"
        if width == None:
            return "0x%x" % value
        width = (width + 3) // 4
        hex_str = "0x%%0%dx" % width
        return hex_str % value


    # function __pretty_bool
    ###############################################################################
    def __pretty_bool(self, value):
        """
        Return a boolen value of width bits as a pretty formatted string.
        """
        if value == None:
            return "Undefined"
        if value:
            return "True"
        else:
            return "False"


    # function __pretty_header_filename
    ###############################################################################
    def __pretty_header_filename(self, filename):
        if filename == None:
            return "pycrc_stdout.h"
        filename = os.path.basename(filename)
        if filename[-2:] == ".c":
            return filename[0:-1] + "h"
        else:
            return filename + ".h"


    # function __pretty_hdrprotection
    ###############################################################################
    def __pretty_hdrprotection(self):
        """
        Return the name of a C header protection (e.g. __CRC_IMPLEMENTATION_H__).
        """
        if self.opt.OutputFile == None:
            filename = "pycrc_stdout"
        else:
            filename = os.path.basename(self.opt.OutputFile)
        out_str = "".join([s.upper() if s.isalnum() else "_" for s in filename])
        return "__" + out_str + "__"


    # function __get_underlying_crc_t
    ###############################################################################
    def __get_underlying_crc_t(self):
        """
        Return the C type of the crc_t typedef.
        """
        if self.opt.CrcType != None:
            return self.opt.CrcType
        if self.opt.CStd == "C89":
            if self.opt.Width == None:
                return "unsigned long int"
            if self.opt.Width <= 8:
                return "unsigned char"
            elif self.opt.Width <= 16:
                return "unsigned int"
            else:
                return "unsigned long int"
        else:       # C99
            if self.opt.Width == None:
                return "unsigned long long int"
            if self.opt.Width <= 8:
                return "uint_fast8_t"
            elif self.opt.Width <= 16:
                return "uint_fast16_t"
            elif self.opt.Width <= 32:
                return "uint_fast32_t"
            elif self.opt.Width <= 64:
                return "uint_fast64_t"
            elif self.opt.Width <= 128:
                return "uint_fast128_t"
            else:
                return "uintmax_t"


    # function __get_include_files
    ###############################################################################
    def __get_include_files(self):
        """
        Return an additional include instructions, if specified.
        """
        if self.opt.IncludeFiles == None or len(self.opt.IncludeFiles) == 0:
            return None
        ret = []
        for include_file in self.opt.IncludeFiles:
            if include_file[0] == '"' or include_file[0] == '<':
                ret.append('#include %s' % include_file)
            else:
                ret.append('#include "%s"' % include_file)
        return '\n'.join(ret)


    # function __get_init_value
    ###############################################################################
    def __get_init_value(self):
        """
        Return the init value of a C implementation, according to the selected algorithm and
        to the given options.
        If no default option is given for a given parameter, value in the cfg_t structure must be used.
        """
        if self.opt.Algorithm == self.opt.Algo_Bit_by_Bit:
            if self.opt.XorIn == None or self.opt.Width == None or self.opt.Poly == None:
                return None
            crc = Crc(width = self.opt.Width, poly = self.opt.Poly,
                    reflect_in = self.opt.ReflectIn, xor_in = self.opt.XorIn,
                    reflect_out = self.opt.ReflectOut, xor_out = self.opt.XorOut,
                    table_idx_width = self.opt.TableIdxWidth)
            init = crc.NonDirectInit
        elif self.opt.Algorithm == self.opt.Algo_Bit_by_Bit_Fast:
            if self.opt.XorIn == None:
                return None
            init = self.opt.XorIn
        elif self.opt.Algorithm in set([self.opt.Algo_Bitwise_Expression, self.opt.Algo_Table_Driven]):
            if self.opt.ReflectIn == None or self.opt.XorIn == None or self.opt.Width == None:
                return None
            if self.opt.Poly == None:
                poly = 0
            else:
                poly = self.opt.Poly
            crc = Crc(width = self.opt.Width, poly = poly,
                    reflect_in = self.opt.ReflectIn, xor_in = self.opt.XorIn,
                    reflect_out = self.opt.ReflectOut, xor_out = self.opt.XorOut,
                    table_idx_width = self.opt.TableIdxWidth)
            if self.opt.ReflectIn:
                init = crc.reflect(crc.DirectInit, self.opt.Width)
            else:
                init = crc.DirectInit
        else:
            init = 0
        return self.__pretty_hex(init, self.opt.Width)


    # function __get_table_init
    ###############################################################################
    def __get_table_init(self):
        """
        Return the precalculated CRC table for the table_driven implementation.
        """
        if self.opt.Algorithm != self.opt.Algo_Table_Driven:
            return "0"
        if self.opt.Width == None or self.opt.Poly == None or self.opt.ReflectIn == None:
            return "0"
        crc = Crc(width = self.opt.Width, poly = self.opt.Poly,
                reflect_in = self.opt.ReflectIn,
                xor_in = 0, reflect_out = False, xor_out = 0,       # set unimportant variables to known values
                table_idx_width = self.opt.TableIdxWidth)
        tbl = crc.gen_table()
        if self.opt.Width >= 32:
            values_per_line = 4
        elif self.opt.Width >= 16:
            values_per_line = 8
        else:
            values_per_line = 16
        format_width = max(self.opt.Width, 8)
        out  = ""
        for i in range(self.opt.TableWidth):
            if i % values_per_line == 0:
                out += " " * 4
            if i == (self.opt.TableWidth - 1):
                out += "%s" % self.__pretty_hex(tbl[i], format_width)
            elif i % values_per_line == (values_per_line - 1):
                out += "%s,\n" % self.__pretty_hex(tbl[i], format_width)
            else:
                out += "%s, " % self.__pretty_hex(tbl[i], format_width)
        return out


    # function __get_table_core_algorithm_nonreflected
    ###############################################################################
    def __get_table_core_algorithm_nonreflected(self):
        """
        Return the core loop of the table-driven algorithm, non-reflected variant
        """
        if self.opt.Algorithm not in set([self.opt.Algo_Table_Driven, self.opt.Algo_Bitwise_Expression]):
            return ""

        loop_core = ""
        loop_indent = ""
        if self.opt.UndefinedCrcParameters:
            loop_indent = " " * 12
        else:
            loop_indent = " " * 8

        if self.opt.Width == None:
            shr = "($cfg_width - $cfg_table_idx_width + $cfg_shift)"
        elif self.opt.Width < 8:
            shr = "%d" % (self.opt.Width - self.opt.TableIdxWidth + 8 - self.opt.Width)
        else:
            shr = "%d" % (self.opt.Width - self.opt.TableIdxWidth)

        if self.opt.TableIdxWidth == 8:
            crc_lookup = '$if ($crc_algorithm == "table-driven") {:crc_table[tbl_idx]:}' + \
                         '$elif ($crc_algorithm == "bitwise-expression") {:$crc_bitwise_expression_function(tbl_idx):}'
            loop_core += loop_indent + "tbl_idx = ((crc >> " + shr + ") ^ *data) & $crc_table_mask;" + '\n' + \
                            loop_indent + "crc = (" + crc_lookup + " ^ (crc << $cfg_table_idx_width)) & $cfg_mask_shifted;" + '\n'
        else:
            crc_lookup = '$if ($crc_algorithm == "table-driven") {:crc_table[tbl_idx & $crc_table_mask]:}' + \
                         '$elif ($crc_algorithm == "bitwise-expression") {:$crc_bitwise_expression_function(tbl_idx & $crc_table_mask):}'
            for i in range (8 // self.opt.TableIdxWidth):
                str_idx = "%s" % (8 - (i + 1) * self.opt.TableIdxWidth)
                loop_core += loop_indent + "tbl_idx = (crc >> " + shr + ") ^ (*data >> " + str_idx + ");" + '\n' + \
                                loop_indent + "crc = " + crc_lookup + " ^ (crc << $cfg_table_idx_width);" + '\n'
        return loop_core


    # function __get_table_core_algorithm_reflected
    ###############################################################################
    def __get_table_core_algorithm_reflected(self):
        """
        Return the core loop of the table-driven algorithm, reflected variant.
        """
        if self.opt.Algorithm not in set([self.opt.Algo_Table_Driven, self.opt.Algo_Bitwise_Expression]):
            return ""

        loop_core = ""
        loop_indent = ""
        if self.opt.UndefinedCrcParameters:
            loop_indent = " " * 12
        else:
            loop_indent = " " * 8
        crc_shifted = "$if ($crc_shift != 0) {:(crc >> $cfg_shift):} $else {:crc:}"

        if self.opt.TableIdxWidth == 8:
            crc_lookup = '$if ($crc_algorithm == "table-driven") {:crc_table[tbl_idx]:}' + \
                         '$elif ($crc_algorithm == "bitwise-expression") {:$crc_bitwise_expression_function(tbl_idx):}'
            loop_core += loop_indent + "tbl_idx = (" + crc_shifted + " ^ *data) & $crc_table_mask;" + '\n' + \
                            loop_indent + "crc = (" + crc_lookup + " ^ (crc >> $cfg_table_idx_width)) & $cfg_mask_shifted;" + '\n'
        else:
            crc_lookup = '$if ($crc_algorithm == "table-driven") {:crc_table[tbl_idx & $crc_table_mask]:}' + \
                         '$elif ($crc_algorithm == "bitwise-expression") {:$crc_bitwise_expression_function(tbl_idx & $crc_table_mask):}'
            for i in range (8 // self.opt.TableIdxWidth):
                str_idx = "%d" % i
                loop_core += loop_indent + "tbl_idx = " + crc_shifted + " ^ (*data >> (" + str_idx + " * $cfg_table_idx_width));" + '\n' + \
                                loop_indent + "crc = " + crc_lookup + " ^ (crc >> $cfg_table_idx_width);" + '\n'
        return loop_core


    # __get_crc_bwe_bitmask_minterms
    ###############################################################################
    def __get_crc_bwe_bitmask_minterms(self):
        """
        Return a list of (bitmask, minterms), for all bits.
        """
        crc = Crc(width = self.opt.Width, poly = self.opt.Poly,
                reflect_in = self.opt.ReflectIn, xor_in = self.opt.XorIn,
                reflect_out = self.opt.ReflectOut, xor_out = self.opt.XorOut,
                table_idx_width = self.opt.TableIdxWidth)
        qm = QuineMcCluskey(use_xor = True)
        crc_tbl = crc.gen_table()
        bm_mt = []
        for bit in range(max(self.opt.Width, 8)):
            ones = [i for i in range(self.opt.TableWidth) if crc_tbl[i] & (1 << bit) != 0]
            terms = qm.simplify(ones, [])
            if self.opt.Verbose:
                print("bit %02d: %s" % (bit, terms))
            if terms != None:
                for term in terms:
                    shifted_term = '.' * bit + term + '.' * (self.opt.Width - bit - 1)
                    bm_mt.append((1 << bit, shifted_term))
        return bm_mt


    # __format_bwe_expression
    ###############################################################################
    def __format_bwe_expression(self, minterms):
        """
        Return the formatted bwe expression.
        """
        or_exps = []
        and_fmt = "((%%s) & 0x%%0%dx)" % ((self.opt.Width + 3) // 4)
        for (bitmask, minterm) in minterms:
            xors = []
            ands = []
            for (bit_pos, operator) in enumerate(minterm):
                shift = bit_pos - self.opt.TableIdxWidth + 1
                if shift > 0:
                    bits_fmt = "(%%sbits << %d)" % (shift)
                elif shift < 0:
                    bits_fmt = "(%%sbits >> %d)" % (-shift)
                else:
                    bits_fmt = "%sbits"

                if operator == "^":
                    xors.append(bits_fmt % "")
                elif operator == "~":
                    xors.append(bits_fmt % "~")
                elif operator == "0":
                    ands.append(bits_fmt % "~")
                elif operator == "1":
                    ands.append(bits_fmt % "")

            if len(xors) > 0:
                ands.append(" ^ ".join(xors))
            if len(ands) > 0:
                and_out = " & ".join(ands)
                or_exps.append(and_fmt % (and_out, bitmask))
        if len(or_exps) == 0:
            return "0"
        return " |\n            ".join(or_exps)


    # __get_crc_bwe_expression
    ###############################################################################
    def __get_crc_bwe_expression(self):
        """
        Return the expression for the bitwise-expression algorithm.
        """
        if self.opt.Algorithm != self.opt.Algo_Bitwise_Expression or \
                self.opt.Action == self.opt.Action_Generate_H or \
                self.opt.UndefinedCrcParameters:
            return ""
        minterms = self.__get_crc_bwe_bitmask_minterms()
        ret = self.__format_bwe_expression(minterms)
        return ret
