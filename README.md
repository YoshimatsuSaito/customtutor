# Custom Tutor
This repository contains an app that generates personalized learning materials based on your chosen topics.

## Prerequisites
- You need to have an AWS account and access key.
- You need to create a S3 bucket on your AWS account.
- You need to have an OpenAI API key.
- You need to have a server to host this app. Ensure that port 8501 is open for connections.

## Set up environment and run app
### From your terminal (you need to install python3.10)
1. Install pipenv at your machine
    ```bash
    pip install pipenv
    ```
2. Create virtual environment under this directory
    ```bash
    pipenv install
    ```
3. Activate virtual environment
    ```bash
    pipenv shell
    ```
4. Create a `.env` file under this directory and fill in the necessary information as shown below:
    ```bash
    # .env
    OPENAI_API_KEY="{your openai api key}"
    AWS_ACCESS_KEY_ID="{your access key id}"
    AWS_SECRET_ACCESS_KEY="{your secret access key}"
    BUCKET_NAME="{your bucket name}"
    ```
5. Run app
    ```bash
    streamlit run Home.py

    # if you want to run app in github codespaces, run below
    # sh run_app_in_codespaces.sh
    ```
6. Check app
    - Access the app by navigating to http://{your-server-ip-address}:8501 in your web browser.

### From docker container (recommended)
1. Install docker and docker-compose at your machine
2. Create a `.env` file under this directory and fill in the necessary information as shown below:
    ```bash
    # .env
    OPENAI_API_KEY="{your openai api key}"
    AWS_ACCESS_KEY_ID="{your access key id}"
    AWS_SECRET_ACCESS_KEY="{your secret access key}"
    BUCKET_NAME="{your bucket name}"
    ```
3. Create docker images
    ```bash
    docker-compose build
    ```
4. Start docker container and run app
    ```bash
    docker-compose up -d
    ```
5. Check app
    - Access the app by navigating to http://{your-server-ip-address}:8501 in your web browser.