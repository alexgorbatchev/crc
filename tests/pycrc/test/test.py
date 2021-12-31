#!/usr/bin/env python
# -*- coding: Latin-1 -*-

#  pycrc test application.

from optparse import OptionParser, Option, OptionValueError
from copy import copy
import os, sys, commands
import tempfile
sys.path.append("..")
from crc_models import CrcModels
from crc_algorithms import Crc


class Options(object):
    """
    The options parsing and validating class
    """

    def __init__(self):
        self.AllAlgorithms          = set(["bit-by-bit", "bbb", "bit-by-bit-fast", "bbf", "bitwise-expression", "bwe", "table-driven", "tbl"])
        self.Compile                = False
        self.RandomParameters       = False
        self.CompileMixedArgs       = False
        self.VariableWidth          = False
        self.Verbose                = False
        self.Python3                = False
        self.Algorithm = copy(self.AllAlgorithms)

    def parse(self, argv = None):
        """
        Parses and validates the options given as arguments
        """
        usage = """%prog [OPTIONS]"""

        models = CrcModels()
        model_list = ", ".join(models.getList())
        algorithms = ", ".join(sorted(list(self.AllAlgorithms)) + ["all"])
        parser = OptionParser(usage=usage)
        parser.add_option("-v", "--verbose",
                        action="store_true", dest="verbose", default=self.Verbose,
                        help="print information about the model")
        parser.add_option("-3", "--python3",
                        action="store_true", dest="python3", default=self.Python3,
                        help="use Python3.x")
        parser.add_option("-c", "--compile",
                        action="store_true", dest="compile", default=self.Compile,
                        help="test compiled version")
        parser.add_option("-r", "--random-parameters",
                        action="store_true", dest="random_parameters", default=self.RandomParameters,
                        help="test random parameters")
        parser.add_option("-m", "--compile-mixed-arguments",
                        action="store_true", dest="compile_mixed_args", default=self.CompileMixedArgs,
                        help="test compiled C program with some arguments given at compile time some arguments given at runtime")
        parser.add_option("-w", "--variable-width",
                        action="store_true", dest="variable_width", default=self.VariableWidth,
                        help="test variable width from 1 to 64")
        parser.add_option("-a", "--all",
                        action="store_true", dest="all", default=False,
                        help="do all tests")
        parser.add_option("--algorithm",
                        action="store", type="string", dest="algorithm", default="all",
                        help="choose an algorithm from {%s}" % algorithms, metavar="ALGO")

        (options, args) = parser.parse_args(argv)

        self.Verbose = options.verbose
        self.Python3 = options.python3
        self.Compile = options.all or options.compile or options.random_parameters
        self.RandomParameters = options.all or options.random_parameters
        self.CompileMixedArgs = options.all or options.compile_mixed_args
        self.VariableWidth = options.all or options.variable_width

        if options.algorithm is not None:
            alg = options.algorithm.lower()
            if alg in self.AllAlgorithms:
                self.Algorithm = set([alg])
            elif alg == "all":
                self.Algorithm = copy(self.AllAlgorithms)
            else:
                sys.stderr.write("unknown algorithm: %s\n" % alg)
                sys.exit(1)


class CrcTests(object):
    """
    The CRC test class.
    """

    def __init__(self):
        """
        The class constructor.
        """
        self.pycrc_bin = "/bin/false"
        self.use_algo_bit_by_bit = True
        self.use_algo_bit_by_bit_fast = True
        self.use_algo_table_driven = True
        self.use_algo_bitwise_expression = True
        self.verbose = False
        self.tmpdir = tempfile.mkdtemp(prefix="pycrc.")
        self.check_file = None
        self.crc_bin_bbb_c89 = None
        self.crc_bin_bbb_c99 = None
        self.crc_bin_bbf_c89 = None
        self.crc_bin_bbf_c99 = None
        self.crc_bin_bwe_c89 = None
        self.crc_bin_bwe_c99 = None
        self.crc_bin_tbl_c89 = None
        self.crc_bin_tbl_c99 = None
        self.crc_bin_tbl_idx2 = None
        self.crc_bin_tbl_idx4 = None

    def __del__(self):
        """
        The class destructor. Delete all generated files.
        """
        if self.check_file is not None:
            os.remove(self.check_file)
        if self.crc_bin_bbb_c89 is not None:
            self.__del_files([self.crc_bin_bbb_c89, self.crc_bin_bbb_c89+".h", self.crc_bin_bbb_c89+".c"])
        if self.crc_bin_bbb_c99 is not None:
            self.__del_files([self.crc_bin_bbb_c99, self.crc_bin_bbb_c99+".h", self.crc_bin_bbb_c99+".c"])
        if self.crc_bin_bbf_c89 is not None:
            self.__del_files([self.crc_bin_bbf_c89, self.crc_bin_bbf_c89+".h", self.crc_bin_bbf_c89+".c"])
        if self.crc_bin_bbf_c99 is not None:
            self.__del_files([self.crc_bin_bbf_c99, self.crc_bin_bbf_c99+".h", self.crc_bin_bbf_c99+".c"])
        if self.crc_bin_bwe_c89 is not None:
            self.__del_files([self.crc_bin_bwe_c89, self.crc_bin_bwe_c89+".h", self.crc_bin_bwe_c89+".c"])
        if self.crc_bin_bwe_c99 is not None:
            self.__del_files([self.crc_bin_bwe_c99, self.crc_bin_bwe_c99+".h", self.crc_bin_bwe_c99+".c"])
        if self.crc_bin_tbl_c89 is not None:
            self.__del_files([self.crc_bin_tbl_c89, self.crc_bin_tbl_c89+".h", self.crc_bin_tbl_c89+".c"])
        if self.crc_bin_tbl_c99 is not None:
            self.__del_files([self.crc_bin_tbl_c99, self.crc_bin_tbl_c99+".h", self.crc_bin_tbl_c99+".c"])
        if self.crc_bin_tbl_idx2 is not None:
            self.__del_files([self.crc_bin_tbl_idx2, self.crc_bin_tbl_idx2+".h", self.crc_bin_tbl_idx2+".c"])
        if self.crc_bin_tbl_idx4 is not None:
            self.__del_files([self.crc_bin_tbl_idx4, self.crc_bin_tbl_idx4+".h", self.crc_bin_tbl_idx4+".c"])
        os.removedirs(self.tmpdir)

    def __del_files(delf, files):
        """
        Helper function to delete files.
        """
        for f in files:
            try:
                os.remove(f)
            except:
                print("error: can't delete %s", f)
                pass

    def __make_src(self, args, basename, cstd):
        """
        Generate the *.h and *.c source files for a test.
        """
        gen_src = "%s/%s" % (self.tmpdir, basename)
        cmd_str = self.pycrc_bin + " %s --std %s --generate h -o %s.h" % (args, cstd, gen_src)
        if self.verbose:
            print(cmd_str)
        ret = commands.getstatusoutput(cmd_str)
        if ret[0] != 0:
            print("error: the following command returned error: %s" % cmd_str)
            print(ret[1])
            print(ret[2])
            return None

        cmd_str = self.pycrc_bin + " %s --std %s --generate c-main -o %s.c" % (args, cstd, gen_src)
        if self.verbose:
            print(cmd_str)
        ret = commands.getstatusoutput(cmd_str)
        if ret[0] != 0:
            print("error: the following command returned error: %s" % cmd_str)
            print(ret[1])
            print(ret[2])
            return None
        return gen_src

    def __compile(self, args, binfile, cstd):
        """
        Compile a generated source file.
        """
        cmd_str = "gcc -W -Wall -pedantic -Werror -std=%s -o %s %s.c" % (cstd, binfile, binfile)
        if self.verbose:
            print(cmd_str)
        ret = commands.getstatusoutput(cmd_str)
        if len(ret) > 1 and len(ret[1]) > 0:
            print(ret[1])
        if ret[0] != 0:
            print("error: %d with command error: %s" % (ret[0], cmd_str))
            return None
        return binfile

    def __make_bin(self, args, basename, cstd="c99"):
        """
        Generate the source and compile to a binary.
        """
        filename = self.__make_src(args, basename, cstd)
        if filename is None:
            return None
        if not self.__compile(args, filename, cstd):
            self.__del_files([filename, filename+".h", filename+".c"])
            return None
        return filename

    def __setup_files(self, opt):
        """
        Set up files needed during the test.
        """
        if self.verbose:
            print("Setting up files...")
        self.check_file = "%s/check.txt" % self.tmpdir
        f = open(self.check_file, "wb")
        f.write("123456789")
        f.close()

        if opt.Compile:
            if self.use_algo_bit_by_bit:
                filename = self.__make_bin("--algorithm bit-by-bit", "crc_bbb_c89", "c89")
                if filename is None:
                    return False
                self.crc_bin_bbb_c89 = filename

                filename = self.__make_bin("--algorithm bit-by-bit", "crc_bbb_c99", "c99")
                if filename is None:
                    return False
                self.crc_bin_bbb_c99 = filename

            if self.use_algo_bit_by_bit_fast:
                filename = self.__make_bin("--algorithm bit-by-bit-fast", "crc_bbf_c89", "c89")
                if filename is None:
                    return False
                self.crc_bin_bbf_c89 = filename

                filename = self.__make_bin("--algorithm bit-by-bit-fast", "crc_bbf_c99", "c99")
                if filename is None:
                    return False
                self.crc_bin_bbf_c99 = filename

            if self.use_algo_table_driven:
                filename = self.__make_bin("--algorithm table-driven", "crc_tbl_c89", "c89")
                if filename is None:
                    return False
                self.crc_bin_tbl_c89 = filename

                filename = self.__make_bin("--algorithm table-driven", "crc_tbl_c99", "c99")
                if filename is None:
                    return False
                self.crc_bin_tbl_c99 = filename

                filename = self.__make_bin("--algorithm table-driven --table-idx-width 2", "crc_tbl_idx2")
                if filename is None:
                    return False
                self.crc_bin_tbl_idx2 = filename

                filename = self.__make_bin("--algorithm table-driven --table-idx-width 4", "crc_tbl_idx4")
                if filename is None:
                    return False
                self.crc_bin_tbl_idx4 = filename

        return True


    def __run_command(self, cmd_str):
        """
        Run a command and return its stdout.
        """
        if self.verbose:
            print(cmd_str)
        ret = commands.getstatusoutput(cmd_str)
        if ret[0] != 0:
            print("error: the following command returned error: %s" % cmd_str)
            print(ret[1])
            print(ret[2])
            return None
        return ret[1]

    def __check_command(self, cmd_str, expected_result):
        """
        Run a command and check if the stdout matches the expected result.
        """
        ret = self.__run_command(cmd_str)
        if int(ret, 16) != expected_result:
            print("error: different checksums!")
            print("%s: expected 0x%x, got %s" %(cmd_str, expected_result, ret))
            return False
        return True

    def __check_bin(self, args, expected_result, long_data_type = True):
        """
        Check all precompiled binaries.
        """
        for binary in [self.crc_bin_bbb_c89, self.crc_bin_bbb_c99, self.crc_bin_bbf_c89, self.crc_bin_bbf_c99, self.crc_bin_tbl_c89, self.crc_bin_tbl_c99, self.crc_bin_tbl_idx2, self.crc_bin_tbl_idx4]:
            if binary is not None:
                # Don't test width > 32 for C89, as I don't know how to ask for an data type > 32 bits.
                if binary[-3:] == "c89" and long_data_type:
                    continue
                cmd_str = binary + " " + args
                if not self.__check_command(cmd_str, expected_result):
                    return False
        return True

    def __get_crc(self, model, check_str = "123456789", expected_crc = None):
        """
        Get the CRC for a set of parameters from the Python reference implementation.
        """
        if self.verbose:
            out_str = "Crc(width = %(width)d, poly = 0x%(poly)x, reflect_in = %(reflect_in)s, xor_in = 0x%(xor_in)x, reflect_out = %(reflect_out)s, xor_out = 0x%(xor_out)x)" % model
            if expected_crc is not None:
                out_str += " [check = 0x%x]" % expected_crc
            print(out_str)
        alg = Crc(width = model["width"], poly = model["poly"],
            reflect_in = model["reflect_in"], xor_in = model["xor_in"],
            reflect_out = model["reflect_out"], xor_out = model["xor_out"])
        error = False
        crc = expected_crc

        if self.use_algo_bit_by_bit:
            bbb_crc = alg.bit_by_bit(check_str)
            if crc is None:
                crc = bbb_crc
            error = error or bbb_crc != crc
        if self.use_algo_bit_by_bit_fast:
            bbf_crc = alg.bit_by_bit_fast(check_str)
            if crc is None:
                crc = bbf_crc
            error = error or bbf_crc != crc
        if self.use_algo_table_driven:
            tbl_crc = alg.table_driven(check_str)
            if crc is None:
                crc = tbl_crc
            error = error or tbl_crc != crc

        if error:
            print("error: different checksums!")
            if expected_crc is not None:
                print("       check:             0x%x" % expected_crc)
            if self.use_algo_bit_by_bit:
                print("       bit-by-bit:        0x%x" % bbb_crc)
            if self.use_algo_bit_by_bit_fast:
                print("       bit-by-bit-fast:   0x%x" % bbf_crc)
            if self.use_algo_table_driven:
                print("       table_driven:      0x%x" % tbl_crc)
            return None
        return crc

    def __compile_and_check_res(self, cmp_opt, run_opt, name, expected_crc):
        """
        Compile a model and run it.
        """
        filename = self.__make_bin(cmp_opt, name)
        if filename is None:
            return False
        if run_opt is None:
            cmd = filename
        else:
            cmd = filename + " " + run_opt
        ret = self.__check_command(cmd, expected_crc)
        self.__del_files([filename, filename+".h", filename+".c"])
        if not ret:
            return False
        return True


    def __test_models(self):
        """
        Standard Tests.
        Test all known models.
        """
        if self.verbose:
            print("Running __test_models()...")
        check_str = "123456789"
        models = CrcModels()
        for m in models.models:
            expected_crc = m["check"]
            if self.__get_crc(m, check_str, expected_crc) != expected_crc:
                return False

            ext_args = "--width %(width)s --poly 0x%(poly)x --xor-in 0x%(xor_in)x --reflect-in %(reflect_in)s --xor-out 0x%(xor_out)x --reflect-out %(reflect_out)s" % m

            cmd_str = self.pycrc_bin + " --model %(name)s" % m
            if not self.__check_command(cmd_str, expected_crc):
                return False

            cmd_str = self.pycrc_bin + " " + ext_args
            if not self.__check_command(cmd_str, expected_crc):
                return False

            cmd_str = self.pycrc_bin + " %s --check-hexstring %s" % (ext_args, "".join(["%02x" % ord(c) for c in check_str]))
            if not self.__check_command(cmd_str, expected_crc):
                return False

            cmd_str = self.pycrc_bin + " --model %s --check-file %s" % (m["name"], self.check_file)
            if not self.__check_command(cmd_str, expected_crc):
                return False

            if not self.__check_bin(ext_args, expected_crc, m["width"] > 32):
                return False

        if self.verbose:
            print("")
        return True


    def __test_compiled_models(self):
        """
        Standard Tests.
        Test all known models with the compiled code
        """
        if self.verbose:
            print("Running __test_compiled_models()...")
        check_str = "123456789"
        models = CrcModels()
        for m in models.models:
            expected_crc = m["check"]
            cmp_opt = "--model %(name)s" % m

            if self.use_algo_bit_by_bit:
                if not self.__compile_and_check_res("--algorithm bit-by-bit" + " " + cmp_opt, None, "crc_bbb_mod", expected_crc):
                    return False

            if self.use_algo_bit_by_bit_fast:
                if not self.__compile_and_check_res("--algorithm bit-by-bit-fast" + " " + cmp_opt, None, "crc_bbf_mod", expected_crc):
                    return False

            if self.use_algo_bitwise_expression:
                if not self.__compile_and_check_res("--algorithm bitwise-expression" + " " + cmp_opt, None, "crc_bwe_mod", expected_crc):
                    return False

            if self.use_algo_table_driven:
                if not self.__compile_and_check_res("--algorithm table-driven" + " " + cmp_opt, None, "crc_tbl_mod", expected_crc):
                    return False

                if not self.__compile_and_check_res("--algorithm table-driven --table-idx-width=2" + " " + cmp_opt, None, "crc_tb2_mod", expected_crc):
                    return False

                if not self.__compile_and_check_res("--algorithm table-driven --table-idx-width=4" + " " + cmp_opt, None, "crc_tb4_mod", expected_crc):
                    return False
        return True


    def __test_compiled_special_cases(self):
        """
        Standard Tests.
        Test some special cases.
        """
        if self.verbose:
            print("Running __test_compiled_special_cases()...")
        if self.use_algo_table_driven:
            if not self.__compile_and_check_res("--model=crc-5 --reflect-in=0 --algorithm table-driven --table-idx-width=8", None, "crc_tbl_special", 0x01):
                return False
            if not self.__compile_and_check_res("--model=crc-5 --reflect-in=0 --algorithm table-driven --table-idx-width=4", None, "crc_tbl_special", 0x01):
                return False
            if not self.__compile_and_check_res("--model=crc-5 --reflect-in=0 --algorithm table-driven --table-idx-width=2", None, "crc_tbl_special", 0x01):
                return False
        return True


    def __test_variable_width(self):
        """
        Test variable width.
        """
        if self.verbose:
            print("Running __test_variable_width()...")
        models = CrcModels()
        m = models.getParams("crc-64-jones")

        for width in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 23, 24, 25, 31, 32, 33, 63, 64]:
            mask = (1 << width) - 1
            mw = {
                'width':         width,
                'poly':          m['poly'] & mask,
                'reflect_in':    m['reflect_in'],
                'xor_in':        m['xor_in'] & mask,
                'reflect_out':   m['reflect_out'],
                'xor_out':       m['xor_out'] & mask,
            }
            args = "--width %(width)s --poly 0x%(poly)x --xor-in 0x%(xor_in)x --reflect-in %(reflect_in)s --xor-out 0x%(xor_out)x --reflect-out %(reflect_out)s" % mw

            check = self.__get_crc(mw)
            if check is None:
                return False

            if self.use_algo_bit_by_bit:
                if self.crc_bin_bbb_c99 is not None:
                    if not self.__check_command(self.crc_bin_bbb_c99 + " " + args, check):
                        return False

                if not self.__compile_and_check_res("--algorithm bit-by-bit" + " " + args, None, "crc_bbb_arg", check):
                    return False

            if self.use_algo_bit_by_bit_fast:
                if self.crc_bin_bbf_c99 is not None:
                    if not self.__check_command(self.crc_bin_bbf_c99 + " " + args, check):
                        return False

                if not self.__compile_and_check_res("--algorithm bit-by-bit-fast" + " " + args, None, "crc_bbf_arg", check):
                    return False

            if self.use_algo_bitwise_expression:
                if self.crc_bin_bwe_c99 is not None:
                    if not self.__check_command(self.crc_bin_bwe_c99 + " " + args, check):
                        return False

                if not self.__compile_and_check_res("--algorithm bitwise-expression" + " " + args, None, "crc_bwe_arg", check):
                    return False

            if self.use_algo_table_driven:
                if self.crc_bin_tbl_c99 is not None:
                    if not self.__check_command(self.crc_bin_tbl_c99 + " " + args, check):
                        return False

                if not self.__compile_and_check_res("--algorithm table-driven" + " " + args, None, "crc_tbl_arg", check):
                    return False
        return True


    def __test_compiled_mixed_args(self):
        """
        Test compiled arguments.
        """
        if self.verbose:
            print("Running __test_compiled_mixed_args()...")
        m =  {
            'name':         'zmodem',
            'width':         ["", "--width 16"],
            'poly':          ["", "--poly 0x1021"],
            'reflect_in':    ["", "--reflect-in False"],
            'xor_in':        ["", "--xor-in 0x0"],
            'reflect_out':   ["", "--reflect-out False"],
            'xor_out':       ["", "--xor-out 0x0"],
            'check':         0x31c3,
        }
        cmp_args = {}
        run_args = {}
        for b_width in range(2):
            cmp_args["width"] = m["width"][b_width]
            run_args["width"] = m["width"][1 - b_width]
            for b_poly in range(2):
                cmp_args["poly"] = m["poly"][b_poly]
                run_args["poly"] = m["poly"][1 - b_poly]
                for b_ref_in in range(2):
                    cmp_args["reflect_in"] = m["reflect_in"][b_ref_in]
                    run_args["reflect_in"] = m["reflect_in"][1 - b_ref_in]
                    for b_xor_in in range(2):
                        cmp_args["xor_in"] = m["xor_in"][b_xor_in]
                        run_args["xor_in"] = m["xor_in"][1 - b_xor_in]
                        for b_ref_out in range(2):
                            cmp_args["reflect_out"] = m["reflect_out"][b_ref_out]
                            run_args["reflect_out"] = m["reflect_out"][1 - b_ref_out]
                            for b_xor_out in range(2):
                                cmp_args["xor_out"] = m["xor_out"][b_xor_out]
                                run_args["xor_out"] = m["xor_out"][1 - b_xor_out]

                                cmp_opt = "%(width)s %(poly)s %(reflect_in)s %(xor_in)s %(reflect_out)s %(xor_out)s" %  cmp_args
                                run_opt = "%(width)s %(poly)s %(reflect_in)s %(xor_in)s %(reflect_out)s %(xor_out)s" %  run_args

                                if self.use_algo_bit_by_bit:
                                    if not self.__compile_and_check_res("--algorithm bit-by-bit" + " " + cmp_opt, run_opt, "crc_bbb_arg", m["check"]):
                                        return False

                                if self.use_algo_bit_by_bit_fast:
                                    if not self.__compile_and_check_res("--algorithm bit-by-bit-fast" + " " + cmp_opt, run_opt, "crc_bbf_arg", m["check"]):
                                        return False

                                if self.use_algo_table_driven:
                                    if not self.__compile_and_check_res("--algorithm table-driven" + " " + cmp_opt, run_opt, "crc_tbl_arg", m["check"]):
                                        return False
        return True


    def __test_random_params(self):
        """
        Test random parameters.
        """
        if self.verbose:
            print("Running __test_random_params()...")
        for width in [8, 16, 32]:
            for poly in [0x8005, 0x4c11db7, 0xa5a5a5a5]:
                for refin in [0, 1]:
                    for refout in [0, 1]:
                        for init in [0x0, 0x1, 0x5a5a5a5a]:
                            args="--width %d --poly 0x%x --reflect-in %s --reflect-out %s --xor-in 0x%x --xor-out 0x0" % (width, poly, refin, refout, init)
                            cmd_str = self.pycrc_bin + " " + args
                            ret = self.__run_command(cmd_str)
                            if ret is None:
                                return False
                            ret = int(ret, 16)
                            if not self.__check_bin(args, ret, width > 32):
                                return False
        return True


    def run(self, opt):
        """
        Run all tests
        """
        self.use_algo_bit_by_bit = "bit-by-bit" in opt.Algorithm or "bbb" in opt.Algorithm
        self.use_algo_bit_by_bit_fast = "bit-by-bit-fast" in opt.Algorithm or "bbf" in opt.Algorithm
        self.use_algo_bitwise_expression = "bitwise-expression" in opt.Algorithm or "bwe" in opt.Algorithm
        self.use_algo_table_driven = "table-driven" in opt.Algorithm or "tbl" in opt.Algorithm
        self.verbose = opt.Verbose

        if opt.Python3:
            self.pycrc_bin = "python3 ../pycrc.py"
        else:
            self.pycrc_bin = "python ../pycrc.py"

        if not self.__setup_files(opt):
            return False

        if not self.__test_models():
            return False

        if opt.Compile and not self.__test_compiled_models():
            return False

        if opt.Compile and not self.__test_compiled_special_cases():
            return False

        if opt.VariableWidth and not self.__test_variable_width():
            return False

        if opt.CompileMixedArgs and not self.__test_compiled_mixed_args():
            return False

        if opt.RandomParameters and not self.__test_random_params():
            return False

        return True


def main():
    """
    Main function.
    """
    opt = Options()
    opt.parse(sys.argv[1:])

    test = CrcTests()
    if not test.run(opt):
        return 1
    print("Test OK")
    return 0


# program entry point
if __name__ == "__main__":
    sys.exit(main())
