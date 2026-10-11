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

    def test_guest_mark_uses_stride_and_preserves_guards(self):
        code=(ROOT/'m1n1_windows/src/fb.c').read_text();a=code.index('void fb_guest_boot_logo(');b=code.index('\n#endif',a)
        self.compile_run('''#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
typedef uint64_t u64; typedef uint32_t u32;
typedef struct {uint8_t r,g,b;} rgb_t;
static struct {struct {u32 width,height;} font;} console={{8,16}};
static rgb_t font_get_pixel(char c,u32 x,u32 y) {(void)c;(void)x;(void)y;return (rgb_t){255,255,255};}
#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))
'''+code[a:b]+'''
int main(void) {
 const u32 w=2560,h=1664,stride=10240+64;
 size_t count=(size_t)h*(stride/4);u32 *p=calloc(count+2,sizeof(u32));assert(p);
 p[0]=0xdeadbeef;p[count+1]=0xdeadbeef;
 fb_guest_boot_logo((u64)(uintptr_t)(p+1),w,h,stride);
 assert(p[0]==0xdeadbeef && p[count+1]==0xdeadbeef);
 for(u32 y=0;y<h;y++)for(u32 x=w;x<stride/4;x++)assert(p[1+y*(stride/4)+x]==0);
 u32 side=h/10,gap=side/16,left=(w-side*2-gap)/2,top=(h-side*2-gap)/2;
 assert(p[1+top*(stride/4)+left]==0x0078d4);
 assert(p[1+(top+side)*(stride/4)+left]==0);
 free(p);fb_guest_boot_logo(0,0,0,0);return 0;
}
''')

    def test_actual_mu_bmp_header_pixels_and_warning_fallback(self):
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
static UINT32 le32(UINT8 *p){return p[0]|((UINT32)p[1]<<8)|((UINT32)p[2]<<16)|((UINT32)p[3]<<24);}
int main(void){UINTN size;UINT8 *p=NULL;
 assert(GetBootGraphic(0,&size,&p)==0 && p);
 assert(size==110646 && p[0]=='B' && p[1]=='M' && le32(p+2)==size);
 assert(le32(p+10)==54 && le32(p+18)==192 && le32(p+22)==192 && p[28]==24);
 size_t filled=0;for(size_t i=54;i<size;i+=3)if(p[i]){assert(p[i]==0xd4 && p[i+1]==0x78 && p[i+2]==0);filled++;}
 assert(filled==152*152);free(p);
 assert(GetBootGraphic(1,&size,&p)==71 && GetBootGraphic(2,&size,&p)==72);
 assert(GetBootGraphic(3,&size,&p)==EFI_UNSUPPORTED);
 assert(GetBootGraphic(0,NULL,&p)==EFI_INVALID_PARAMETER);return 0;}
''')
if __name__=='__main__':unittest.main()
