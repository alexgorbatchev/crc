import {crcSuiteFor} from './test_helpers';

describe('CRC16CCITT', function() {
  crcSuiteFor({crc: require('../lib/crc16_ccitt')});
});
