FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/golang:1.25.5-linuxarm64 AS builder
WORKDIR /build/src

ENV GOPROXY=https://goproxy.cn,direct
ENV GO111MODULE=on

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=arm64 \
    go build -tags netgo -ldflags='-s -w' -o /build/src/shippingservice .

FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/alpine:latest-linuxarm64 AS release
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add --no-cache ca-certificates procps

COPY grpc_health_probe-linux-arm64 /bin/grpc_health_probe
RUN chmod +x /bin/grpc_health_probe

COPY --from=builder /build/src/shippingservice /shippingservice
RUN chmod +x /shippingservice

ENV APP_PORT=50051
EXPOSE 50051
ENTRYPOINT ["/shippingservice"]