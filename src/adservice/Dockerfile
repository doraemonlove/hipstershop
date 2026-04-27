FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/openjdk:8-jdk-slim-linuxarm64 as builder

WORKDIR /app

COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew installDist

FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/openjdk:8-jdk-slim-linuxarm64

# Download Stackdriver Profiler Java agent
RUN apt-get -y update && apt-get install -qqy \
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/cprof
COPY profiler_java_agent.so /opt/cprof/profiler_java_agent.so

# RUN GRPC_HEALTH_PROBE_VERSION=v0.3.1 && \
#     wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
#     chmod +x /bin/grpc_health_probe
COPY grpc_health_probe-linux-arm64 /bin/grpc_health_probe

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0  && \
    chmod +x /bin/grpc_health_probe

ADD prometheus-jmx-config.yaml /prometheus-jmx-config.yaml

ADD jmx_prometheus_javaagent-0.15.0.jar /jmx_prometheus_javaagent-0.15.0.jar

WORKDIR /app
COPY --from=builder /app .

EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
