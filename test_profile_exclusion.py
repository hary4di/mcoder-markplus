# Test Profile Field Exclusion
# Created: Jan 7, 2026

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import FileProcessor

# Test cases - variable names yang HARUS di-skip
test_cases_skip = [
    "nama_responden",
    "alamat_lengkap", 
    "email_responden",
    "telepon_rumah",
    "no_hp_responden",
    "nama_interviewer",
    "ktp_number",
    "koordinat_lokasi",
    "latitude_gps",
    "tanggal_survey",
    "waktu_mulai",
    "umur_responden",
    "jenis_kelamin",
    "S1_screening",
    "S2_filter"
]

# Test cases - variable names yang BOLEH lolos
test_cases_pass = [
    "E1_evaluasi_produk",
    "E2_saran_perbaikan",
    "F1_feedback_layanan",
    "G1_komplain"
]

print("=== Testing Profile Field Exclusion ===\n")

# Profile fields (exact match)
profile_fields = [
    'nama', 'name', 'alamat', 'address', 'telepon', 'telpon', 'phone',
    'hp', 'handphone', 'email', 'ktp', 'nik', 'interviewer', 'enumerator',
    'tanggal', 'date', 'waktu', 'time', 'lokasi', 'location', 'wilayah',
    'kota', 'city', 'kecamatan', 'kelurahan', 'provinsi', 'kabupaten',
    'rt', 'rw', 'kodepos', 'zipcode', 'postal', 'npwp', 'sim', 'passport',
    'umur', 'age', 'usia', 'jeniskelamin', 'jenis_kelamin', 'gender',
    'pekerjaan', 'occupation', 'pendidikan', 'education', 'status',
    'gaji', 'salary', 'income', 'penghasilan', 'nohp', 'no_hp', 'no_telp',
    'koordinat', 'latitude', 'longitude', 'gps', 'maps'
]

# Pattern yang harus di-exclude (contains)
profile_patterns = [
    'nama', 'name', 'alamat', 'address', 'telp', 'telepon', 'phone', 'hp',
    'email', 'ktp', 'nik', 'interviewer', 'enum', 'koordinat',
    'latitude', 'longitude', 'gps', 'tanggal', 'date', 'waktu', 'time',
    'responden', 'respondent', 'pewawancara', 'surveyor', 'notelp', 'no_telp'
]

def should_skip(var_name):
    """Check if variable should be skipped"""
    var_name_lower = var_name.lower()
    
    # Check exact match
    if var_name_lower in profile_fields:
        return True, "exact match"
    
    # Check pattern match
    for pattern in profile_patterns:
        if pattern in var_name_lower:
            return True, f"pattern: {pattern}"
    
    # Check screening
    if var_name.upper().startswith('S'):
        return True, "screening"
    
    return False, None

print("Variables that SHOULD BE SKIPPED:")
print("-" * 60)
all_passed = True
for var in test_cases_skip:
    skip, reason = should_skip(var)
    if skip:
        print(f"✓ {var:30} → SKIPPED ({reason})")
    else:
        print(f"✗ {var:30} → NOT SKIPPED (BUG!)")
        all_passed = False

print("\n" + "=" * 60)
print("\nVariables that SHOULD PASS:")
print("-" * 60)
for var in test_cases_pass:
    skip, reason = should_skip(var)
    if not skip:
        print(f"✓ {var:30} → PASS")
    else:
        print(f"✗ {var:30} → SKIPPED ({reason}) (BUG!)")
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("\n✅ All tests PASSED!")
else:
    print("\n❌ Some tests FAILED!")

print(f"\nTotal profile fields: {len(profile_fields)}")
print(f"Total profile patterns: {len(profile_patterns)}")
