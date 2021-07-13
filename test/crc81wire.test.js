import crcSuiteFor from './test_helpers';
import crc81wire from '../lib/es6/crc81wire';

describe('CRC8 1 Wire', () => {
  crcSuiteFor({ crc: crc81wire });
});
