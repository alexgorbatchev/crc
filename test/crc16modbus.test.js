import crcSuiteFor from './test_helpers';
import crc16modbus from '../lib/es6/crc16modbus';

describe('CRC16Modbus', function() {
  crcSuiteFor({ crc: crc16modbus });
});
