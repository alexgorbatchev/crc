import {crcSuiteFor} from './test_helpers';

describe('CRC16Modbus', function() {
  crcSuiteFor({crc: require('../lib/crc16_modbus')});
});
