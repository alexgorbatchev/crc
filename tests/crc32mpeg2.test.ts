import crcSuiteFor from './test_helpers';
import crc32mpeg2 from './.build/crc32mpeg2';

describe('CRC32 MPEG-2', () => {
  crcSuiteFor({ crc: crc32mpeg2 });
});
