import crcSuiteFor from './test_helpers';
import crc32 from '../src/crc32';

describe('CRC32', () => {
  crcSuiteFor({ crc: crc32 });
});
