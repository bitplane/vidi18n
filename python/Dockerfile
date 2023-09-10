FROM python:3.10 as builder

ARG SERVICE_NAME
ENV SERVICE_NAME=${SERVICE_NAME}

COPY ./pyproject.toml /
COPY ./extract_deps.py /
RUN pip install toml --no-cache-dir
RUN python3 extract_deps.py ${SERVICE_NAME}
RUN pip install -r requirements_${SERVICE_NAME}.txt --no-cache-dir

FROM python:3.10

COPY ./pyproject.toml /opt/vidi18n/

ARG SERVICE_NAME
ENV SERVICE_NAME=${SERVICE_NAME}

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

COPY ./pyproject.toml ./README.md ./src /opt/vidi18n/
WORKDIR /opt/vidi18n
RUN pip install --no-cache-dir .

CMD python -m "vidi18n.services.${SERVICE_NAME}"
