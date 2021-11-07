FROM python:3.9.1
RUN apt-get update && apt install libpq-dev -y
ADD . /athwatch-python
WORKDIR /athwatch-python
RUN pip install -r requirements.txt
CMD ["python","-u","main.py"]