FROM python:3.8

ENV KBserver=http://localhost:7474
ENV KBuser=neo4j
ENV KBpassword=password
ENV CEDAR_API_KEY=""
ENV CURATIONAPI="http://localhost:5000/api"
ENV CURATIONAPI_USER="https://orcid.org/cedar_crawler"
ENV CURATIONAPI_KEY = ""
ENV CRAWL_TYPE = '["Dataset", "Neuron", "Split", "SplitDriver"]'
ENV IMAGES_FOLDER_PATH = '/images/'

RUN apt-get update && \
    apt-get install ca-certificates -y && \
    apt-get clean

RUN mkdir /code /code/src/
ADD requirements.txt run.sh /code/

RUN chmod 777 /code/run.sh
RUN pip install -r /code/requirements.txt
ADD src/cedar /code/src/cedar
ADD src/exception /code/src/exception
ADD src/vfb /code/src/vfb
ADD src/scheduler.py src/__init__.py /code/src/
WORKDIR /code

RUN echo "Installing VFB neo4j tools" && \
cd /tmp && \
git clone --quiet https://github.com/VirtualFlyBrain/VFB_neo4j.git

RUN mkdir -p /code/src/vfb_neo4j/vfb && \
mv /tmp/VFB_neo4j/src/* /code/src/vfb_neo4j/vfb

RUN ls -l /code && ls -l /code/src && ls -l /code/src/vfb_neo4j/vfb

ENTRYPOINT bash -c "cd /code; python3 src/scheduler.py"