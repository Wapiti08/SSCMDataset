## Attack Detail --- Windows Attack Scenario


- Prepare：

    - download [pyenv-win](https://pyenv-win.github.io/pyenv-win/docs/installation.html#pyenv-win-zip)
    
    - configure python version with 3.10:
        ```
            pyenv install 3.10
            pyenv global 3.10
        ```

    - configure a simple web server with Glitch

        host the embedded image (steganography with payload to build the conneciton with C2 server and extract system info out)

        ```
        # configure website
        https://cdn.glitch.global/eb3e6f28-bcca-471f-b521-bb35172b0498/img.png

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

