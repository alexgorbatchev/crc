import { CRCCalculator } from '../types';

const crc16xmodem: CRCCalculator<Uint8Array> = (current, previous) => {
  let crc = typeof previous !== 'undefined' ? ~~previous : 0x0;

  for (let index = 0; index < current.length; index++) {
    let code = (crc >>> 8) & 0xff;

    code ^= current[index] & 0xff;
    code ^= code >>> 4;
    crc = (crc << 8) & 0xffff;
    crc ^= code;
    code = (code << 5) & 0xffff;
    crc ^= code;
    code = (code << 7) & 0xffff;
    crc ^= code;
  }

  return crc;
};

export default crc16xmodem;
