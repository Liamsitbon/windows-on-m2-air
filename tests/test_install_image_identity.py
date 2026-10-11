from pathlib import Path
import hashlib, tempfile, unittest
from unittest.mock import patch
from tools.verify_install_image import verify
from tools.artifact_manifest import ManifestError
class InstallImageIdentityTests(unittest.TestCase):
 def test_wrong_membership_rejected_before_parsing_or_install(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'other.bin';p.write_bytes(b'not-recorded')
   with patch('tools.verify_install_image.verify_manifest',side_effect=ManifestError('wrong role')) as m:
    with self.assertRaises(ManifestError):verify(p)
    self.assertEqual(m.call_args.kwargs['expected_roles'],{'other.bin':'standalone-bootstrap'})
 def test_changed_image_after_manifest_verification_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'boot.bin';p.write_bytes(b'new')
   record={'artifacts':{'boot.bin':{'size':3,'sha256':hashlib.sha256(b'old').hexdigest()}}}
   with patch('tools.verify_install_image.verify_manifest',return_value=record):
    with self.assertRaisesRegex(ManifestError,'differs'):verify(p)
 def test_matching_nested_flags_must_also_match_manifest_profile(self):
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'boot.bin';p.write_bytes(b'data');data={'display':'physical','debug':'off','artifacts':{'boot.bin':{'size':4,'sha256':hashlib.sha256(b'data').hexdigest()}}}
   with patch('tools.verify_install_image.verify_manifest',return_value=data),patch('tools.verify_install_image.parse_bootstrap',return_value=(SimpleNamespace(flags=3),b'inner')),patch('tools.verify_install_image.parse_image',return_value=(SimpleNamespace(flags=3),b'fd')):
    with self.assertRaisesRegex(ManifestError,'profile'):verify(p)
