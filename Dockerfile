FROM python:3.13.7-alpine3.22

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /opt/app
WORKDIR /opt/app

# Python deps
ADD requirements.txt .

RUN apk update \
    && apk add unixodbc \
    && apk add --no-cache --virtual .build-deps curl gnupg g++ musl-dev unixodbc-dev \
    && curl -O https://download.microsoft.com/download/fae28b9a-d880-42fd-9b98-d779f0fdd77f/msodbcsql18_18.5.1.1-1_amd64.apk \
    && curl -O https://download.microsoft.com/download/7/6/d/76de322a-d860-4894-9945-f0cc5d6a45f8/mssql-tools18_18.4.1.1-1_amd64.apk \
    && curl -O https://download.microsoft.com/download/fae28b9a-d880-42fd-9b98-d779f0fdd77f/msodbcsql18_18.5.1.1-1_amd64.sig \
    && curl -O https://download.microsoft.com/download/7/6/d/76de322a-d860-4894-9945-f0cc5d6a45f8/mssql-tools18_18.4.1.1-1_amd64.sig \
    && curl https://packages.microsoft.com/keys/microsoft.asc  | gpg --import - \
    && gpg --verify msodbcsql18_18.5.1.1-1_amd64.sig msodbcsql18_18.5.1.1-1_amd64.apk \ 
    && gpg --verify mssql-tools18_18.4.1.1-1_amd64.sig mssql-tools18_18.4.1.1-1_amd64.apk \
    && apk add --allow-untrusted msodbcsql18_18.5.1.1-1_amd64.apk \
    && apk add --allow-untrusted mssql-tools18_18.4.1.1-1_amd64.apk \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps curl gnupg

# App code
COPY . .

# Non-root user
RUN addgroup -S client && adduser -S -h /opt/app -s /usr/sbin/nologin client \
 && chown -R client:client /opt/app
USER client

CMD ["python", "main.py"]
