import {crcSuiteFor} from './test_helpers';

describe('CRC16XModem', function() {
  crcSuiteFor({crc: require('../lib/crc16_xmodem')});
});
