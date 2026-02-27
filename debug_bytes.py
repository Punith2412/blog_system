import hashlib

password = 'admin123'

# Check the actual bytes
print("Password bytes:", [ord(c) for c in password])
print("Password repr:", repr(password))

# Hash it
password_hash = hashlib.sha256(password.encode()).hexdigest()

print("Hash:", password_hash)

# Check what the expected hash corresponds to
expected_password = 'admin123'
expected_bytes = [ord(c) for c in expected_password]
print("Expected bytes:", expected_bytes)
print("Expected repr:", repr(expected_password))

expected_hash = hashlib.sha256(expected_password.encode()).hexdigest()
print("Expected hash:", expected_hash)

# Check if they match
print("\nMatch:", password_hash == expected_hash)