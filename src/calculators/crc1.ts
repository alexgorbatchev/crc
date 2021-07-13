import { CRCCalculator } from '../types';

const crc1: CRCCalculator<Uint8Array> = (current, previous) => {
  let crc = ~~previous;
  let accum = 0;

  for (let index = 0; index < current.length; index++) {
    accum += current[index];
  }

  crc += accum % 256;

  return crc % 256;
};

export default crc1;
