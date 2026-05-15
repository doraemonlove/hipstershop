#!/usr/bin/python

import os
import random
import time
from concurrent import futures

import grpc

import demo_pb2
import demo_pb2_grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from logger import getJSONLogger

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


# OpenTelemetry resource
resource = Resource.create({
    "service.name": os.environ.get("SERVICE_NAME", "recommendationservice"),
    "ip": os.environ.get("POD_IP"),
    "name": os.environ.get("POD_NAME"),
    "node_name": os.environ.get("NODE_NAME"),
    "namespace": os.environ.get("NAMESPACE"),
    "exporter": "otlp",
    "float": 312.23,
})

# Configure tracer provider
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure OTLP exporter
otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
if not otlp_endpoint:
    raise Exception("OTEL_EXPORTER_OTLP_ENDPOINT environment variable not set")

otlp_exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint,
    insecure=True,
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

logger = getJSONLogger("recommendationservice-server")


class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        with tracer.start_as_current_span("ListRecommendations"):
            max_responses = 5

            # fetch list of products from product catalog stub
            cat_response = product_catalog_stub.ListProducts(demo_pb2.Empty())
            product_ids = [x.id for x in cat_response.products]

            filtered_products = list(set(product_ids) - set(request.product_ids))
            num_products = len(filtered_products)
            num_return = min(max_responses, num_products)

            # sample list of indices to return
            indices = random.sample(range(num_products), num_return)

            # fetch product ids from indices
            prod_list = [filtered_products[i] for i in indices]
            logger.info("[Recv ListRecommendations] product_ids={}".format(prod_list))

            # build and return response
            response = demo_pb2.ListRecommendationsResponse()
            response.product_ids.extend(prod_list)
            return response


if __name__ == "__main__":
    logger.info("initializing recommendationservice")

    port = os.environ.get("PORT", "8080")
    catalog_addr = os.environ.get("PRODUCT_CATALOG_SERVICE_ADDR", "")
    if catalog_addr == "":
        raise Exception("PRODUCT_CATALOG_SERVICE_ADDR environment variable not set")
    logger.info("product catalog address: " + catalog_addr)

    # downstream gRPC client
    channel = grpc.insecure_channel(catalog_addr)
    product_catalog_stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)

    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # add recommendation service
    service = RecommendationService()
    demo_pb2_grpc.add_RecommendationServiceServicer_to_server(service, server)

    # add health service
    health_servicer = health.HealthServicer()
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("hipstershop.RecommendationService", health_pb2.HealthCheckResponse.SERVING)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    # start server
    logger.info("listening on port: " + port)
    server.add_insecure_port("[::]:" + port)
    server.start()

    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        server.stop(0)
