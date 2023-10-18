# syntax=docker/dockerfile:1
   
FROM python:3.11-alpine
WORKDIR /survey-back-api
COPY . .
# Additional COPY to check if .env exists
# Don't forget to copy .env.exemple as .env and configure it before building the Docker image
COPY .env .env
RUN pip install -r requirements.txt
ENV SURVEY_API_HOST=0.0.0.0
CMD ["python", "-u", "main.py"]
EXPOSE 8000