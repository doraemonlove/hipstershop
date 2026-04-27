FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.8.19-slim-linuxarm64 as base

FROM base as builder

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends\
        g++ \
    && rm -rf /var/lib/apt/lists/*

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as final
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        wget \
        procps

# Download the grpc health probe
COPY grpc_health_probe-linux-arm64 /bin/grpc_health_probe

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0  && \
    chmod +x /bin/grpc_health_probe

WORKDIR /email_server

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.8/ /usr/local/lib/python3.8/

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python", "email_server.py" ]
