import crcSuiteFor from './test_helpers';
import crc16xmodem from './.build/crc16xmodem';

describe('CRC16XModem', () => {
  crcSuiteFor({ crc: crc16xmodem });
});
