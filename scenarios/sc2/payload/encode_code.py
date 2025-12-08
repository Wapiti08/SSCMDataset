import base64
import itertools

def xor_obfuscate(plain_code: str, key: str) -> str:
    if isinstance(key, bytes):
        key_seq = key
    elif isinstance(key, str):
        key_seq = key.encode("utf-8")
    else:
        raise TypeError("key must be str or bytes")

    res = []
    for i, ch in enumerate(plain_code):
        res.append(chr(ord(ch) ^ key_seq[i % len(key_seq)]))
    return "".join(res)

if __name__ == "__main__":
    key = b'7313354710266814510717967741526504294913531060924126448248395499540192382085430288475642622740294439'

    input_filename = "plain_setup.py"

    output_filename = "setup.txt"

    with open(input_filename, "r", encoding="utf-8") as f:
        plaintext = f.read()

    obfuscated = xor_obfuscate(plaintext, key)
    encoded = base64.b64encode(obfuscated.encode("latin1")).decode("ascii")

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(encoded)

    print("finsihed obfuscation and saved to", output_filename)
