import crcSuiteFor from './test_helpers';
import crc32mpeg from './.build/crc32mpeg';

describe('CRC32 MPEG', () => {
  crcSuiteFor({ crc: crc32mpeg });
});
