#!/usr/bin/env python3
"""Extract only the bounded J413 log from FAT32; never write to the source."""
import argparse
from pathlib import Path
import struct

class FatLogReader:
    def __init__(self, source):
        self.source = source
        b = self.read(0, 512)
        u16=lambda n: struct.unpack_from('<H',b,n)[0]
        u32=lambda n: struct.unpack_from('<I',b,n)[0]
        self.bps=u16(11);spc=b[13];reserved=u16(14);nf=b[16];fat_size=u32(36);total=u32(32);self.root=u32(44)
        if b[510:512]!=b'\x55\xaa' or u16(17) or u16(22): raise ValueError('expected FAT32 partition, not whole disk')
        if self.bps not in (512,1024,2048,4096) or not spc or spc & (spc-1) or not reserved or nf not in (1,2) or not fat_size: raise ValueError('invalid FAT32 geometry')
        if total*self.bps > 1024**3: raise ValueError('unexpected ESP size (maximum 1 GiB)')
        self.clusters=(total-reserved-nf*fat_size)//spc
        if self.clusters<65525 or (self.clusters+2)*4>fat_size*self.bps: raise ValueError('invalid FAT32 cluster capacity')
        flags=u16(40);active=(flags&15) if flags&128 else 0
        if active>=nf or not 2<=self.root<self.clusters+2: raise ValueError('invalid active FAT/root')
        self.fat=(reserved+active*fat_size)*self.bps
        self.data=(reserved+nf*fat_size)*self.bps;self.cs=spc*self.bps

    def read(self, offset, length):
        self.source.seek(offset);data=self.source.read(length)
        if len(data)!=length: raise ValueError('short read from FAT source')
        return data

    def chain(self, cluster, maximum):
        seen=set()
        while cluster<0x0ffffff8:
            if not 2<=cluster<self.clusters+2 or cluster in seen or len(seen)>=maximum: raise ValueError('invalid/cyclic/overlong FAT chain')
            seen.add(cluster);yield cluster
            cluster=struct.unpack('<I',self.read(self.fat+cluster*4,4))[0]&0x0fffffff

    def entry(self, directory, name):
        for cluster in self.chain(directory,128):
            data=self.read(self.data+(cluster-2)*self.cs,self.cs)
            for offset in range(0,len(data),32):
                e=data[offset:offset+32]
                if e[0]==0: raise FileNotFoundError(name.decode())
                if e[0]==0xe5 or e[11]&8 or e[11]==15:continue
                if e[:11]==name:
                    c=((struct.unpack_from('<H',e,20)[0]<<16)|struct.unpack_from('<H',e,26)[0])&0x0fffffff
                    return c,struct.unpack_from('<I',e,28)[0],e[11]
        raise FileNotFoundError(name.decode())

    def log(self):
        directory,_,attr=self.entry(self.root,b'M1N1       ')
        if not attr&16: raise ValueError('m1n1 is not a directory')
        cluster,size,attr=self.entry(directory,b'J413UEFILOG')
        if attr&16 or not 0<size<=16384: raise ValueError('unexpected log file type/size')
        chunks=[]
        for c in self.chain(cluster,(16384+self.cs-1)//self.cs):
            chunks.append(self.read(self.data+(c-2)*self.cs,self.cs))
        data=b''.join(chunks)
        if len(data)<size: raise ValueError('log chain shorter than file size')
        return data[:size].split(b'\0',1)[0]

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--output',type=Path);args=p.parse_args()
    try:
        with args.source.open('rb') as source:data=FatLogReader(source).log()
    except (OSError, ValueError) as error:
        p.exit(2, f'EFI log unavailable: {error}\n')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(data)
    print(data.decode('ascii',errors='replace'),end='')
