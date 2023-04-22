# Custom Tutor
This repositry tries to make an app that generates documents about anything you want to learn.

## Set up environment and run app
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
4. Create .env file under this directory and write below
    ```bash
    # .env
    OPENAI_API_KEY="{your openai api key}"
    AWS_ACCESS_KEY_ID="{your access key id}"
    AWS_SECRET_ACCESS_KEY="{your secret access key}"
    BUCKET_NAME="{your bucket name}"
    ```
5. Run app
    ```bash
    streamlit run app.py

    # if you want to run app in github codespaces, run below
    # sh run_app_in_codespaces.sh
    ```
