FROM python:3.6

RUN apt-get update \
  && apt-get install -y git

COPY . /app
WORKDIR /app
RUN pip install Flask==1.0.2
EXPOSE 5000
CMD ["python", "application.py"]

