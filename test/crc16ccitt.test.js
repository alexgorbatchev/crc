import crcSuiteFor from './test_helpers';
import crc16ccitt from '../lib/es6/crc16ccitt';

describe('CRC16CCITT', function() {
  crcSuiteFor({ crc: crc16ccitt });
});
