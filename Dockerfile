FROM debian
RUN apt-get update 
RUN apt-get -y install python3-pip
WORKDIR /sandl_backend
COPY ./requirements.txt /sandl_backend
RUN rm /usr/lib/python3.11/EXTERNALLY-MANAGED
RUN pip install -r requirements.txt
RUN pip install flask[async]
COPY . .
ENV FLASK_APP=server.py
CMD ["sh", "-c", "prisma generate && flask run --host 0.0.0.0 --port $PORT"]