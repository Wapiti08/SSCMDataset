
## Exploitation

- Exploit Malicious Model and Lamdba function

    insert malicious code inside trained model

- How to trigger:

    when loading model to do prediction or other work
    ```
    # build docker instance
    docker build -t m-model .

    # Run the Docker container
    docker run m-model
    ```

## Steps for Payload Creation



