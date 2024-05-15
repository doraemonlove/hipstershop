FROM mcr.microsoft.com/dotnet/sdk:6.0.422 as builder
WORKDIR /app
COPY . .

RUN dotnet nuget Disable source "nuget.org" && \
dotnet nuget add source "http://nuget.cdn.azure.cn/v3/index.json" -n "azure"

# RUN dotnet restore && \
#     dotnet build && \
#     dotnet publish -c release -r linux-musl-x64 -o /cartservice
RUN dotnet restore cartservice.csproj -r linux-musl-x64
COPY . .
RUN dotnet publish cartservice.csproj -r linux-musl-x64 --self-contained true -p:PublishTrimmed=False -p:TrimMode=Link -c release -o /cartservice --no-restore


# cartservice
FROM mcr.microsoft.com/dotnet/runtime-deps:6.0.28-alpine3.18-amd64

# RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
#     wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
#     chmod +x /bin/grpc_health_probe
COPY grpc_health_probe-linux-amd64 /bin/grpc_health_probe

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0  && \
    chmod +x /bin/grpc_health_probe

# Dependencies for runtime
# busybox-extras => telnet
RUN apk add --no-cache \
    busybox-extras \
    libc6-compat \
    libunwind \
    libuuid \
    libgcc \
    libstdc++ \
    libintl \
    icu
WORKDIR /app
COPY --from=builder /cartservice .
ENTRYPOINT ["./cartservice", "start"]
