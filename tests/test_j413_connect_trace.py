from pathlib import Path
import shutil, subprocess, tempfile, unittest
ROOT = Path(__file__).resolve().parents[1]
class ConnectTraceTests(unittest.TestCase):
    def test_actual_algorithm_brackets_calls_and_handles_enumeration_failure(self):
        cc = shutil.which('cc')
        if not cc: self.skipTest('C compiler unavailable')
        header = (ROOT/'platforms/j413/mu/Silicon/Apple/AppleSiliconPkg/Drivers/WindowsAutoBootDxe/J413ConnectTrace.h').read_text().replace('#include <Library/DxeServicesTableLib.h>', '')
        source = r'''
#include <assert.h>
#include <stdlib.h>
#include <stdint.h>
#include <wchar.h>
#define STATIC static
#define VOID void
#define TRUE 1
#define FALSE 0
#define EFI_ERROR(x) ((x)!=0)
#define AllHandles 0
typedef int EFI_STATUS; typedef size_t UINTN; typedef void *EFI_HANDLE; typedef wchar_t CHAR16;
typedef struct {int value;} EFI_DEVICE_PATH_PROTOCOL;
static int calls,console_entries,console_returns,controller_entries,controller_returns,dispatch_entries,dispatch_returns,free_count,enumeration_failure;
static void Print(const wchar_t *format, ...) {
 if(wcsstr(format,L"consoles entered")) console_entries++;
 if(wcsstr(format,L"consoles returned")) console_returns++;
 if(wcsstr(format,L"handle %p entered")) controller_entries++;
 if(wcsstr(format,L"controller %u returned")) controller_returns++;
 if(wcsstr(format,L"dispatch entered")) dispatch_entries++;
 if(wcsstr(format,L"dispatch returned")) dispatch_returns++;
}
static void EfiBootManagerConnectAllDefaultConsoles(void){assert(console_entries==console_returns+1);calls++;}
static EFI_STATUS locate(int type,void *guid,void *key,UINTN *count,EFI_HANDLE **out){
 assert(type==AllHandles&&!guid&&!key);if(enumeration_failure)return 7;
 *count=2;*out=malloc(2*sizeof(EFI_HANDLE));(*out)[0]=(void*)1;(*out)[1]=(void*)2;return 0;}
static EFI_STATUS connect(EFI_HANDLE handle,void *driver,void *path,int recursive){
 assert(!driver&&!path&&recursive);assert(controller_entries==controller_returns+1);calls++;return handle==(void*)1?0:7;}
static EFI_STATUS dispatch(void){assert(dispatch_entries==dispatch_returns+1);calls++;return dispatch_entries==1?0:7;}
static EFI_DEVICE_PATH_PROTOCOL path;
static EFI_DEVICE_PATH_PROTOCOL *DevicePathFromHandle(EFI_HANDLE h){return h==(void*)1?&path:NULL;}
static CHAR16 *ConvertDevicePathToText(EFI_DEVICE_PATH_PROTOCOL *p,int display,int shortcuts){assert(p==&path&&!display&&!shortcuts);return calloc(2,sizeof(CHAR16));}
static void FreePool(void *p){assert(p);free_count++;free(p);}
static struct {EFI_STATUS (*LocateHandleBuffer)(int,void*,void*,UINTN*,EFI_HANDLE**); EFI_STATUS (*ConnectController)(EFI_HANDLE,void*,void*,int);} bs={locate,connect};
static struct {EFI_STATUS (*Dispatch)(void);} ds={dispatch};
#define gBS (&bs)
#define gDS (&ds)
''' + header + r'''
int main(void){
 J413ConnectAll();assert(calls==8&&console_entries==2&&console_returns==2&&controller_entries==4&&controller_returns==4&&dispatch_entries==2&&dispatch_returns==2&&free_count==4);
 calls=console_entries=console_returns=controller_entries=controller_returns=dispatch_entries=dispatch_returns=free_count=0;enumeration_failure=1;
 J413ConnectAll();assert(calls==1&&console_entries==1&&console_returns==1&&!controller_entries&&!dispatch_entries&&!free_count);return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'test.c').write_text(source)
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p/'test.c'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True)
