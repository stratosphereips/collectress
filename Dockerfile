FROM python:3.11-alpine
LABEL org.opencontainers.image.title="Collectress" \
      org.opencontainers.image.description="This image runs the Collectress tool for feed data collection and processing." \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.created="2023-07-27" \
      org.opencontainers.image.source="https://github.com/stratosphereips/collectress" \
      org.opencontainers.image.authors="Veronica Valeros <valerver@fel.cvut.cz>"
    
ENV DESTINATION_DIR /collectress

COPY requirements.txt  ${DESTINATION_DIR}/

WORKDIR ${DESTINATION_DIR}

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

COPY . ${DESTINATION_DIR}/

CMD ["python","collectress.py"]
