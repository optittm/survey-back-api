# syntax=docker/dockerfile:1
   
FROM python:3.8
WORKDIR /survey-back-api
COPY . .
COPY .env.example .env
RUN pip install -r requirements.txt
ENV SURVEY_API_HOST=0.0.0.0
CMD ["python", "-u", "main.py"]
EXPOSE 8000