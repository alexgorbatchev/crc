#!/usr/bin/env ./nodeunit/bin/nodeunit

var crc = require('../lib/crc');
var fs = require('fs');

describe('crc8()', function(){
  it('should work with strings', function(){
    crc.crc8('hello world').should.equal(64);
  })

  it('should work with Buffers', function(){
    crc.buffer.crc8(new Buffer('hello world')).should.equal(64);
  })

  it('should work with Streams', function(done){
    var stream = fs.createReadStream('./test/hello_world.txt');
    crc.stream.crc8(stream, function(err, val) {
      if (err) throw err;
      val.should.equal(64);
      done();
    });
  })
})

describe('crc16()', function(){
  it('should work with strings', function(){
    crc.crc16('hello world').should.equal(15332);
  })

  it('should work with Buffers', function(){
    crc.buffer.crc16(new Buffer('hello world')).should.equal(15332);
  })

  it('should work with Streams', function(done){
    var stream = fs.createReadStream('./test/hello_world.txt');
    crc.stream.crc16(stream, function(err, val) {
      if (err) throw err;
      val.should.equal(15332);
      done();
    });
  })
})

describe('crc32()', function(){
  it('should work with strings', function(){
    crc.crc32('hello world').should.equal(222957957);
  })

  it('should work with Buffers', function(){
    crc.buffer.crc32(new Buffer('hello world')).should.equal(222957957);
  })

  it('should work with Streams', function(done){
    var stream = fs.createReadStream('./test/hello_world.txt');
    crc.stream.crc32(stream, function(err, val) {
      if (err) throw err;
      val.should.equal(222957957);
      done();
    });
  })
})

describe('crcArc()', function(){
  it('should work with strings', function(){
    crc.crcArc('hello world').should.equal(14785);
  })
})

describe('fcs16()', function(){
  it('should work with strings', function(){
    crc.fcs16('hello world').should.equal(44550);
  })
})

describe('hex8()', function(){
  it('should work with strings', function(){
    crc.hex8(64).should.equal('40');
  })
})

describe('hex16()', function(){
  it('should work with strings', function(){
    crc.hex16(15332).should.equal('3BE4');
  })
})

describe('hex32()', function(){
  it('should work with strings', function(){
    crc.hex32(222957957).should.equal('0D4A1185');
  })
})
