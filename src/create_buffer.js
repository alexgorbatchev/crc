import {Buffer} from 'buffer';

const createBuffer = typeof Buffer.from === 'function'
  ? Buffer.from

  // support for Node < 5.10
  : val => new Buffer(val)
  ;

export default createBuffer;
