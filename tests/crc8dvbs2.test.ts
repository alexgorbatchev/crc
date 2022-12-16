import crcSuiteFor from './test_helpers';
import crc8dvbs2 from './.build/crc8dvbs2';

describe('CRC8 DVB-S2', () => {
  crcSuiteFor({ crc: crc8dvbs2, value: Buffer.from('45A2DFF1', 'hex'), expected: 'f6' });
});
