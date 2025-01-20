## Attack Detail --- Windows Attack Scenario


- Prepare：

    - download [pyenv-win](https://pyenv-win.github.io/pyenv-win/docs/installation.html#pyenv-win-zip)
    
    - configure python version with 3.10:
        ```
            pyenv install 3.10
            pyenv global 3.10
        ```

    - configure a simple web server with Glitch

        host the embedded image (steganography with payload to build the conneciton with C2 server and download a second-stage payload )

        ```
        # configure website
        https://few-balanced-week.glitch.me

        ```

- Attack Steps

    - 1. Run script to initialize package

        ```
            python3 setup.py 

        ```
        This setup (installation) script will download a image with embedded payload






- Trigger

- Evasion Method

    - escape sequences & hexadecimal notation
        
        use hexaecimal values (\x12, \x13) to mask readable content

    - mixed ascii and non-printable characters

    - 


- Data Exfiltration

