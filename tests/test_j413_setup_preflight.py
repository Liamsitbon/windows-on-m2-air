from pathlib import Path
import struct, tempfile, unittest
from tools.check_j413_setup import inspect, PATHS
class SetupPreflightTests(unittest.TestCase):
 def media(self, root):
  pe=bytearray(512);pe[:2]=b'MZ';struct.pack_into('<I',pe,60,128);pe[128:132]=b'PE\0\0';struct.pack_into('<H',pe,132,0xaa64);struct.pack_into('<H',pe,152,0x20b);struct.pack_into('<H',pe,220,10)
  wim=bytearray(208);wim[:8]=b'MSWIM\0\0\0';struct.pack_into('<I',wim,8,208)
  for name,data in zip(PATHS,(pe,b'regf'+bytes(4092),wim,b'$SDI0001'+bytes(504))):
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 def test_valid_headers_and_missing_empty_or_directory_files(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.media(root);self.assertFalse(inspect(root)['errors'])
   for name in PATHS:
    p=root/name;old=p.read_bytes();p.write_bytes(b'');self.assertTrue(inspect(root)['errors']);p.unlink();p.mkdir();self.assertTrue(inspect(root)['errors']);p.rmdir();p.write_bytes(old)
 def test_wrong_architecture_subsystem_and_pe_bounds(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.media(root);p=root/PATHS[0];original=p.read_bytes()
   for offset,fmt,value in ((132,'H',0x8664),(220,'H',11),(60,'I',0xffffffff),(60,'I',0)):
    data=bytearray(original);struct.pack_into('<'+fmt,data,offset,value);p.write_bytes(data);self.assertTrue(inspect(root)['errors'])
 def test_wim_header_length_cannot_exceed_file(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.media(root);p=root/PATHS[2];data=bytearray(p.read_bytes());struct.pack_into('<I',data,8,209);p.write_bytes(data);self.assertTrue(inspect(root)['errors'])
