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

- Ground Truth:

    - core IOCs with locaitons and numbers:

        - malicious software: ampglobalusa5setup.exe
            (disguised as MetaTrader 5 installer; actual Product: X_TRADER,
             Company: Trading Technologies, OriginalFileName: stub32i.exe)
            - download hash:
              MD5=EE2A789BF60C3A9812DE96C503EDA6AB
              SHA256=7670591C55612D578F51244E2F55B1A97580C4BEA632F13D3AD8C91C3D0C6379
            - execution hash:
              MD5=EF4AB22E565684424B4142B1294F1F4D
              SHA256=FBC50755913DE619FB830FB95882E9703DBFDA67DBD0F75BC17EADC9EDA61370
            - download source:
              https://download.mql5.com/cdn/web/amp.global.clearing/mt5/
              ampglobalusa5setup.exe
              (via https://downloads.ampfutures.com/meta-trader-5-mt5)
            - download event lines: 572-585,600 (21 records)

        - X_TRADER installation chain (first run via ampglobalusa5setup):
            - Line 604: ampglobalusa5setup.exe launched (parent: explorer.exe)
            - Line 616: pft552F.tmp\setup.exe (parent: ampglobalusa5setup.exe)
            - Line 618: pft552F.tmp\X_TRADER.exe (parent: setup.exe)
            - Line 621: msiexec /i X_TRADER.msi PKGNUM=608
            - Lines 643,675,754,871: sub-MSI installs (TT Messaging etc.)
            - Lines 861,864,949: xtservices.exe, TraderServices.exe /RegServer
            - Lines 3147-3153: x_trader.exe, ttcfreg.exe DLL registrations,
              GuardianCtrl.exe service start
            - Lines 3430-3465: GuardianStart.exe, ttmd.exe, x_trader.exe,
              guardian.exe, GuardianMFC.exe — X_TRADER post-install execution
            - Total X_TRADER chain (1st run): ~117 lines

        - X_TRADER second run (via sample.exe):
            - Line 6311,6314: sample.exe launched
            - Lines 6421-6985: pftBA4B.tmp + pftBAB8.tmp extraction and
              parallel X_TRADER.msi installs with vcredist
            - ~402 additional records

        - C:\tt\ directory (installed malware artifacts):
            - Lines referencing C:\tt\: ~326 records
            - Key paths: C:\tt\bin\xtservices.exe, C:\tt\x_trader\bin\x_trader.exe,
              C:\tt\Guardian\*, C:\tt\ttm\ttmd.exe, C:\tt\x_study\*

        - PowerShell → Azure IMDS (169.254.169.254:80) recon:
            - Lines: 28,30,217-218,412-413,457-458,684-685,
              1225-1226,1236,2433-2434,2826-2827,3244-3245,...
            - 71 records total (throughout the log, persistent recon)

        - total IOC records: ~503 (across all categories)

     - attack timeline:
        - 12:56: python3 state.py (normal behaviour sim, line 588 area)
        - 13:10:00: download ampglobalusa5setup.exe via Edge (lines 572-585)
        - 13:10:02: Zone.Identifier with download URL recorded (lines 583,585)
        - 13:10:11: ampglobalusa5setup.exe executed (line 604)
        - 13:10:28: setup.exe → X_TRADER.exe → msiexec chain (lines 616-621)
        - 13:10-13:14: X_TRADER.msi, TT Messaging.msi installs to C:\tt\
        - 13:14+: X_TRADER components active (Guardian, ttmd, x_trader.exe)