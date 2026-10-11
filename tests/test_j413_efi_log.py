from pathlib import Path
import shutil,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class EfiLogTests(unittest.TestCase):
 def test_actual_bounded_writer_targets_nvme_anchor_and_checks_write_flush(self):
  cc=shutil.which('cc')
  if not cc:self.skipTest('C compiler unavailable')
  c=r'''
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <wchar.h>
#define STATIC static
#define CONST const
#define VOID void
#define TRUE 1
#define FALSE 0
#define EFI_SUCCESS 0
#define EFI_NOT_FOUND 1
#define EFI_DEVICE_ERROR 2
#define EFI_ERROR(s) ((s)!=0)
#define ByProtocol 0
#define EFI_FILE_MODE_READ 1
#define EFI_FILE_MODE_WRITE 2
#define EFI_FILE_MODE_CREATE 4
#define MESSAGING_DEVICE_PATH 3
#define MSG_NVME_NAMESPACE_DP 23
typedef int EFI_STATUS;typedef int BOOLEAN;typedef size_t UINTN;typedef uint64_t UINT64;typedef char CHAR8;typedef void *EFI_HANDLE;
typedef struct {int MediaPresent,ReadOnly;} MEDIA;typedef struct {MEDIA *Media;} EFI_BLOCK_IO_PROTOCOL;
typedef struct {int type,sub,end;} EFI_DEVICE_PATH_PROTOCOL;
static EFI_DEVICE_PATH_PROTOCOL paths[3]={{3,1,0},{3,23,0},{3,23,0}},end={0,0,1};
static EFI_DEVICE_PATH_PROTOCOL *DevicePathFromHandle(EFI_HANDLE h){return &paths[(uintptr_t)h-1];}
#define IsDevicePathEnd(p) ((p)->end)
#define DevicePathType(p) ((p)->type)
#define DevicePathSubType(p) ((p)->sub)
#define NextDevicePathNode(p) (&end)
static UINTN AsciiSPrint(char *out,size_t size,const char *fmt,...){va_list ap;va_start(ap,fmt);const char *label=va_arg(ap,const char*);int n;
 if(strstr(fmt,"%Lu"))n=snprintf(out,size,"%s = %llu",label,(unsigned long long)va_arg(ap,UINT64));else n=snprintf(out,size,"%s: %d\r\n",label,va_arg(ap,int));va_end(ap);return n<0?0:((size_t)n<size?(size_t)n:size-1);}
struct File;typedef struct File EFI_FILE_PROTOCOL;
struct File {EFI_STATUS(*Open)(EFI_FILE_PROTOCOL*,EFI_FILE_PROTOCOL**,const wchar_t*,int,int);EFI_STATUS(*Close)(EFI_FILE_PROTOCOL*);EFI_STATUS(*SetPosition)(EFI_FILE_PROTOCOL*,UINT64);EFI_STATUS(*Write)(EFI_FILE_PROTOCOL*,UINTN*,void*);EFI_STATUS(*Flush)(EFI_FILE_PROTOCOL*);};
struct Fs;typedef struct Fs EFI_SIMPLE_FILE_SYSTEM_PROTOCOL;struct Fs {EFI_STATUS(*OpenVolume)(EFI_SIMPLE_FILE_SYSTEM_PROTOCOL*,EFI_FILE_PROTOCOL**);};
static EFI_FILE_PROTOCOL root,anchor,logfile;
static int opens,closes,writes,flushes,short_write,write_error,flush_error,anchor_error,position_error,create_error,locate_error,saved_print;
static MEDIA media[3]={{1,0},{1,1},{1,0}};static EFI_BLOCK_IO_PROTOCOL block[3];static EFI_SIMPLE_FILE_SYSTEM_PROTOCOL fs;
static int gEfiSimpleFileSystemProtocolGuid,gEfiBlockIoProtocolGuid;
static EFI_STATUS close_file(EFI_FILE_PROTOCOL*p){(void)p;closes++;return 0;}
static EFI_STATUS open_file(EFI_FILE_PROTOCOL*r,EFI_FILE_PROTOCOL**out,const wchar_t*name,int mode,int attr){assert(r==&root&&!attr);opens++;
 if(!wcscmp(name,L"\\m1n1\\boot.bin")){assert(mode==1);if(anchor_error)return 1;*out=&anchor;}else{assert(!wcscmp(name,L"\\m1n1\\j413uefi.log")&&mode==7);if(create_error)return 2;*out=&logfile;}return 0;}
static EFI_STATUS position(EFI_FILE_PROTOCOL*p,UINT64 off){assert(p==&logfile&&off==0);return position_error;}
static EFI_STATUS write_file(EFI_FILE_PROTOCOL*p,UINTN*n,void*data){assert(p==&logfile&&*n==16384&&data);assert(((char*)data)[16383]==0);writes++;if(short_write)(*n)--;return write_error;}
static EFI_STATUS flush(EFI_FILE_PROTOCOL*p){assert(p==&logfile);flushes++;return flush_error;}
static EFI_STATUS open_volume(EFI_SIMPLE_FILE_SYSTEM_PROTOCOL*f,EFI_FILE_PROTOCOL**out){assert(f==&fs);*out=&root;return 0;}
static EFI_STATUS locate(int t,int*g,void*k,UINTN*n,EFI_HANDLE**out){(void)t;(void)g;(void)k;if(locate_error)return 1;*n=3;*out=malloc(3*sizeof(EFI_HANDLE));for(int i=0;i<3;i++)(*out)[i]=(void*)(uintptr_t)(i+1);return 0;}
static EFI_STATUS protocol(EFI_HANDLE h,int*g,void**out){int i=(uintptr_t)h-1;*out=g==&gEfiBlockIoProtocolGuid?(void*)&block[i]:(void*)&fs;return 0;}
static struct {EFI_STATUS(*LocateHandleBuffer)(int,int*,void*,UINTN*,EFI_HANDLE**);EFI_STATUS(*HandleProtocol)(EFI_HANDLE,int*,void**);} services={locate,protocol};
#define gBS (&services)
static struct {void*ConOut;} table={(void*)1};
#define gST (&table)
static void FreePool(void*p){free(p);}
static int Print(const wchar_t*s,...){if(wcsstr(s,L"phase log saved"))saved_print++;return 0;}
#include "J413EfiLog.h"
static void reset(void){opens=closes=writes=flushes=short_write=write_error=flush_error=anchor_error=position_error=create_error=locate_error=saved_print=0;}
int main(void){for(int i=0;i<3;i++)block[i].Media=&media[i];root.Open=open_file;root.Close=anchor.Close=logfile.Close=close_file;logfile.SetPosition=position;logfile.Write=write_file;logfile.Flush=flush;fs.OpenVolume=open_volume;
 J413LogCount("handles",3);for(int i=0;i<3000;i++)J413LogStatus("test",2);assert(mJ413LogUsed<=16383&&mJ413Log[16383]==0);
 reset();assert(J413SaveLog()==0&&writes==1&&flushes==1&&closes==3&&opens==2);
 reset();short_write=1;assert(J413SaveLog()==2&&flushes==0&&closes==3);
 reset();write_error=2;assert(J413SaveLog()==2&&flushes==0&&closes==3);
 reset();flush_error=2;assert(J413SaveLog()==2&&closes==3);
 reset();anchor_error=1;assert(J413SaveLog()==1&&writes==0&&closes==1);
 reset();create_error=2;assert(J413SaveLog()==2&&writes==0&&closes==2);
 reset();position_error=2;assert(J413SaveLog()==2&&writes==0&&closes==3);
 reset();locate_error=1;assert(J413SaveLog()==1&&opens==0);
 reset();J413Checkpoint("checkpoint",0);assert(saved_print==1&&writes==1);return 0;}
'''
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'Library').mkdir()
   for name in ['PrintLib.h','BaseMemoryLib.h']:(p/'Library'/name).write_text('')
   shutil.copyfile(ROOT/'platforms/j413/mu/Silicon/Apple/AppleSiliconPkg/Drivers/WindowsAutoBootDxe/J413EfiLog.h',p/'J413EfiLog.h')
   (p/'t.c').write_text(c);subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(p),str(p/'t.c'),'-o',str(p/'t')],check=True);subprocess.run([str(p/'t')],check=True)
