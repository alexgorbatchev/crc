import crc32 from 'crc/calculators/crc32';

const helloWorld = new Uint8Array([104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]);

// eslint-disable-next-line no-console
console.log(crc32(helloWorld));
