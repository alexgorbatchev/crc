import crcSuiteFor from './test_helpers';
import crc16kermit from '../lib/es6/crc16kermit';

describe('CRC16KERMIT', () => {
  crcSuiteFor({ crc: crc16kermit });
});
