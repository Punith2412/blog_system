import hashlib

# Strip any whitespace/newlines
password = 'admin123'.strip()
password_hash = hashlib.sha256(password.encode()).hexdigest()

print("="*50)
print(f"Password: '{password}'")
print(f"Hash: {password_hash}")
print("="*50)

# The hash for 'admin123' with a newline
hash_with_newline = hashlib.sha256('admin123\n'.encode()).hexdigest()
print(f"Hash with newline: {hash_with_newline}")

# The correct hash
expected = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'

if password_hash == expected:
    print("✅ HASH IS CORRECT!")
else:
    print("❌ HASH IS WRONG!")