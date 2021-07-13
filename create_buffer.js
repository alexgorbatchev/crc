/* eslint-disable operator-linebreak */
import { Buffer } from 'buffer';

const createBuffer = Buffer.from && Buffer.alloc && Buffer.allocUnsafe && Buffer.allocUnsafeSlow
  ? Buffer.from
  : // support for Node < 5.10
  // eslint-disable-next-line no-buffer-constructor
  (val) => new Buffer(val);

export default createBuffer;
