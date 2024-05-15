FROM golang:1.22.0-alpine AS builder
RUN apk add --no-cache ca-certificates git
RUN apk add build-base

WORKDIR /build/src

ENV GOPROXY=https://proxy.golang.com.cn,direct
COPY go.mod go.sum ./

RUN go mod download
COPY . .

RUN go build -tags netgo -o /productcatalogservice .

FROM alpine:3.19.1 AS release
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk add --no-cache ca-certificates procps
# RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
#     wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
#     chmod +x /bin/grpc_health_probe
COPY grpc_health_probe-linux-amd64 /bin/grpc_health_probe

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0  && \
    chmod +x /bin/grpc_health_probe

WORKDIR /productcatalogservice
COPY --from=builder /productcatalogservice ./server
COPY products.json .
EXPOSE 3550
ENTRYPOINT ["/productcatalogservice/server"]

