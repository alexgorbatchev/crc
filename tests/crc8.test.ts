import crcSuiteFor from './test_helpers';
import crc8 from './.build/crc8';

describe('CRC8', () => {
  crcSuiteFor({ crc: crc8 });
});
