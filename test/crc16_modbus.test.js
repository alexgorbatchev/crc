import crcSuiteFor from './test_helpers';
import crc16_modbus from '../lib/es6/crc16_modbus';

describe('CRC16Modbus', function() {
  crcSuiteFor({ crc: crc16_modbus });
});
