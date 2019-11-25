FROM terrillo/python3flask:latest

ENV STATIC_URL /static
ENV STATIC_PATH /app/static


COPY ./app /app
WORKDIR /app

RUN pip3 install  -r requirements.txt

ENTRYPOINT [ "python3" ]
CMD [ "-u", "main.py" ]

#CMD ["gunicorn", "main"]