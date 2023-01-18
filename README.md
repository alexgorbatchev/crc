# crc

Functions for calculating Cyclic Redundancy Checks (CRC) values for the Node.js and front-end.

## Features

- Written in TypeScript and provides typings out of the box.
- Supports ESM and CommonJS.
- Pure JavaScript implementation, no native dependencies.
- Full test suite using `pycrc` as a refenrence.
- Supports for the following CRC algorithms:
  - CRC1 (`crc1`)
  - CRC8 (`crc8`)
  - CRC8 1-Wire (`crc81wire`)
  - CRC8 DVB-S2 (`crc8dvbs2`)
  - CRC16 (`crc16`)
  - CRC16 CCITT (`crc16ccitt`)
  - CRC16 Modbus (`crc16modbus`)
  - CRC16 Kermit (`crc16kermit`)
  - CRC16 XModem (`crc16xmodem`)
  - CRC24 (`crc24`)
  - CRC32 (`crc32`)
  - CRC32 MPEG-2 (`crc32mpeg`)
  - CRCJAM (`crcjam`)

## Installation

```
npm install crc
```

## Usage

Using specific CRC is the recommended way to reduce bundle size:

```js
import crc32 from 'crc/crc32';
crc32('hello').toString(16);
// "3610a686"
```

Alternatively you can use main default export:

```js
import crc from 'crc';
crc.crc32('hello').toString(16);
// "3610a686"
```

If you really wish to minimize bundle size, you can import CRC calculators directly and pass an instance of `Int8Array`:

```js
import crc32 from 'crc/calculators/crc32';
const helloWorld = new Int8Array([104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]);
crc32(helloWorld).toString(16);
// "3610a686"
```

CommonJS is supported as well without the need to unwrap `.default`:

```js
const crc32 = require('crc/crc32');
crc32('hello').toString(16);
// "3610a686"
```

Calculate a CRC32 of a file:

```js
crc32(fs.readFileSync('README.md', 'utf-8')).toString(16);
// "127ad531"
```

Or using a `Buffer`:

```js
crc32(fs.readFileSync('README.md', 'utf-8')).toString(16);
// "127ad531"
```

Incrementally calculate a CRC:

```js
let value = crc32('one');
value = crc32('two', value);
value = crc32('three', value);
value.toString(16);
// "9e1c092"
```

## Tests

```
npm test
```

## Thanks!

[pycrc](http://www.tty1.net/pycrc/) library is which the source of all of the CRC tables.

# License

The MIT License (MIT)

Copyright (c) 2014 Alex Gorbatchev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
