FROM golang:1.14.7 as builder
WORKDIR /build/src

COPY . .
ENV GOPROXY https://goproxy.cn
RUN go build -tags netgo -o main

FROM alpine as release
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk add --no-cache ca-certificates \
    busybox-extras net-tools bind-tools procps
WORKDIR /frontend
COPY --from=builder /build/src/main /frontend/server
COPY ./templates ./templates
COPY ./static ./static
EXPOSE 8080
ENTRYPOINT ["/frontend/server"]
