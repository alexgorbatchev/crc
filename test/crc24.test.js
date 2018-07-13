import crcSuiteFor from './test_helpers';
import crc24 from '../lib/es6/crc24';

describe('CRC24', function() {
  crcSuiteFor({ crc: crc24 });
});
