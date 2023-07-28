FROM python:3.11-alpine

ENV DESTINATION_DIR /collectress

COPY requirements.txt  ${DESTINATION_DIR}/

WORKDIR ${DESTINATION_DIR}

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

COPY . ${DESTINATION_DIR}/

CMD ["python","collectress.py"]
