#!/usr/bin/env python3

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
pycrc is a fully parameterisable Cyclic Redundancy Check (CRC) calculation
utility and C source code generator written in Python.

It can:
    -  generate the checksum of a string
    -  generate the checksum of a file
    -  generate the C header file and source of any of the algorithms below

It supports the following CRC algorithms:
    -  bit-by-bit       the basic algorithm which operates bit by bit on the
                        augmented message
    -  bit-by-bit-fast  a variation of the simple bit-by-bit algorithm
    -  table-driven     the standard table driven algorithm
"""

from __future__ import print_function
from crc_opt import Options
from crc_algorithms import Crc
from crc_parser import MacroParser, ParseError
import binascii
import sys


# function print_parameters
###############################################################################
def print_parameters(opt):
    """
    Generate a string with the options pretty-printed (used in the --verbose mode).
    """
    in_str  = ""
    in_str += "Width        = $crc_width\n"
    in_str += "Poly         = $crc_poly\n"
    in_str += "ReflectIn    = $crc_reflect_in\n"
    in_str += "XorIn        = $crc_xor_in\n"
    in_str += "ReflectOut   = $crc_reflect_out\n"
    in_str += "XorOut       = $crc_xor_out\n"
    in_str += "Algorithm    = $crc_algorithm\n"

    mp = MacroParser(opt)
    mp.parse(in_str)
    return mp.out_str


# function check_string
###############################################################################
def check_string(opt):
    """
    Return the calculated CRC sum of a string.
    """
    error = False
    if opt.UndefinedCrcParameters:
        sys.stderr.write("%s: error: undefined parameters\n" % sys.argv[0])
        sys.exit(1)
    if opt.Algorithm == 0:
        opt.Algorithm = opt.Algo_Bit_by_Bit | opt.Algo_Bit_by_Bit_Fast | opt.Algo_Table_Driven

    alg = Crc(width = opt.Width, poly = opt.Poly,
        reflect_in = opt.ReflectIn, xor_in = opt.XorIn,
        reflect_out = opt.ReflectOut, xor_out = opt.XorOut,
        table_idx_width = opt.TableIdxWidth)

    crc = None
    if opt.Algorithm & opt.Algo_Bit_by_Bit:
        bbb_crc = alg.bit_by_bit(opt.CheckString)
        if crc != None and bbb_crc != crc:
            error = True
        crc = bbb_crc
    if opt.Algorithm & opt.Algo_Bit_by_Bit_Fast:
        bbf_crc = alg.bit_by_bit_fast(opt.CheckString)
        if crc != None and bbf_crc != crc:
            error = True
        crc = bbf_crc
    if opt.Algorithm & opt.Algo_Table_Driven:
        # no point making the python implementation slower by using less than 8 bits as index.
        opt.TableIdxWidth = 8
        tbl_crc = alg.table_driven(opt.CheckString)
        if crc != None and tbl_crc != crc:
            error = True
        crc = tbl_crc

    if error:
        sys.stderr.write("%s: error: different checksums!\n" % sys.argv[0])
        if opt.Algorithm & opt.Algo_Bit_by_Bit:
            sys.stderr.write("       bit-by-bit:        0x%x\n" % bbb_crc)
        if opt.Algorithm & opt.Algo_Bit_by_Bit_Fast:
            sys.stderr.write("       bit-by-bit-fast:   0x%x\n" % bbf_crc)
        if opt.Algorithm & opt.Algo_Table_Driven:
            sys.stderr.write("       table_driven:      0x%x\n" % tbl_crc)
        sys.exit(1)
    return crc


# function check_hexstring
###############################################################################
def check_hexstring(opt):
    """
    Return the calculated CRC sum of a hex string.
    """
    if opt.UndefinedCrcParameters:
        sys.stderr.write("%s: error: undefined parameters\n" % sys.argv[0])
        sys.exit(1)
    if len(opt.CheckString) % 2 != 0:
        opt.CheckString = "0" + opt.CheckString
    if sys.version_info >= (3,0):
        opt.CheckString = bytes(opt.CheckString, 'UTF-8')
    try:
        check_str = binascii.unhexlify(opt.CheckString)
    except TypeError:
        sys.stderr.write("%s: error: invalid hex string %s\n" % (sys.argv[0], opt.CheckString))
        sys.exit(1)

    opt.CheckString = check_str
    return check_string(opt)


# function crc_file_update
###############################################################################
def crc_file_update(alg, register, check_byte_str):
    """
    Update the CRC using the bit-by-bit-fast CRC algorithm.
    """
    for octet in check_byte_str:
        if not isinstance(octet, int):
            # Python 2.x compatibility
            octet = ord(octet)
        if alg.ReflectIn:
            octet = alg.reflect(octet, 8)
        for j in range(8):
            bit = register & alg.MSB_Mask
            register <<= 1
            if octet & (0x80 >> j):
                bit ^= alg.MSB_Mask
            if bit:
                register ^= alg.Poly
        register &= alg.Mask
    return register


# function check_file
###############################################################################
def check_file(opt):
    """
    Calculate the CRC of a file.
    This algorithm uses the table_driven CRC algorithm.
    """
    if opt.UndefinedCrcParameters:
        sys.stderr.write("%s: error: undefined parameters\n" % sys.argv[0])
        sys.exit(1)
    alg = Crc(width = opt.Width, poly = opt.Poly,
        reflect_in = opt.ReflectIn, xor_in = opt.XorIn,
        reflect_out = opt.ReflectOut, xor_out = opt.XorOut,
        table_idx_width = opt.TableIdxWidth)

    try:
        in_file = open(opt.CheckFile, 'rb')
    except IOError:
        sys.stderr.write("%s: error: can't open file %s\n" % (sys.argv[0], opt.CheckFile))
        sys.exit(1)

    if not opt.ReflectIn:
        register = opt.XorIn
    else:
        register = alg.reflect(opt.XorIn, opt.Width)
    # Read bytes from the file.
    check_byte_str = in_file.read()
    while check_byte_str:
        register = crc_file_update(alg, register, check_byte_str)
        check_byte_str = in_file.read()
    in_file.close()

    if opt.ReflectOut:
        register = alg.reflect(register, opt.Width)
    register = register ^ opt.XorOut
    return register


# main function
###############################################################################
def main():
    """
    Main function.
    """
    opt = Options()
    opt.parse(sys.argv[1:])
    if opt.Verbose:
        print(print_parameters(opt))
    if opt.Action == opt.Action_Check_String:
        crc = check_string(opt)
        print("0x%x" % crc)
    if opt.Action == opt.Action_Check_Hex_String:
        crc = check_hexstring(opt)
        print("0x%x" % crc)
    if opt.Action == opt.Action_Check_File:
        crc = check_file(opt)
        print("0x%x" % crc)
    if opt.Action in set([opt.Action_Generate_H, opt.Action_Generate_C, opt.Action_Generate_C_Main, opt.Action_Generate_Table]):
        mp = MacroParser(opt)
        if opt.Action == opt.Action_Generate_H:
            in_str = "$h_template"
        elif opt.Action == opt.Action_Generate_C:
            in_str = "$c_template"
        elif opt.Action == opt.Action_Generate_C_Main:
            in_str = "$c_template\n\n$main_template"
        elif opt.Action == opt.Action_Generate_Table:
            in_str = "$crc_table_init"
        else:
            sys.stderr.write("%s: error: unknown action. Please file a bug report!\n" % sys.argv[0])
            sys.exit(1)
        mp.parse(in_str)
        if opt.OutputFile == None:
            print(mp.out_str)
        else:
            try:
                out_file = open(opt.OutputFile, "w")
                out_file.write(mp.out_str)
                out_file.close()
            except IOError:
                sys.stderr.write("%s: error: cannot write to file %s\n" % (sys.argv[0], opt.OutputFile))
                sys.exit(1)
    return 0


# program entry point
###############################################################################
if __name__ == "__main__":
    sys.exit(main())
