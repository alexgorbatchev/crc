import crc16xmodem from './calculators/crc16xmodem.js';
import defineCrc from './define_crc.js';

export default defineCrc('xmodem', crc16xmodem);
