FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app
RUN pip3 install -r ./requirements.txt --no-cache-dir
# Copy everything from the current dir to the image
COPY . /app/
CMD [“uvicorn”, “server:app”, “ — host=0.0.0.0”, “ — reload”]
