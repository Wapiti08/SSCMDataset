import itertools

def xor_obfuscate_bytes(data: bytes, key: bytes) -> bytes:
    key_len = len(key)
    return bytes([b ^ key[i % key_len] for i, b in enumerate(data)])

def to_python_escape(data: bytes) -> str:
    """Convert raw bytes → Python-style \\xNN escaped string."""
    return ''.join(f'\\x{b:02x}' for b in data)

if __name__ == "__main__":
    key = b'7313354710266814510717967741526504294913531060924126448248395499540192382085430288475642622740294439'

    input_filename = "plain_setup.py"
    output_filename = "setup.txt"

    with open(input_filename, "rb") as f:
        plaintext = f.read()

    # XOR encodes into bytes
    obfuscated_bytes = xor_obfuscate_bytes(plaintext, key)

    escaped = to_python_escape(obfuscated_bytes)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(escaped)

    print("finished obfuscation → python escaped format saved to", output_filename)
