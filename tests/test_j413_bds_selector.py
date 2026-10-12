from pathlib import Path
import shutil, subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class BdsSelectorTests(unittest.TestCase):
 def test_actual_selector_skips_invalid_media_and_builds_ephemeral_option(self):
  cc=shutil.which('cc')
  if not cc:self.skipTest('C compiler unavailable')
  src=(ROOT/'mu/Silicon/Apple/AppleSiliconPkg/Drivers/WindowsAutoBootDxe/WindowsAutoBootDxe.c').read_text()
  a=src.index('STATIC EFI_STATUS EFIAPI GetJ413SetupOption(');b=src.index('STATIC J413_WINDOWS_SETUP mSetup',a)
  c=r'''
#include <assert.h>
#include <stdlib.h>
#include <stdint.h>
#include <wchar.h>
#define STATIC static
#define EFIAPI
#define OUT
#define TRUE 1
#define FALSE 0
#define EFI_SUCCESS 0
#define EFI_INVALID_PARAMETER 1
#define EFI_NOT_FOUND 2
#define EFI_OUT_OF_RESOURCES 3
#define EFI_ERROR(x) ((x)!=0)
#define ByProtocol 0
#define LoadOptionNumberUnassigned 0xffff
#define LoadOptionTypeBoot 0
#define LOAD_OPTION_ACTIVE 1
#define WINDOWS_FALLBACK_LOADER L"\\EFI\\BOOT\\BOOTAA64.EFI"
typedef int BOOLEAN;typedef int EFI_STATUS;typedef void VOID;typedef size_t UINTN;typedef void *EFI_HANDLE;
typedef struct {int MediaPresent;} MEDIA;
typedef struct {MEDIA *Media;} EFI_BLOCK_IO_PROTOCOL;
typedef struct {int complete;} EFI_SIMPLE_FILE_SYSTEM_PROTOCOL;
typedef struct {int id;} EFI_DEVICE_PATH_PROTOCOL;
typedef struct {int ready;} EFI_BOOT_MANAGER_LOAD_OPTION;
static int gEfiSimpleFileSystemProtocolGuid,gEfiBlockIoProtocolGuid,gJ413UsbDartReadyProtocolGuid;
typedef struct {unsigned ControllerMask;} J413_USB_DART_READY;
static void J413LogStatus(const char *s,int v){(void)s;(void)v;}
static void J413LogCount(const char *s,size_t v){(void)s;(void)v;}
static void J413Checkpoint(const char *s,int v){(void)s;(void)v;}
static EFI_STATUS locate_protocol(int *guid,void *key,void **out){(void)guid;(void)key;*out=NULL;return EFI_NOT_FOUND;}

static BOOLEAN mSetupSelected;
static struct {void *ConOut;} table={(void*)1};
static int connection_banner;
#define gST (&table)
static int Print(const wchar_t *s,...){if(!wcscmp(s,L"UEFI TRACE: Setup selector entered; connecting controllers\r\n"))connection_banner++;return 0;}
static int free_count,connects,locate_fail,init_fail,path_fail,init_count,probe_null;
static MEDIA media[3];static EFI_BLOCK_IO_PROTOCOL block[3];static EFI_SIMPLE_FILE_SYSTEM_PROTOCOL fs[3];
static void FreePool(void *p){assert(p);free_count++;free(p);}
static void J413ConnectAll(void){assert(connection_banner==connects+1);connects++;}
static int HasCompleteSetupMedia(EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *p){return p->complete;}
static EFI_STATUS locate(int type,int *guid,void *key,UINTN *count,EFI_HANDLE **out){
 (void)type;(void)guid;(void)key;if(locate_fail)return EFI_NOT_FOUND;
 *count=3;*out=malloc(3*sizeof(EFI_HANDLE));for(int i=0;i<3;i++)(*out)[i]=(void*)(uintptr_t)(i+1);return 0;}
static EFI_STATUS handle(EFI_HANDLE h,int *guid,void **out){int i=(int)(uintptr_t)h-1;assert(i>=0&&i<3);
 if(probe_null){*out=NULL;return 0;}*out=guid==&gEfiBlockIoProtocolGuid?(void*)&block[i]:(void*)&fs[i];return 0;}
static struct {EFI_STATUS (*LocateHandleBuffer)(int,int*,void*,UINTN*,EFI_HANDLE**);EFI_STATUS (*HandleProtocol)(EFI_HANDLE,int*,void**);EFI_STATUS (*LocateProtocol)(int*,void*,void**);} services={locate,handle,locate_protocol};
#define gBS (&services)
static EFI_DEVICE_PATH_PROTOCOL *FileDevicePath(EFI_HANDLE h,const wchar_t *name){assert(!wcscmp(name,WINDOWS_FALLBACK_LOADER));if(path_fail)return NULL;EFI_DEVICE_PATH_PROTOCOL *p=malloc(sizeof(*p));p->id=(int)(uintptr_t)h;return p;}
static EFI_STATUS EfiBootManagerInitializeLoadOption(EFI_BOOT_MANAGER_LOAD_OPTION *o,int number,int type,int attr,const wchar_t *name,EFI_DEVICE_PATH_PROTOCOL *p,void *opts,int length){
 assert(number==0xffff&&type==0&&attr==1&&p->id==3&&!opts&&!length);assert(!wcscmp(name,L"Windows ARM64 Setup"));init_count++;if(init_fail)return 3;o->ready=1;return 0;}
'''+src[a:b]+r'''
static void reset(void){mSetupSelected=0;connection_banner=0;free_count=connects=locate_fail=init_fail=path_fail=init_count=probe_null=0;
 for(int i=0;i<3;i++){media[i].MediaPresent=1;block[i].Media=&media[i];fs[i].complete=0;}media[0].MediaPresent=0;fs[2].complete=1;}
int main(void){EFI_BOOT_MANAGER_LOAD_OPTION o={0};reset();assert(GetJ413SetupOption(NULL)==1&&connects==0);
 assert(GetJ413SetupOption(&o)==0&&o.ready&&init_count==1&&free_count==2&&connects==1);
 assert(GetJ413SetupOption(&o)==2&&connects==1);reset();locate_fail=1;assert(GetJ413SetupOption(&o)==2&&free_count==0);
 reset();probe_null=1;assert(GetJ413SetupOption(&o)==2&&free_count==1&&!mSetupSelected);
 reset();block[2].Media=NULL;assert(GetJ413SetupOption(&o)==2&&free_count==1);
 reset();fs[2].complete=0;assert(GetJ413SetupOption(&o)==2&&init_count==0);
 reset();path_fail=1;assert(GetJ413SetupOption(&o)==3&&free_count==1&&!mSetupSelected);
 reset();init_fail=1;assert(GetJ413SetupOption(&o)==3&&free_count==2&&!mSetupSelected);init_fail=0;assert(GetJ413SetupOption(&o)==0);return 0;}
'''
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'t.c').write_text(c);subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p/'t.c'),'-o',str(p/'t')],check=True);subprocess.run([str(p/'t')],check=True)
