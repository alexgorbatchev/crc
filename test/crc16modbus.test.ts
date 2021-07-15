import crcSuiteFor from './test_helpers';
import crc16modbus from '../src/crc16modbus';

describe('CRC16Modbus', () => {
  crcSuiteFor({ crc: crc16modbus });
});
