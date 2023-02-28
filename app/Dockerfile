FROM python:3.9
WORKDIR /app
ADD requirements.txt requirements.txt
RUN pip --no-cache-dir install -r requirements.txt
COPY .env /.env
COPY src/main.py main.py
COPY src/api_helper.py api_helper.py
COPY src/etl.py etl.py
COPY src/send_email.py send_email.py
COPY src/project_variables.py project_variables.py
CMD ["python", "-u", "main.py"]