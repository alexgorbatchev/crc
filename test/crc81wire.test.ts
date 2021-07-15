import crcSuiteFor from './test_helpers';
import crc81wire from '../src/crc81wire';

describe('CRC8 1 Wire', () => {
  crcSuiteFor({ crc: crc81wire });
});
