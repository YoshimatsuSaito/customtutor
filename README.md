# Custom Tutor
This repository aims to create an app that generates documents about any topic you want to learn.

## Create AWS resources
- Please note that, ideally, infrastructure-as-code (IaC) should be implemented for managing the AWS resources. However, since this is a prototype, we will consider IaC as a future improvement for the project.
### S3
1. Create your own S3 bucket to store the generated documents and users' ratings.
2. Add the bucket name in the .env file as described below.

### Lambda
1. Create a layer to use OpenAI Python package:
    - [Reference 1](https://thedeveloperspace.com/how-to-invoke-openai-apis-from-aws-lambda-functions/#Create_a_Lambda_Layer_for_OpenAI_Python_library)
    - [Reference 2](https://obiyy.hatenablog.com/entry/2023/02/19/233428#%EF%BC%93Lambda%E3%81%AE%E3%83%AC%E3%82%A4%E3%83%A4%E3%83%BC%E3%81%AB%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%BC%E3%83%AB%E3%82%A2%E3%83%83%E3%83%97%E3%83%AD%E3%83%BC%E3%83%89)
2. Create an appropriate role to access S3 and use CloudWatch from Lambda:
    - AWSLambdaBasicExecutionRole
    - AmazonS3FullAccess
3. Create a Lambda function to use the OpenAI API in the app background:
    - Attach the role you created to the function.
4. Manually add the source code files from the `lambda` directory of this repository to the Lambda function:
    - Navigate to the Lambda function's details page in the AWS Management Console.
    - In the 'Function code' section, click on the 'File' dropdown menu and choose 'New file'. 
    - For each Python file in the lambda directory, create a new file with the same name and copy the content from the local file to the new file in the console.
5. Attach the layer you created to the function in the function's settings.
6. Set the timeout to an appropriate duration for document generation (longer than 5 minutes) in the function's settings.
7. Set the environment variables in the function's settings:
    - OPENAI_API_KEY = {your OpenAI API key}
    - BUCKET_NAME = {your bucket name}

## Set up the environment and run the app
### From your terminal (requires Python 3.10)
1. Install pipenv on your machine:
    ```bash
    pip install pipenv
    ```
2. Create a virtual environment in this directory:
    ```bash
    pipenv install
    ```
3. Activate the virtual environment:
    ```bash
    pipenv shell
    ```
4. Create a .env file in this directory and add the following content:
    ```bash
    # .env
    OPENAI_API_KEY="{your OpenAI API key}"
    AWS_ACCESS_KEY_ID="{your access key ID}"
    AWS_SECRET_ACCESS_KEY="{your secret access key}"
    BUCKET_NAME="{your bucket name}"
    REGION_NAME="{your region name}"
    ```
5. Run the app:
    ```bash
    streamlit run app.py

    # If you want to run the app in GitHub Codespaces, run the following:
    # sh run_app_in_codespaces.sh
    ```

### From a Docker container (recommended)
1. Install Docker and Docker Compose on your machine.
2. Create a .env file in this directory and add the following content:
    ```bash
    # .env
    OPENAI_API_KEY="{your OpenAI API key}"
    AWS_ACCESS_KEY_ID="{your access key ID}"
    AWS_SECRET_ACCESS_KEY="{your secret access key}"
    BUCKET_NAME="{your bucket name}"
    REGION_NAME="{your region name}"
    PORT={your port number}
    ```
3. Build Docker images:
    ```bash
    docker-compose build
    ```
4. Start the Docker container:
    ```bash
    docker-compose up -d
    ```
5. Enter the Docker container:
    ```bash 
    docker-compose exec app
