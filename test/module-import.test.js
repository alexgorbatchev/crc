
import crc32_src from '../src/crc32';
import { crc32 as crc32_mod } from '../lib/index';
import crc32_lib from '../lib/crc32';

import crc16kermit_src from '../src/crc16_kermit';
import { crc16kermit as crc16kermit_mod } from '../lib/index';
import crc16kermit_lib from '../lib/crc16_kermit';

import chai from 'chai';

chai.should();

describe('Module imports', function() {
    describe('"import foo from \'crc\'" equals "import foo from \'crc/src/foo\'" ', function(){
        it('crc32', function() {
            crc32_mod.should.equal(crc32_src);
        });
        it('crc16_kermit', function() {
            crc16kermit_mod.should.equal(crc16kermit_src);
        });
    });
    describe('Transpiled functions from \'crc/lib/foo\' behave the same as module functions', function(){
        it('crc32', function() {
            crc32_mod("1234567890").should.equal(crc32_lib("1234567890"));
        });
        it('crc16_kermit', function() {
            crc16kermit_mod("1234567890").should.equal(crc16kermit_lib("1234567890"));
        });
    });
});

