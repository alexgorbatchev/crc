import crcSuiteFor from './test_helpers';
import crc81wire from './.build/crc81wire';

describe('CRC8 1 Wire', () => {
  crcSuiteFor({ crc: crc81wire });
});
