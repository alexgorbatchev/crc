import crcSuiteFor from './test_helpers';
import crc16kermit from '../src/crc16kermit';

describe('CRC16KERMIT', () => {
  crcSuiteFor({ crc: crc16kermit });
});
