# -*- coding: utf-8 -*-
from typing import Dict, Tuple
import yourProtocol

class EncodingException(Exception):
    def __init__(self, reason:str):
        self.reason = reason
        
        
class Encoder(object):
    """
    This object implement a protocol of exchange between a client and a server
    based on an dictionnary. The dictionnary should be
    
    {    key1 : value1
         key2 : value2
         ...}
    
    whith key(s) a parameter and value(s) a string/byte/int object
    I let you free to develop your own gramma based on this constrain
    """
    
    def __init__(self, logger):
        self.logger = logger
        
    def encode(self, fields:Dict):
        result = bytearray()
        result.append(0x02) # The start byte
        
        keys = sorted(*fields)
        for key in keys:
            if not isinstance(key, int):
                raise EncodingException("Cannot encode non integer key [%s]" %key)
            
            string = str(fields[key])
            result.extend(self.encode_93(key))
            result.extend(self.encode_93(len(string)))
            result.extend(string.encode('utf-8'))
            
        result.append(0x03) # The stop byte
        return bytes(result)
    
    def decode(self, data:bytes) -> Dict:
        
        position = 0
        result = {}
        
        if data[position] == 0x02: # Optional buffer of one byte, you can delete this if for your protocol
            position += 1
            
        while data[position] != 0x03 and position + 3 < len(data):
            fieldIndex, position = self.decode_93(data, position)
            fieldSize, position = self.decode_93(data, position)
            
            if position + fieldSize > len(data):
                raise EncodingException( "Field size [%s] going over protocol length. Pos [%s] protocol [%s]" %(fieldSize, position, len(data)))
                
            if not fieldIndex in result:
                result[fieldIndex] = data[position:position+fieldSize].decode("utf-8")
                
            position += fieldSize
        return result
    
    def encode_93(self, value:int) -> bytes:
        
        result = bytearray()
        
        if value < yourProtocol.minKey or value > yourProtocol.maxKey:
            raise EncodingException('Value to encode in [%s] is not between [%s ; %s]' %(value, yourProtocol.minKey, yourProtocol.maxKey))
            
        quot, rem = divmod(value, 93)
        if quot > 0:
            result.append(0x7f)
            result.append(rem+32)
            result.append(quot+32)
        else:
            result.append(rem+32)
        return bytes(result)
    
    def decode_93(self, data:bytes, position:int) -> Tuple[int, int]:
        newPosition = position
        result = 0
        
        firstByte = data[newPosition]
        if firstByte < 0x0f:
            result = data[newPosition] - 32
        elif firstByte == 0x0f:
            newPosition += 1
            result = data[newPosition] - 32
            newPosition += 1
        elif firstByte == 0x88:
            newPosition += 1
            result = (data[newPosition] - 32) *-1
        elif firstByte == 0x89:
            newPosition += 1
            result = (data[newPosition] - 32) *-1
            newPosition += 1
            result -= (data[newPosition] -32) * 93
        else:
            raise EncodingException("Invalid protocol first byte value [%s]" %firstByte)
            
        newPosition +=1
        return result, newPosition
            
            
            
                
                