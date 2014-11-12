//  Copyright (c) 2006-2013  Thomas Pircher  <tehpeh@gmx.net>
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in
//  all copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
//  THE SOFTWARE.

#include "crc.h"
#include <getopt.h>
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <stdbool.h>
#include <string.h>

static bool atob(const char *str);
static crc_t xtoi(const char *str);
static int get_config(int argc, char *argv[], crc_cfg_t *cfg);
#if CRC_ALGO_BIT_BY_BIT
static crc_t crc_verify(const crc_cfg_t *cfg, crc_t crc_pre_final, crc_t crc);
static crc_t crc_reflect(crc_t data, size_t data_len);
#endif



static bool verbose = false;
static unsigned char str[256] = "123456789";

bool atob(const char *str)
{
    if (!str) {
        return 0;
    }
    if (isdigit(str[0])) {
        return (bool)atoi(str);
    }
    if (tolower(str[0]) == 't') {
        return true;
    }
    return false;
}

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


int get_config(int argc, char *argv[], crc_cfg_t *cfg)
{
    int c;
    int option_index;
    static struct option long_options[] = {
        {"width",           1, 0, 'w'},
        {"poly",            1, 0, 'p'},
        {"reflect-in",      1, 0, 'n'},
        {"xor-in",          1, 0, 'i'},
        {"reflect-out",     1, 0, 'u'},
        {"xor-out",         1, 0, 'o'},
        {"verbose",         0, 0, 'v'},
        {"check-string",    1, 0, 's'},
        {"table-idx-with",  1, 0, 't'},
        {0, 0, 0, 0}
    };

    while (1) {
        option_index = 0;

        c = getopt_long(argc, argv, "w:p:ni:uo:v", long_options, &option_index);
        if (c == -1)
            break;

        switch (c) {
            case 0:
                printf("option %s", long_options[option_index].name);
                if (optarg)
                    printf(" with arg %s", optarg);
                printf ("\n");
            case 'w':
                cfg->width = atoi(optarg);
                break;
            case 'p':
                cfg->poly = xtoi(optarg);
                break;
            case 'n':
                cfg->reflect_in = atob(optarg);
                break;
            case 'i':
                cfg->xor_in = xtoi(optarg);
                break;
            case 'u':
                cfg->reflect_out = atob(optarg);
                break;
            case 'o':
                cfg->xor_out = xtoi(optarg);
                break;
            case 's':
                memcpy(str, optarg, strlen(optarg) < sizeof(str) ? strlen(optarg) + 1 : sizeof(str));
                str[sizeof(str) - 1] = '\0';
                break;
            case 'v':
                verbose = true;
                break;
            case 't':
                // ignore --table_idx_width option
                break;
            case '?':
                return -1;
            case ':':
                fprintf(stderr, "missing argument to option %c\n", c);
                return -1;
            default:
                fprintf(stderr, "unhandled option %c\n", c);
                return -1;
        }
    }
    cfg->msb_mask = (crc_t)1u << (cfg->width - 1);
    cfg->crc_mask = (cfg->msb_mask - 1) | cfg->msb_mask;
    cfg->crc_shift = cfg->width < 8 ? 8 - cfg->width : 0;

    cfg->poly &= cfg->crc_mask;
    cfg->xor_in &= cfg->crc_mask;
    cfg->xor_out &= cfg->crc_mask;
    return 0;
}


#if CRC_ALGO_BIT_BY_BIT
crc_t crc_verify(const crc_cfg_t *cfg, crc_t crc_pre_final, crc_t crc)
{
    crc_t result;
    unsigned char data;
    unsigned int i;

    // don't verify if the width is not a multiple of 8
    if (cfg->width % 8) {
        return 0;
    }
    if (cfg->xor_out) {
        crc ^= cfg->xor_out;
    }
    if (cfg->reflect_out) {
        crc = crc_reflect(crc, cfg->width);
    }
    result = crc_pre_final;
    for (i = 0; i < cfg->width / 8; i++) {
        data = (crc >> (cfg->width - 8 * i - 8)) & 0xff;
        if (cfg->reflect_in) {
            data = crc_reflect(data, 8);
        }
        result = crc_update(cfg, result, &data, 1);
    }
    // no crc_finalize, because if the CRC calculation is correct, result == 0.
    // A crc_finalize would XOR-in again some ones into the solution.
    // In theory the finalize function of the bit-by-bit algorithm
    // would also loop over cfg->width zero bits, but since
    // a) result == 0, and
    // b) input data == 0
    // the output would always be zero
    return result;
}

crc_t crc_reflect(crc_t data, size_t data_len)
{
    unsigned int i;
    crc_t ret;

    ret = 0;
    for (i = 0; i < data_len; i++)
    {
        if (data & 0x01) {
            ret = (ret << 1) | 1;
        } else {
            ret = ret << 1;
        }
        data >>= 1;
    }
    return ret;
}
#endif       // CRC_ALGO_BIT_BY_BIT


int main(int argc, char *argv[])
{
    crc_cfg_t cfg = {
        0,      // width
        0,      // poly
        0,      // xor_in
        0,      // reflect_in
        0,      // xor_out
        0,      // reflect_out

        0,      // crc_mask
        0,      // msb_mask
        0,      // crc_shift
    };
    crc_t crc;
    crc_t crc_test, crc_pre_final;
    char format[20];
    int ret, i;

    ret = get_config(argc, argv, &cfg);
    if (ret == 0) {
#       if CRC_ALGO_TABLE_DRIVEN
        crc_table_gen(&cfg);
#       endif       // CRC_ALGO_TABLE_DRIVEN
        crc = crc_init(&cfg);
        crc = crc_pre_final = crc_update(&cfg, crc, str, strlen((char *)str));
        crc = crc_finalize(&cfg, crc);

#       if CRC_ALGO_BIT_BY_BIT
        if (crc_verify(&cfg, crc_pre_final, crc) != 0) {
            fprintf(stderr, "error: crc verification failed\n");
            return 1;
        }
#       endif

        // calculate the checksum again, but this time loop over the input
        // bytes one-by-one.
        crc_test = crc_init(&cfg);
        for (i = 0; str[i]; i++)
        {
            crc_test = crc_update(&cfg, crc_test, str + i, 1);
        }
        crc_test = crc_finalize(&cfg, crc_test);
        if (crc_test != crc) {
            fprintf(stderr, "error: crc loop verification failed\n");
            return 1;
        }

        if (verbose) {
            snprintf(format, sizeof(format), "%%-16s = 0x%%0%dx\n", (unsigned int)(cfg.width + 3) / 4);
            printf("%-16s = %d\n", "width", (unsigned int)cfg.width);
            printf(format, "poly", (unsigned int)cfg.poly);
            printf("%-16s = %s\n", "reflect_in", cfg.reflect_in ? "true": "false");
            printf(format, "xor_in", cfg.xor_in);
            printf("%-16s = %s\n", "reflect_out", cfg.reflect_out ? "true": "false");
            printf(format, "xor_out", (unsigned int)cfg.xor_out);
            printf(format, "crc_mask", (unsigned int)cfg.crc_mask);
            printf(format, "msb_mask", (unsigned int)cfg.msb_mask);
        }
        printf("0x%llx\n", (unsigned long long int)crc);
    }
    return !ret;
}
