import crcSuiteFor from './test_helpers';
import crc81wire from '../lib/es6/crc81wire';

describe('CRC8 1 Wire', function() {
  crcSuiteFor({ crc: crc81wire });
});
