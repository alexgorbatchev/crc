import crcSuiteFor from './test_helpers';
import crc16xmodem from '../lib/es6/crc16xmodem';

describe('CRC16XModem', () => {
  crcSuiteFor({ crc: crc16xmodem });
});
