"""Execute owning boot renderers with independently checked pixel boundaries."""
from pathlib import Path
import shutil, subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]

class J413BootUITests(unittest.TestCase):
    def compile_run(self,source):
        cc=shutil.which('cc')
        if not cc:self.skipTest('C compiler unavailable')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'test.c').write_text(source)
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p/'test.c'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True,timeout=10)

    def test_initial_branding_clears_inherited_logo_and_flushes(self):
        code=(ROOT/'m1n1_windows/src/fb.c').read_text();a=code.index('void fb_display_logo(void)');b=code.index('\nvoid fb_restore_logo',a)
        self.compile_run('''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#define M1N1_J413 1
typedef uint32_t u32; typedef u32 rgb_t;
static struct {int initialized;struct {u32 width,height;} font;} console={1,{16,32}};
static struct {u32 width,height;} fb={2560,1664};
static int cleared,drawn,flushed;
static rgb_t int2rgb(u32 value){return value;}
static void fb_clear(rgb_t color){assert(color==0);cleared++;}
static void fb_update(void){assert(cleared && drawn);flushed++;}
static void j413_boot_text(u32 x,u32 y,const char *text,u32 scale){
 assert(cleared && !strcmp(text,"UEFI BOOT") && scale==3);
 assert(x+9*16*scale<=fb.width && y+32*scale<=fb.height);drawn++;
}
'''+code[a:b]+'''int main(void){fb_display_logo();assert(cleared==1 && drawn==1 && flushed==1);
console.initialized=0;fb_display_logo();assert(flushed==1);return 0;}''')

    def test_guest_text_and_firmware_log_stop_at_gop_takeover(self):
        code=(ROOT/'m1n1_windows/src/fb.c').read_text();a=code.index('static struct {u32 *pixels; u32 width, height, stride, row; bool active;} fw_console;');b=code.index('\n#endif',a)
        self.compile_run('''#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#include <stdbool.h>
#include <string.h>
typedef uint64_t u64; typedef uint32_t u32;
typedef struct {uint8_t r,g,b;} rgb_t;
static struct {struct {u32 width,height;} font;} console={{8,16}};
static rgb_t font_get_pixel(char c,u32 x,u32 y) {(void)c;(void)x;(void)y;return (rgb_t){255,255,255};}
static void memset32(u32 *p,u32 value,size_t bytes){for(size_t i=0;i<bytes/4;i++)p[i]=value;}
static int cleans,disabled;
static void dc_cvac_range(void *p,u64 size){(void)p;assert(size>0);cleans++;}
static void fb_set_active(bool active){assert(!active);disabled++;}
#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))
'''+code[a:b]+'''
int main(void) {
 const u32 w=2560,h=1664,stride=10240+64;
 size_t count=(size_t)h*(stride/4);u32 *p=calloc(count+2,sizeof(u32));assert(p);
 p[0]=0xdeadbeef;p[count+1]=0xdeadbeef;
 fb_guest_boot_text((u64)(uintptr_t)(p+1),w,h,stride);
 assert(p[0]==0xdeadbeef && p[count+1]==0xdeadbeef);
 for(u32 y=0;y<h;y++)for(u32 x=w;x<stride/4;x++)assert(p[1+y*(stride/4)+x]==0);
 assert(p[1+(h/2)*(stride/4)+w/2]==0); // no mark
 assert(p[1+(h-64)*(stride/4)+w/2]==0); // no progress bar
 fb_firmware_log_line("REAL FIRMWARE LOG",false);assert(cleans==1);
 u32 *saved=malloc(count*4);assert(saved);memcpy(saved,p+1,count*4);
 fb_firmware_log_line("J413_GOP_CONSOLE_TAKEOVER",true);
 fb_firmware_log_line("LATE OUTPUT",false);
 assert(disabled==1 && cleans==1 && memcmp(saved,p+1,count*4)==0);free(saved);
 free(p);fb_guest_boot_text(0,0,0,0);return 0;
}
''')

    def test_no_normal_mu_graphic_and_warning_fallback(self):
        p=ROOT/'platforms/j413/mu/Platform/MacBookAirM2Pkg/Library/J413BootGraphicsProviderLib/J413BootGraphicsProviderLib.c'
        code='\n'.join(line for line in p.read_text().splitlines() if not line.startswith('#include'))
        self.compile_run('''#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#define STATIC static
#define CONST const
#define EFIAPI
#define VOID void
typedef uint8_t UINT8;typedef uint16_t UINT16;typedef uint32_t UINT32;typedef uintptr_t UINTN;
typedef int EFI_STATUS;typedef int EFI_GUID;typedef int BOOT_GRAPHIC;
#define BG_SYSTEM_LOGO 0
#define BG_CRITICAL_OVER_TEMP 1
#define BG_CRITICAL_LOW_BATTERY 2
#define EFI_SUCCESS 0
#define EFI_UNSUPPORTED 3
#define EFI_OUT_OF_RESOURCES 4
#define EFI_INVALID_PARAMETER 5
#define EFI_SECTION_RAW 0
#define PcdThermalFile 0
#define PcdLowBatteryFile 1
static EFI_GUID guids[2];
#define PcdGetPtr(p) (&guids[p])
#define AllocateZeroPool(n) calloc(1,n)
static EFI_STATUS GetSectionFromAnyFv(EFI_GUID *g,int type,int instance,VOID **out,UINTN *size) {
 (void)type;(void)instance;(void)out;(void)size;return g==&guids[0]?71:72;
}
'''+code+'''
int main(void){UINTN size=123;UINT8 *p=(UINT8*)1;
 assert(GetBootGraphic(0,&size,&p)==EFI_UNSUPPORTED && p==NULL && size==0);
 assert(GetBootGraphic(1,&size,&p)==71 && GetBootGraphic(2,&size,&p)==72);
 assert(GetBootGraphic(3,&size,&p)==EFI_UNSUPPORTED);
 assert(GetBootGraphic(0,NULL,&p)==EFI_INVALID_PARAMETER);return 0;}
''')
if __name__=='__main__':unittest.main()
