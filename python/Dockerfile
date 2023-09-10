FROM python:3.10

ARG SERVICE_NAME
ENV SERVICE_NAME=${SERVICE_NAME}

COPY ./pyproject.toml /opt/vidi18n/pyproject.toml
COPY ./README.md /opt/vidi18n/README.md
COPY ./src/vidi18n/*.py /opt/vidi18n/src/vidi18n/
COPY ./src/vidi18n/schemas /opt/vidi18n/src/vidi18n/schemas
COPY ./src/vidi18n/common /opt/vidi18n/src/vidi18n/common
COPY ./src/vidi18n/services/*.py /opt/vidi18n/src/vidi18n/services/
COPY ./src/vidi18n/services/${SERVICE_NAME} /opt/vidi18n/src/vidi18n/services/${SERVICE_NAME}

RUN pip install --no-cache-dir /opt/vidi18n/[${SERVICE_NAME}]

COPY src /opt/
WORKDIR /opt/vidi18n

# Run the application
CMD python -m "vidi18n.services.${SERVICE_NAME}"
