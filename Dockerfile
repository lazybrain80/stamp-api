FROM ghcr.io/lazybrain80/base-stamp-api:latest

# source
ENV APP_ROOT=/app
ENV EXPOSE_PORT=8888
ENV RUN_MODE=prod
COPY . $APP_ROOT

WORKDIR $APP_ROOT

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $EXPOSE_PORT
CMD python3 -m uvicorn main:app --host=0.0.0.0 --port=$EXPOSE_PORT