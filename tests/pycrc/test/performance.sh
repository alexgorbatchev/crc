#!/bin/bash
set -e

PYCRC=`dirname $0`/../pycrc.py

function cleanup {
    rm -f a.out performance.c crc_bbb.[ch] crc_bbf.[ch] crc_tb[l4].[ch] crc_bw[e4].[ch]
}

trap cleanup 0 1 2 3 15


prefix=bbb
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo bit-by-bit
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo bit-by-bit
prefix=bbf
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo bit-by-bit-fast
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo bit-by-bit-fast
prefix=tbl
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo table-driven
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo table-driven
prefix=tb4
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo table-driven --table-idx-width 4
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo table-driven --table-idx-width 4
prefix=bwe
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo bitwise-expression
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo bitwise-expression
prefix=bw4
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate h -o crc_$prefix.h --algo bitwise-expression --table-idx-width 4
$PYCRC --model crc-32 --symbol-prefix crc_${prefix}_ --generate c -o crc_$prefix.c --algo bitwise-expression --table-idx-width 4


function print_main {
cat <<EOF
#include "crc_bbb.h"
#include "crc_bbf.h"
#include "crc_tbl.h"
#include "crc_tb4.h"
#include "crc_bwe.h"
#include "crc_bw4.h"
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <sys/times.h>
#include <unistd.h>

#define NUM_RUNS    (256*256)

unsigned char buf[1024];

void test_bbb(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_bbf(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_tbl(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_tb4(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_bwe(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);
void test_bw4(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec);

/**
 * Print results.
 *
 * \param   dsc Description of the test
 * \param   crc Resulting CRC
 * \param   buflen Length of one buffer
 * \param   num_runs Number of runs over that buffer
 * \param   t_user user time
 * \param   t_sys system time
 * \return  void
 *****************************************************************************/
void show_times(const char *dsc, unsigned int crc, size_t buflen, size_t num_runs, double t_user, double t_sys)
{
    printf("%s of %ld bytes (%ld * %ld): 0x%08x\n", dsc, (long)buflen*num_runs, (long)buflen, (long)num_runs, crc);
    printf("%13s: %7.3f s\n", "user time", t_user);
    printf("%13s: %7.3f s\n", "system time", t_sys);
    printf("\n");
}


/**
 * C main function.
 *
 * \retval      0 on success
 * \retval      1 on failure
 *****************************************************************************/
int main(void)
{
    unsigned int i;
    long int clock_per_sec;

    for (i = 0; i < sizeof(buf); i++) {
        buf[i] = (unsigned char)rand();
    }
    clock_per_sec = sysconf(_SC_CLK_TCK);

    // bit-by-bit
    test_bbb(buf, sizeof(buf), NUM_RUNS, clock_per_sec);

    // bit-by-bit-fast
    test_bbf(buf, sizeof(buf), NUM_RUNS, clock_per_sec);

    // table-driven
    test_tbl(buf, sizeof(buf), NUM_RUNS, clock_per_sec);

    // table-driven idx4
    test_tb4(buf, sizeof(buf), NUM_RUNS, clock_per_sec);

    // bitwise-expression
    test_bwe(buf, sizeof(buf), NUM_RUNS, clock_per_sec);

    // table-driven idx4
    test_bw4(buf, sizeof(buf), NUM_RUNS, clock_per_sec);

    return 0;
}
EOF
}

function print_routine {
    algo=$1
    prefix=$2
    cat <<EOF
/**
 * Test $algo Algorithm.
 *
 * \return      void
 *****************************************************************************/
void test_${prefix}(unsigned char *buf, size_t buf_len, size_t num_runs, clock_t clock_per_sec)
{
    crc_${prefix}_t crc;
    unsigned int i, j;
    struct tms tm1, tm2;

    times(&tm1);
    crc = crc_${prefix}_init();
    for (i = 0; i < num_runs; i++) {
        crc = crc_${prefix}_update(crc, buf, buf_len);
    }
    crc = crc_${prefix}_finalize(crc);
    times(&tm2);
    show_times("CRC32, $algo, block-wise", crc, buf_len, num_runs,
            ((double)(tm2.tms_utime - tm1.tms_utime) / (double)clock_per_sec),
            ((double)(tm2.tms_stime - tm1.tms_stime) / (double)clock_per_sec));

    times(&tm1);
    crc = crc_${prefix}_init();
    for (i = 0; i < num_runs; i++) {
        for (j = 0; j < buf_len; j++) {
            crc = crc_${prefix}_update(crc, &buf[j], 1);
        }
    }
    crc = crc_${prefix}_finalize(crc);
    times(&tm2);
    show_times("CRC32, $algo, byte-wise", crc, buf_len, num_runs,
            ((double)(tm2.tms_utime - tm1.tms_utime) / (double)clock_per_sec),
            ((double)(tm2.tms_stime - tm1.tms_stime) / (double)clock_per_sec));
}

EOF
}

print_main > performance.c
print_routine "bit-by-bit" bbb >> performance.c
print_routine "bit-by-bit-fast" bbf >> performance.c
print_routine "table-driven" tbl >> performance.c
print_routine "table-driven idx4" tb4 >> performance.c
print_routine "bitwise-expression" bwe >> performance.c
print_routine "bitwise-expression idx4" bw4 >> performance.c

gcc -W -Wall -O3 crc_bbb.c crc_bbf.c crc_tbl.c crc_tb4.c crc_bwe.c crc_bw4.c performance.c
./a.out
