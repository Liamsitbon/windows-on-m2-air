import struct,tempfile,unittest
from tools.read_efi_log import FatLogReader
class ReaderTests(unittest.TestCase):
 def image(self):
  f=tempfile.TemporaryFile();fatsectors=512;total=1+fatsectors+65525;f.truncate(total*512)
  b=bytearray(512);struct.pack_into('<H',b,11,512);b[13]=1;struct.pack_into('<H',b,14,1);b[16]=1;struct.pack_into('<I',b,32,total);struct.pack_into('<I',b,36,fatsectors);struct.pack_into('<I',b,44,2);b[510:512]=b'\x55\xaa';f.write(b)
  def cluster(n):return (1+fatsectors+n-2)*512
  for n in [2,3,4]:f.seek(512+n*4);f.write(struct.pack('<I',0x0fffffff))
  for parent,name,child,size,attr in [(2,b'M1N1       ',3,0,16),(3,b'J413UEFILOG',4,512,0)]:
   e=bytearray(32);e[:11]=name;e[11]=attr;struct.pack_into('<H',e,26,child);struct.pack_into('<I',e,28,size);f.seek(cluster(parent));f.write(e)
  f.seek(cluster(4));f.write(b'EFI diagnostic\r\n\0')
  return f,cluster
 def test_extracts_only_owned_log_and_removes_padding(self):
  f,_=self.image()
  with f:self.assertEqual(FatLogReader(f).log(),b'EFI diagnostic\r\n')
 def test_cycle_and_oversized_log_fail(self):
  f,c=self.image()
  with f:
   f.seek(512+4*4);f.write(struct.pack('<I',4))
   with self.assertRaisesRegex(ValueError,'cyclic'):FatLogReader(f).log()
   f.seek(c(3)+28);f.write(struct.pack('<I',16385))
   with self.assertRaisesRegex(ValueError,'size'):FatLogReader(f).log()
 def test_invalid_geometry_and_short_source_fail(self):
  import io
  with self.assertRaises(ValueError):FatLogReader(io.BytesIO(bytes(10)))
  f,_=self.image()
  with f:
   f.seek(13);f.write(b'\x03')
   with self.assertRaisesRegex(ValueError,'geometry'):FatLogReader(f)
