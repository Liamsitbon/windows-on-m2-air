import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / 'drivers/apple-dockchannel/core'
HARNESS = r'''
#include <assert.h>
#include <string.h>
#include "hid_discovery.h"
#include "hid_stream.h"
int main(void) {
    uint8_t init[128] = {0xf0,0,0,2};
    memcpy(init+4,"keyboard",8);
    init[22]=0; init[24]=3; init[26]=5; init[27]=1; init[28]=9;
    init[29]=7; init[31]=4; memcpy(init+33,"ABC",4);
    struct dchid_discovery d;
    assert(dchid_parse_discovery(init,37,&d)==DCHID_OK);
    assert(d.interface_id==2 && !strcmp(d.name,"keyboard"));
    assert(d.descriptor_size==3 && d.descriptor==init+26);
    assert(d.product_size==4 && d.product==init+33);
    for (size_t n=0;n<22;n++) assert(dchid_parse_discovery(init,n,&d)==DCHID_INCOMPLETE && !d.descriptor);
    for (size_t n=23;n<29;n++) assert(dchid_parse_discovery(init,n,&d)==DCHID_BAD_HEADER && !d.descriptor);
    init[36]=1; assert(dchid_parse_discovery(init,37,&d)==DCHID_BAD_HEADER && !d.descriptor); init[36]=0;
    init[31]=0; assert(dchid_parse_discovery(init,33,&d)==DCHID_BAD_HEADER); init[31]=4;
    init[3]=16; assert(dchid_parse_discovery(init,37,&d)==DCHID_BAD_HEADER); init[3]=2;
    memset(init+4,'x',16); assert(dchid_parse_discovery(init,37,&d)==DCHID_OK && d.name[16]==0);
    memset(init+22,0,106); init[22]=1; init[24]=35;
    assert(dchid_parse_discovery(init,61,&d)==DCHID_BAD_HEADER); /* GPIO must fit block, not enclosing event. */
    init[24]=36; init[28]=7; memset(init+30,'g',32);
    assert(dchid_parse_discovery(init,62,&d)==DCHID_OK && d.gpio_id==7 && d.gpio_name[32]==0);
    uint8_t wire[128], guarded[130], payload[]={1,2,3}; size_t written, used;
    struct dchid_packet view; struct dchid_stream s;
    assert(dchid_encode_command(2,7,0x81,payload,3,wire,128,&written)==DCHID_OK);
    memcpy(wire+written,wire,written);
    for (size_t split=0;split<=written;split++) {
        memset(guarded,0xa5,sizeof(guarded));
        assert(dchid_stream_reset(&s,guarded+1,128)==DCHID_OK);
        enum dchid_status r=dchid_stream_feed(&s,wire,split,&used,&view);
        assert(used==split && r==(split==written ? DCHID_OK : DCHID_INCOMPLETE));
        r=dchid_stream_feed(&s,wire+split,2*written-split,&used,&view);
        assert(r==DCHID_OK && used==written-split && view.payload_size==3);
        assert(!memcmp(view.payload,payload,3) && guarded[0]==0xa5 && guarded[129]==0xa5);
    }
    dchid_stream_reset(&s,guarded+1,20);
    assert(dchid_stream_feed(&s,wire,written,&used,&view)==DCHID_NO_SPACE && used==8);
    assert(dchid_stream_feed(&s,wire,written,&used,&view)==DCHID_NO_SPACE && !used);
    dchid_stream_reset(&s,guarded+1,128); wire[written-1]^=1;
    assert(dchid_stream_feed(&s,wire,written,&used,&view)==DCHID_BAD_CHECKSUM && !view.payload);
    assert(dchid_stream_feed(&s,wire,written,&used,&view)==DCHID_BAD_CHECKSUM && !used);
    uint32_t seed=1;
    for (unsigned t=0;t<10000;t++) {
        size_t n=t%sizeof(init);
        for(size_t i=0;i<n;i++) { seed=seed*1664525u+1013904223u; init[i]=(uint8_t)(seed>>24); }
        if(dchid_parse_discovery(init,n,&d)==DCHID_OK) {
            if(d.descriptor) assert(d.descriptor>=init && d.descriptor_size<=(size_t)(init+n-d.descriptor));
        } else assert(!d.descriptor && !d.product);
    }
}
'''

class DockChannelDiscoveryTests(unittest.TestCase):
    def test_partial_reads_and_discovery_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path/'test.c').write_text(HARNESS)
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(CORE),str(path/'test.c'),*[str(CORE/name) for name in ('hid_packet.c','hid_stream.c','hid_discovery.c')],'-o',str(path/'test')],check=True)
            subprocess.run([str(path/'test')],check=True,timeout=15)

    def test_windows_arm64_objects(self):
        compiler=shutil.which('clang')
        if not compiler: self.skipTest('Clang unavailable')
        with tempfile.TemporaryDirectory() as directory:
            for name in ('hid_stream','hid_discovery'):
                output=Path(directory)/(name+'.obj')
                subprocess.run([compiler,'--target=aarch64-pc-windows-msvc','-ffreestanding','-std=c11','-Wall','-Wextra','-Werror','-c',str(CORE/(name+'.c')),'-o',str(output)],check=True)
                self.assertEqual(0xaa64,struct.unpack_from('<H',output.read_bytes())[0])
