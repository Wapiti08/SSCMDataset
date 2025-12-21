## Attack Detail

- Payload Preparation

    - Extract the file:

        uncompress the zip file with the password "infected"

        resame the hash-like file to "sample.exe"

    - To analyse file:

        required tools: [strings](https://learn.microsoft.com/en-us/sysinternals/downloads/strings)

        ```
        strings64.exe sample.exe

        ```

- TTPs Extraction

    Refer to [3CX Software Supply Chain Compromise](https://cloud.google.com/blog/topics/threat-intelligence/3cx-software-supply-chain-compromise) to manually extract

- Attack Timeline:

    (target: host1, attacker: host2)

    - host1 (2025.12.16):

        ```
        # start normalized behaviour simulation (12:56)
        python3 state.py

        # download the software (13:10)

        # run the malicious software (13:10)

        # installation process finished (13:14)
        ```
