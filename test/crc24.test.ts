import crcSuiteFor from './test_helpers';
import crc24 from '../src/crc24';

describe('CRC24', () => {
  crcSuiteFor({ crc: crc24 });
});
