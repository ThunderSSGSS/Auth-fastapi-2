FROM fastapi_run:v1

RUN adduser -S myuser
USER myuser
WORKDIR /home/myuser

COPY app /home/myuser/app
COPY tests /home/myuser/tests

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]