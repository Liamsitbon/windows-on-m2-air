"""Exercise the actual startup/proxy entry bodies with host hardware boundaries."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'm1n1_windows/src'
OVERLAY = ROOT / 'platforms/j413/m1n1'

STARTUP = r'''
#include <assert.h>
#include <stdbool.h>
#include <setjmp.h>
#include <stdio.h>
#include "hv_bootstrap.h"
#include "hv_autonomous_boot_runtime.h"
#include "hv_stage_role.h"
static jmp_buf halted;
static int attempt, proxy_calls, usb_calls, payload_calls, kicks;
static bool display;
#define sysop(op) longjmp(halted, 1)
void fb_set_active(bool value) { display=value; }
void iodev_console_kick(void) { kicks++; }
void usb_init(void) { usb_calls++; }
void usb_iodev_init(void) { usb_calls++; }
int uartproxy_run(void *start) { (void)start; proxy_calls++; return 0; }
int payload_run(void) { payload_calls++; return 1; }
enum hv_bootstrap_attempt hv_bootstrap_chainload_if_present(bool *usb) {
    (void)usb; return (enum hv_bootstrap_attempt)attempt;
}
enum hv_autonomous_boot_attempt hv_autonomous_boot_if_present(bool *usb) {
    (void)usb; return (enum hv_autonomous_boot_attempt)attempt;
}
'''
STARTUP_END = r'''
int main(void) {
    for (attempt=0;attempt<3;attempt++) {
        proxy_calls=usb_calls=payload_calls=kicks=0;display=false;
        int did_halt=setjmp(halted);
        if (!did_halt) run_actions();
#ifdef M1N1_NO_PROXY
        assert(did_halt == (attempt != 1));
        assert(!proxy_calls && !usb_calls && !payload_calls);
        assert(kicks == (attempt != 1));
        if (did_halt) assert(display);
#else
        assert(!did_halt);
        assert(proxy_calls == (attempt != 1));
        assert(usb_calls == 2*(attempt != 1));
#endif
    }
    return 0;
}
'''

ENTRY = r'''
#include <assert.h>
#include <stdbool.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
struct uartproxy_msg_start { uint32_t reason, code; void *info, *reserved; };
static jmp_buf halted;
static int kicks;
static bool display;
#define sysop(op) longjmp(halted, 1)
void fb_set_active(bool value) { display=value; }
void iodev_console_kick(void) { kicks++; }
'''
ENTRY_END = r'''
int main(void) {
    struct uartproxy_msg_start start={3,7,NULL,NULL};
    for (int i=0;i<2;i++) {
        display=false;kicks=0;
        int did_halt=setjmp(halted);
        if (!did_halt) {
            uartproxy_run(i ? &start : NULL);
            assert(!"proxy must stop instead of returning or reading commands");
        }
        assert(did_halt && display && kicks==1);
    }
    return 0;
}
'''

PROFILE = r'''
#include <assert.h>
#include "hv_no_proxy_profile.h"
int main(void) {
    for (uint32_t flags=0;flags<32;flags++) {
        bool accepted=hv_no_proxy_flags_allowed(flags);
        assert(accepted == (flags == HV_AUTONOMOUS_DISPLAY_PHYSICAL));
        if (accepted) {
            struct hv_autonomous_profile profile;
            struct hv_autonomous_usb_plan plan;
            assert(hv_autonomous_profile_decode(flags,&profile));
            hv_autonomous_profile_usb_plan(&profile,&plan);
            assert(plan.power_platform && !plan.start_debug_transport);
            assert(!hv_autonomous_profile_accept_proxy(&profile,true));
            assert(!hv_autonomous_profile_usb_window_seconds(&profile));
        }
    }
    assert(!hv_no_proxy_flags_allowed(0x80000001));
    assert(!hv_no_proxy_profile_allowed(NULL));
    return 0;
}
'''


class J413NoProxyTests(unittest.TestCase):
    def compile_run(self, source, defines=(), objects=()):
        cc=shutil.which('cc')
        if not cc:
            self.skipTest('C compiler unavailable')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'test.c').write_text(source)
            subprocess.run([cc,'-std=c11','-Wall','-Wextra','-Werror',
                '-I',str(SRC),'-I',str(OVERLAY),*defines,str(p/'test.c'),
                *map(str,objects),'-o',str(p/'test')],check=True,capture_output=True)
            return subprocess.check_output([str(p/'test')],text=True,timeout=5)

    def test_both_actual_startup_stages_halt_on_failure_without_proxy(self):
        source=(SRC/'main.c').read_text()
        body=source[source.index('void run_actions(void)'):source.index('void m1n1_main(void)')]
        for role in (0,1):
            with self.subTest(role=role):
                output=self.compile_run(STARTUP+body+STARTUP_END,
                    ['-DM1N1_NO_PROXY','-DEARLY_PROXY_TIMEOUT=5',f'-DM1N1_STAGE{role}'],
                    [SRC/'hv_stage_role.c'])
                self.assertEqual(output.count('J413 STOP:'),2)
                self.assertNotIn('Running proxy...',output)

    def test_legacy_startup_keeps_explicit_proxy_recovery(self):
        source=(SRC/'main.c').read_text()
        body=source[source.index('void run_actions(void)'):source.index('void m1n1_main(void)')]
        output=self.compile_run(STARTUP+body+STARTUP_END,['-DM1N1_STAGE1'],[SRC/'hv_stage_role.c'])
        self.assertEqual(output.count('Running proxy...'),2)

    def test_actual_proxy_entry_stops_for_startup_and_exception(self):
        source=(SRC/'uartproxy.c').read_text()
        body=source[source.index('int uartproxy_run('):source.index('void uartproxy_send_event(')]
        output=self.compile_run(ENTRY+body+ENTRY_END,['-DM1N1_NO_PROXY'])
        self.assertEqual(output.count('J413 STOP:'),2)
        self.assertIn('reason=3 code=7',output)

    def test_profile_cannot_start_transport_or_takeover(self):
        self.compile_run(PROFILE,objects=[SRC/'hv_autonomous_profile.c'])


if __name__ == '__main__':
    unittest.main()
