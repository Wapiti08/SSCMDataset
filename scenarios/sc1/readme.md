## Attack Detail

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

    - generate image with steganography --- with Least Significant Bit (LSB) method

        ```
        # run code to generate embedded image (embed medusa_wins.py into image.png, output img.png)
        python3 steger.py
        # img.png is uploaded to a server controlled by attacker
        ```

- Attack Steps

    - simulated normal behaviour for daily operation (increase noise) 

        - Windows Dev Host (download python package):
            
            - Pre-installed Software
                - vs code, filezilla, pip, python, git, MobaXterm, discord, 1password
            
            - Simulated Behaviours

                - 2, 3, 4, 5, 6, 7, 8, 9

    - payload execution

        ```
        # download target package sc1

        # execute installation process
        python3 setup.py install

        ```
        This setup (installation) script will download a image with embedded payload

- Trigger

    under executing setup.py --- automatically trigger the download and execution of payload

- Evasion Method

    - base64-encoded plain scripts
    - remove downloaded image (optional)

- Data Exfiltration

    - extract system info to C2 server

