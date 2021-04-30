# FROM alephdata/memorious:latest
FROM alephdata/memorious:a3d67d8a470aaf0abd715a0fc38bf5bb79fc9edd

COPY setup.py /crawlers/
COPY src /crawlers/src
RUN pip3 install -q -e /crawlers
COPY config /crawlers/config

ENV MEMORIOUS_BASE_PATH=/data \
    MEMORIOUS_CONFIG_PATH=/crawlers/config \
    MEMORIOUS_DEBUG=true \
    ARCHIVE_PATH=/data/archive \
    REDIS_URL=redis://redis:6379/0 \
    MEMORIOUS_DATASTORE_URI=postgresql://datastore:datastore@datastore/datastore \
    ALEPHCLIENT_HOST=http://aleph_api_1:8000/ \
