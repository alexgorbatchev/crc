#!/usr/bin/env ./nodeunit/bin/nodeunit

var crc = require('../lib/crc');

describe('crc8()', function(){
  it('should work with strings', function(){
    crc.crc8('hello world').should.equal(64);
  })
})