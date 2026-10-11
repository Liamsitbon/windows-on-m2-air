from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'drivers/apple-dockchannel/core'
HARNESS=r'''
#include <assert.h>
#include <string.h>
#include "hid_command.h"
#include "hid_firmware.h"
static void put32(uint8_t *p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(i*8));}
int main(void){
 struct dchid_command c={0}; uint8_t wire[128],request[]={0x10,3},response[8];size_t n,rsize;uint32_t rc;
 memset(wire,0xa5,sizeof(wire));
 assert(dchid_command_begin(&c,2,0x81,request,2,wire,20,&n)==DCHID_NO_SPACE && !c.active && !n && wire[0]==0xa5);
 assert(dchid_command_begin(&c,2,0xc1,request,2,wire,128,&n)==DCHID_OK && c.active && c.sequence==0);
 assert(dchid_command_begin(&c,2,0xc1,request,2,wire,128,&n)==DCHID_INVALID && !n && c.active);
 uint8_t data[]={0x10,4,5}; struct dchid_packet p={.channel=0x11,.interface_id=2,.sequence=0,.flags=0xc1,.payload=data,.payload_size=3};
 for(unsigned field=0;field<5;field++){
  struct dchid_packet bad=p;switch(field){case 0:bad.channel=0x12;break;case 1:bad.interface_id=3;break;case 2:bad.sequence=1;break;case 3:bad.flags=0xc0;break;case 4:data[0]=0x11;break;}
  memset(response,0xa5,sizeof(response));
  assert(dchid_command_complete(&c,&bad,response,8,&rsize,&rc)==DCHID_REPLY_UNEXPECTED && c.active && !rsize && !rc && response[0]==0xa5);data[0]=0x10;
 }
 assert(dchid_command_complete(&c,&p,response,1,&rsize,&rc)==DCHID_REPLY_NO_SPACE && c.active && rsize==2 && response[0]==0xa5);
 assert(dchid_command_complete(&c,&p,response,8,&rsize,&rc)==DCHID_REPLY_OK && !c.active && c.next_sequence==1 && rsize==2 && response[0]==4 && response[1]==5 && response[2]==0xa5);
 assert(dchid_command_complete(&c,&p,response,8,&rsize,&rc)==DCHID_REPLY_UNEXPECTED);
 c.next_sequence=255;assert(dchid_command_begin(&c,2,0x80,request,2,wire,128,&n)==DCHID_OK);
 p.sequence=255;p.flags=0x80;p.return_code=7;memset(response,0xa5,sizeof(response));
 assert(dchid_command_complete(&c,&p,response,8,&rsize,&rc)==DCHID_REPLY_REMOTE_ERROR && rc==7 && !c.active && c.next_sequence==0 && response[0]==0xa5);
 assert(dchid_command_begin(&c,2,0x80,request,2,wire,128,&n)==DCHID_OK);
 dchid_command_cancel(&c);dchid_command_cancel(&c);assert(!c.active && c.next_sequence==1);
 for(unsigned flags=0;flags<256;flags++){
  memset(&c,0,sizeof(c));enum dchid_status s=dchid_command_begin(&c,2,(uint8_t)flags,request,2,wire,128,&n);
  assert((s==DCHID_OK)==((flags>>6)>0 && (flags&0x3f)<=1 && ((flags>>6)!=1 || (flags&0x3f)==1)));
 }
 uint8_t fw[32]={0x48,0x49,0x44,0x46,1};put32(fw+8,20);put32(fw+12,4);put32(fw+16,2);fw[20]=1;fw[21]=2;fw[22]=3;fw[23]=4;
 memset(response,0xa5,8);assert(dchid_prepare_firmware(fw,24,7,response,8,&n)==DCHID_OK && n==4 && response[0]==1 && response[2]==7 && response[4]==0xa5 && fw[22]==3);
 put32(fw+16,0);assert(dchid_prepare_firmware(fw,24,7,response,8,&n)==DCHID_OK && response[0]==1);
 for(size_t size=0;size<24;size++) {memset(response,0xa5,8);assert(dchid_prepare_firmware(fw,size,7,response,8,&n)!=DCHID_OK && !n && response[0]==0xa5);}
 assert(dchid_prepare_firmware(fw,24,7,response,3,&n)==DCHID_NO_SPACE && !n);
 put32(fw+16,4);assert(dchid_prepare_firmware(fw,24,7,response,8,&n)==DCHID_BAD_HEADER);
 put32(fw+16,0);put32(fw+8,UINT32_MAX);assert(dchid_prepare_firmware(fw,24,7,response,8,&n)==DCHID_BAD_HEADER);
 put32(fw+8,20);put32(fw+12,UINT32_MAX);assert(dchid_prepare_firmware(fw,24,7,response,8,&n)==DCHID_BAD_HEADER);
 uint32_t seed=7;
 for(unsigned t=0;t<10000;t++) {size_t size=t%32;for(size_t i=0;i<size;i++){seed=seed*1664525u+1013904223u;fw[i]=(uint8_t)(seed>>24);}memset(response,0xa5,8);enum dchid_status s=dchid_prepare_firmware(fw,size,7,response,8,&n);if(s!=DCHID_OK)assert(!n && response[0]==0xa5);else assert(n<=8);}
}
'''

class DockChannelCommandTests(unittest.TestCase):
    def test_matching_cancel_remote_errors_and_firmware_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);(path/'test.c').write_text(HARNESS)
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(CORE),str(path/'test.c'),*[str(CORE/(name+'.c')) for name in ('hid_packet','hid_command','hid_firmware')],'-o',str(path/'test')],check=True)
            subprocess.run([str(path/'test')],check=True,timeout=10)

    def test_windows_arm64_objects(self):
        cc=shutil.which('clang')
        if not cc:self.skipTest('Clang unavailable')
        with tempfile.TemporaryDirectory() as directory:
            for name in ('hid_command','hid_firmware'):
                out=Path(directory)/(name+'.obj')
                subprocess.run([cc,'--target=aarch64-pc-windows-msvc','-ffreestanding','-std=c11','-Wall','-Wextra','-Werror','-c',str(CORE/(name+'.c')),'-o',str(out)],check=True)
                self.assertEqual(0xaa64,struct.unpack_from('<H',out.read_bytes())[0])
