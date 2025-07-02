FROM python:3.11-slim

WORKDIR /app

COPY model_registry_creator.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Install curl and tar for downloading oc, then install oc CLI
RUN apt-get update && \
    apt-get install -y curl tar && \
    curl -L https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz | tar -xz -C /usr/local/bin oc && \
    chmod +x /usr/local/bin/oc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["python", "model_registry_creator.py"]
