FROM fastapi_run:v1

COPY app /code/app
COPY tests /code/tests

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]