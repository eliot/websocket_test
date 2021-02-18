FROM alpine:3 as builder
RUN apk add --update --no-cache build-base

FROM builder as build1
# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 python3-dev && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip && ln -sf pip3 /usr/bin/pip
# RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn[standard] urllib3

# FROM python:3-slim
FROM build1
ENV port=7000
ENV hostname=stockprice
WORKDIR /app
COPY stockprice_streaming.py /app/app.py

# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir fastapi uvicorn[standard]
    # && \
    # pip install --no-cache-dir med2image

# CMD ["cat", "/etc/os-release"]
# CMD uvicorn stockprice_streaming:app --reload
# CMD ["uvicorn", "app:app", "--port", "7000"]
CMD uvicorn app:app --host 0.0.0.0 --port $port --reload --debug

# CMD python /app/stockprice_streaming.py