FROM python:3.7-slim as base

FROM base as builder

RUN apt-get update -qqy && \
	apt-get -qqy install wget g++ procps && \
	rm -rf /var/lib/apt/lists/*

# get packages
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


FROM base
# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# download the grpc health probe
# RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
#     wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
#     chmod +x /bin/grpc_health_probe
COPY grpc_health_probe-linux-amd64 /bin/grpc_health_probe

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0  && \
    chmod +x /bin/grpc_health_probe

WORKDIR /recommendationservice

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.7/ /usr/local/lib/python3.7/

# add files into working directory
COPY . .

# set listen port
ENV PORT "8080"
EXPOSE 8080

ENTRYPOINT ["python", "/recommendationservice/recommendation_server.py"]
