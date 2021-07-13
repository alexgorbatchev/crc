import chai from 'chai';

import { crc32 as crc32mod, crc16kermit as crc16kermitMod } from '..';
import crc32src from '../crc32';
import crc32lib from '../lib/es6/crc32';
import crc16kermitSrc from '../crc16kermit';
import crc16kermitLib from '../lib/es6/crc16kermit';

chai.should();

describe('Module imports', () => {
  describe("Functions from a 'crc/src/' file behave the same as functions from the module", () => {
    it('crc32', () => {
      crc32mod('1234567890').should.equal(crc32src('1234567890'));
    });
    it('crc16kermit', () => {
      crc16kermitMod('1234567890').should.equal(crc16kermitSrc('1234567890'));
    });
  });

  describe("Transpiled functions from 'crc/lib/foo' behave the same as module functions", () => {
    it('crc32', () => {
      crc32mod('1234567890').should.equal(crc32lib('1234567890'));
    });
    it('crc16kermit', () => {
      crc16kermitMod('1234567890').should.equal(crc16kermitLib('1234567890'));
    });
  });
});
