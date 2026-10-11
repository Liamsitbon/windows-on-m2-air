from pathlib import Path
import shutil,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class FirmwareLogTests(unittest.TestCase):
 def test_actual_line_buffer_bounds_and_ownership_marker(self):
  cc=shutil.which('cc')
  if not cc:self.skipTest('C compiler unavailable')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'test.c').write_text(r'''
#include <assert.h>
#include <string.h>
#include "hv_j413_fw_log.h"
static int lines, takeover;static char last[256];
static void emit(const char *s,bool taken,void *ctx){(void)ctx;assert(strlen(s)<256);strcpy(last,s);lines++;if(taken)takeover++;}
int main(void){struct hv_j413_fw_log log={0};
 const char *s="Actual Mu init\r\n";for(;*s;s++)hv_j413_fw_log_feed(&log,*s,emit,0);
 assert(lines==1 && !strcmp(last,"Actual Mu init") && !log.taken);
 for(int i=0;i<255;i++)hv_j413_fw_log_feed(&log,'X',emit,0);
 assert(lines==2 && strlen(last)==255);
 hv_j413_fw_log_feed(&log,'\n',emit,0);
 s=HV_J413_GOP_TAKEOVER "\n";for(;*s;s++)hv_j413_fw_log_feed(&log,*s,emit,0);
 assert(log.taken && takeover==1);
 s="after\n";for(;*s;s++)hv_j413_fw_log_feed(&log,*s,emit,0);
 assert(takeover==2);return 0;}
''');subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(ROOT/'platforms/j413/m1n1'),str(p/'test.c'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)
