import {crcSuiteFor} from './test_helpers';
import crc16_xmodem from '../lib/crc16_xmodem';

describe('CRC16XModem', function() {
  crcSuiteFor({crc: crc16_xmodem});
});
