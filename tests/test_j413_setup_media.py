from pathlib import Path
import shutil,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class SetupMediaTests(unittest.TestCase):
 def test_actual_setup_predicate_requires_every_file_and_closes_handles(self):
  cc=shutil.which('cc')
  if not cc:self.skipTest('C compiler unavailable')
  source=(ROOT/'mu/Silicon/Apple/AppleSiliconPkg/Drivers/WindowsAutoBootDxe/WindowsAutoBootDxe.c').read_text();a=source.index('STATIC BOOLEAN HasCompleteSetupMedia(');b=source.index('\n#endif',a)
  c=r'''
#include <assert.h>
#include <stdarg.h>
#include <wchar.h>
#include <stddef.h>
#define STATIC static
#define IN
#define CONST const
#define TRUE 1
#define FALSE 0
#define EFI_ERROR(x) ((x)!=0)
#define EFI_FILE_MODE_READ 1
typedef int BOOLEAN;typedef int EFI_STATUS;typedef wchar_t CHAR16;typedef size_t UINTN;
struct File;typedef struct File EFI_FILE_PROTOCOL;
struct File {int (*Open)(EFI_FILE_PROTOCOL*,EFI_FILE_PROTOCOL**,CHAR16*,int,int);int (*Close)(EFI_FILE_PROTOCOL*);};
struct FS;typedef struct FS EFI_SIMPLE_FILE_SYSTEM_PROTOCOL;
struct FS {int (*OpenVolume)(EFI_SIMPLE_FILE_SYSTEM_PROTOCOL*,EFI_FILE_PROTOCOL**);};
static struct {void *ConOut;} table={0};
#define gST (&table)
static int Print(const CHAR16 *s,...){(void)s;return 0;}
static void J413LogStatus(const char *s,int v){(void)s;(void)v;}
typedef char CHAR8;
static int missing=-1,opens,closes,root_fail;static EFI_FILE_PROTOCOL root,file;
static int close_file(EFI_FILE_PROTOCOL *p){(void)p;closes++;return 0;}
static int open_file(EFI_FILE_PROTOCOL *r,EFI_FILE_PROTOCOL **out,CHAR16 *name,int mode,int attrs){
 (void)r;(void)attrs;assert(mode==1);
 const wchar_t *paths[]={L"\\EFI\\BOOT\\BOOTAA64.EFI",L"\\EFI\\Microsoft\\Boot\\BCD",L"\\sources\\boot.wim",L"\\boot\\boot.sdi"};
 assert(opens<4 && !wcscmp(name,paths[opens]));int n=opens++;
 if(n==missing)return 1;*out=&file;return 0;
}
static int open_root(EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *fs,EFI_FILE_PROTOCOL **out){(void)fs;if(root_fail)return 1;*out=&root;return 0;}
'''+source[a:b]+r'''
int main(void){root.Open=open_file;root.Close=close_file;file.Close=close_file;EFI_SIMPLE_FILE_SYSTEM_PROTOCOL fs={open_root};
 for(missing=-1;missing<4;missing++){opens=closes=0;BOOLEAN result=HasCompleteSetupMedia(&fs);
 assert(result==(missing==-1));assert(opens==(missing==-1?4:missing+1));assert(closes==(missing==-1?5:missing+1));}
 root_fail=1;opens=closes=0;assert(!HasCompleteSetupMedia(&fs));assert(opens==0 && closes==0);return 0;}
'''
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'test.c').write_text(c);subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p/'test.c'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
