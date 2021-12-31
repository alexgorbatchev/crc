import crcSuiteFor from './test_helpers';
import crc16ccitt from './.build/crc16ccitt';

describe('CRC16CCITT', () => {
  crcSuiteFor({ crc: crc16ccitt });
});
