import crcSuiteFor from './test_helpers';
import crc16ccitt from '../src/crc16ccitt';

describe('CRC16CCITT', () => {
  crcSuiteFor({ crc: crc16ccitt });
});
