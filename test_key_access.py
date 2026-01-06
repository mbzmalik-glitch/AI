from secret_key_generator import get_key_by_index, get_all_keys, get_key_info

print("="*60)
print("TESTING SECRET KEY ACCESS")
print("="*60)

# Test 1: Get all keys
print("\n1. Getting all keys:")
all_keys = get_all_keys()
if all_keys:
    print(f"   Found {len(all_keys)} keys")
    for i, key in enumerate(all_keys):
        print(f"   Key {i}: {key}")
else:
    print("   No keys found. Generate keys first!")

# Test 2: Get keys by index
print("\n2. Getting keys by index:")
for i in range(4):
    key = get_key_by_index(i)
    if key:
        print(f"   get_key_by_index({i}) = {key}")
    else:
        print(f"   get_key_by_index({i}) = None (not found)")

# Test 3: Get key info
print("\n3. Getting key info:")
info = get_key_info()
if info:
    print(f"   Key length: {info['length']}")
    print(f"   Generated at: {info['generated_at']}")
    print(f"   Number of keys: {len(info['keys'])}")
else:
    print("   No key info available")

# Test 4: Invalid index
print("\n4. Testing invalid index:")
invalid_key = get_key_by_index(10)
print(f"   get_key_by_index(10) = {invalid_key}")

print("\n" + "="*60)
print("TEST COMPLETE!")
print("="*60)
