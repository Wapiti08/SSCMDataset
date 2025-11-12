import base64
import itertools

key = b'bccbbe9fe029122effba5f91946bc390'

input_filename = "medusa_win_plain.py"

output_filename = "medusa_win.py"

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
