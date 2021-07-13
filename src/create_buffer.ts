import { Buffer } from 'buffer';

const createBuffer =
  Buffer.hasOwnProperty('from') &&
  Buffer.hasOwnProperty('alloc') &&
  Buffer.hasOwnProperty('allocUnsafe') &&
  Buffer.hasOwnProperty('allocUnsafeSlow')
    ? Buffer.from
    : // support for Node < 5.10
      // eslint-disable-next-line no-buffer-constructor
      (val: string) => new Buffer(val);

export default createBuffer;
