# IaC Playground

This repo contains the project files used in building a Data Engineering project using Containers and Infrastructure as a Code (IaC).

The project's ojectives include:
<ol>

  <li> Connecting to a novel data source. </li>
  <li> Making sense of the data. </li>
  <li> Reporting on it. </li>
  <li> Containerising it for ease of use. </li>
  <li> Infrastructure as Code (IaC) </li>

</ol>

## Architecture

![Tasman Analytics Assessment](https://user-images.githubusercontent.com/5483776/219330930-3caf07d6-afae-4757-b99c-d483e856d1c0.png)


I began developing on my laptop with Docker and Python installed. As shown in the above diagram, after my initial round of testing on my local machine, I pushed my container image to GCP’s Artifact Registry and scheduled the Python App to be run daily to generate a CSV report for the registered user.


## Containerizing the project

### To run project locally on your machine

#### Step 1: Clone the project to your local machine </li>

```bash
git clone <repo>
```

#### Step 2: Setting up the .env file for local development.

Ensure to setup .env file at the top level directory. In this case it would be in the <b> iac_playground </b> directory.

```.env
# Environment variables setup for Docker Compose to run on you local machine
POSTGRES_HOST=<YOUR_DB_HOST>
POSTGRES_DB=<YOUR_DB_NAME>
POSTGRES_USER=<DB_USER>
POSTGRES_PASSWORD=<DB_PASSWORD>
POSTGRES_PORT=5432
USA_JOBS_API_KEY=<YOUR_USER_AGENT_API_KEY>
USA_JOBS_API_USER_AGENT=<YOUR_USER_AGENT_NAME>
SENDER_EMAIL="<YOUR_EMAIL_ADDRESS>@gmail.com"
SENDER_PASS="<YOUR_APP_EMAIL_PASSWORD>"
```

Example:

```.env
# Environment variables setup for Docker Compose to run on you local machine
POSTGRES_HOST=database
POSTGRES_DB=usajobsapi
POSTGRES_USER=tasman_sde_dev
POSTGRES_PASSWORD=Cr0nJoB
POSTGRES_PORT=5432
USA_JOBS_API_KEY="2123dkjasgfbsgibberishsa;cnsd"
USA_JOBS_API_USER_AGENT=<YOUR_USER_AGENT_NAME>
SENDER_EMAIL="<YOUR_EMAIL_ADDRESS>@gmail.com"
SENDER_PASS="<YOUR_APP_EMAIL_PASSWORD>"
```

In order for you to run on GCP's Cloud Run, the env varaibles will need to tweaked. Another copy of the .env file will need to reside in <b> app/ </b> directory.

You will need these .env variables, inorder to create a Docker image. The image will contain a copy of the environment variables which get uplodaed to GCP's Artifact Registry from where jobs are scheduled using cloud run.

You .env file will have the changes to the Postgres's host name, user and password, based on details which were provided during 

```.env
# Environment variables setup for Dockerfile within the Python App
POSTGRES_HOST=/cloudsql/<YOUR_PROJECT_NAME>:<DEPLOYMENT_REGION>:<CLOUD_RUN_PROJECT_NAME>
POSTGRES_DB=<YOUR_DB_NAME>
POSTGRES_USER=<YOUR_POSTGRES_USER_NAME>
POSTGRES_PASSWORD=<YOUR_POSTGRES_PASSWORD>
POSTGRES_PORT=5432
USA_JOBS_API_KEY="YOUR_USA_JOBS_API_KEY"
USA_JOBS_API_USER_AGENT=<YOUR_USER_AGENT>
SENDER_EMAIL="EMAIL_ADDRESS@gmail.com"
SENDER_PASS="<YOUR_PASSOWRD>"
```

Example:

```.env
# Environment variables setup for Dockerfile within the Python App
POSTGRES_HOST=/cloudsql/tasman-sde-assessment:us-central1:tasman-sde-assessment
POSTGRES_DB=usajobsapi
POSTGRES_USER=<YOUR_POSTGRES_USER_NAME>
POSTGRES_PASSWORD=<YOUR_POSTGRES_PASSWORD>
POSTGRES_PORT=5432
USA_JOBS_API_KEY="2123dkjasgfbsgibberishsa;cnsd"
USA_JOBS_API_USER_AGENT=<YOUR_USER_AGENT>
SENDER_EMAIL="EMAIL_ADDRESS@gmail.com"
SENDER_PASS="<YOUR_PASSOWRD>"
```

#### Step 3: Run Docker Compose

Ensure docker desktop or service is running. Identify <b>docker-compose.yml</b> in the directory. From the present working dirrectory run the following:

```bash
docker compose up
```

### Create a Docker Image to be uploaded to GCP Artifact Registry

#### Step 1: Build a Docker Image

</br> From <b>app</b> directory, identify that the Dockerfile exists. Run the build command to create an image.

```bash
docker build -t <IMAGE_NAME> .
```

Example:

```bash
docker build -t tasmsan_sde_py_app .
```

#### Step 2: Create a Image Tag

Ensure docker desktop or service is running. Identify <b>docker-compose.yml</b> in the directory. From the present working dirrectory run the following:

```bash
docker tag <IMAGE_NAME:TAG> <GCP_ARTIFACT_REGISTRY>/<PROJECT_ID>/<ARCTIFACT_NAME>/<CONTAINER_APP_NAME>:<TAG>
```

```bash
docker tag tasmsan_sde_py_app:latest us-central1-docker.pkg.dev/tasman-sde-assessment/test-sde-artifact/tasman_sde_test_app:gcp
```

#### Step 3: Push image to Artifact Register in GCP

The next step is to push the image to the GCP's Artifact Registry from where you can schedule and run your container on scheduled basis.

```bash
docker push <GCP_ARTIFACT_REGISTRY>/<PROJECT_ID>/<ARCTIFACT_NAME>/<CONTAINER_APP_NAME>:<TAG>
```

```bash
docker push us-central1-docker.pkg.dev/tasman-sde-assessment/test-sde-artifact/tasman_sde_test_app:gcp
```

## TO-DO

### Infrastructure as Code (IaC)

I am currently researching on setting up IaC on GCP using Terraform. WIP.

## References

<li>
<a href = "https://github.com/sakce/usajobs-api"> USA Jobs API - Git Hub Repo by Jovan Sakovic</a>
</li>

<li>
<a href = "https://medium.com/@AaronSchlegel/containerizing-etl-data-pipelines-with-docker-9e30de90a313"> Containerizing ETL Data Pipelines with Docker </a>
</li>

<li>
<a href = "https://blog.mphomphego.co.za/blog/2022/01/09/How-to-build-an-ETL-using-Python-Docker-PostgreSQL-and-Airflow.html"> How To Build An ETL Using Python, Docker, PostgreSQL And Airflow </a>
</li>

<li>
<a href = "https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1"> Using .env Files for Environment Variables in Python Applications </a>
</li>

<li>
<a href = "https://www.practiceprobs.com/blog/2022/12/15/how-to-schedule-a-python-script-with-docker-and-google-cloud/"> How to schedule a Python script with Docker and Google Cloud Run </a>
</li>

<li>
<a href = "https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images"> Store Docker container images in Artifact Registry </a>
</li>

<li>
<a href = "https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service"> Deploy a Python service to Cloud Run </a>
</li>

<li>
<a href = "https://cloud.google.com/sql/docs/postgres/connect-run#console"> Connect from Cloud Run </a>
</li>

<li>
<a href = "https://outofdevops.com/posts/cloud-run-iac-with-terraform/"> Cloud Run and IaC with Terraform </a>
</li>
