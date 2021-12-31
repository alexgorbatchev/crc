import crcSuiteFor from './test_helpers';
import crc32 from './.build/crc32';

describe('CRC32', () => {
  crcSuiteFor({ crc: crc32 });
});
