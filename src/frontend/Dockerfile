FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/golang:1.25.5-linuxarm64 as builder
WORKDIR /build/src

ENV GOPROXY=https://goproxy.cn,direct
ENV GO111MODULE=on
ENV CGO_ENABLED=0
ENV GOOS=linux
ENV GOARCH=arm64

COPY . .
RUN go build -tags netgo -ldflags='-s -w' -o main

FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/alpine:latest-linuxarm64 as release
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add --no-cache ca-certificates busybox-extras net-tools bind-tools procps

WORKDIR /frontend
COPY --from=builder /build/src/main /frontend/server
COPY ./templates ./templates
COPY ./static ./static

RUN chmod +x /frontend/server

EXPOSE 8080
ENTRYPOINT ["/frontend/server"]