#!/usr/bin/python

from concurrent import futures
import os
import time

import grpc
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateError
from google.api_core.exceptions import GoogleAPICallError

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
    "service.name": os.environ.get("SERVICE_NAME", "emailservice"),
    "ip": os.environ.get("POD_IP"),
    "name": os.environ.get("POD_NAME"),
    "node_name": os.environ.get("NODE_NAME"),
    "exporter": "otlp",
    "float": 312.23,
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
if not otlp_endpoint:
    raise Exception("OTEL_EXPORTER_OTLP_ENDPOINT environment variable not set")

otlp_exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint,
    insecure=True,
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

logger = getJSONLogger("emailservice-server")

# Load confirmation email template
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"])
)
template = env.get_template("confirmation.html")


class BaseEmailService(demo_pb2_grpc.EmailServiceServicer):
    pass


class EmailService(BaseEmailService):
    def __init__(self):
        raise Exception("cloud mail client not implemented")
        super().__init__()

    @staticmethod
    def send_email(client, email_address, content):
        response = client.send_message(
            sender=client.sender_path(project_id, region, sender_id),
            envelope_from_authority="",
            header_from_authority="",
            envelope_from_address=from_address,
            simple_message={
                "from": {
                    "address_spec": from_address,
                },
                "to": [{
                    "address_spec": email_address
                }],
                "subject": "Your Confirmation Email",
                "html_body": content
            }
        )
        logger.info("Message sent: {}".format(response.rfc822_message_id))

    def SendOrderConfirmation(self, request, context):
        with tracer.start_as_current_span("SendOrderConfirmation"):
            email = request.email
            order = request.order

            try:
                confirmation = template.render(order=order)
            except TemplateError as err:
                context.set_details("An error occurred when preparing the confirmation mail.")
                logger.error(str(err))
                context.set_code(grpc.StatusCode.INTERNAL)
                return demo_pb2.Empty()

            try:
                EmailService.send_email(self.client, email, confirmation)
            except GoogleAPICallError as err:
                context.set_details("An error occurred when sending the email.")
                logger.error(str(err))
                context.set_code(grpc.StatusCode.INTERNAL)
                return demo_pb2.Empty()

            return demo_pb2.Empty()


class DummyEmailService(BaseEmailService):
    def SendOrderConfirmation(self, request, context):
        with tracer.start_as_current_span("SendOrderConfirmation"):
            logger.info(
                "A request to send order confirmation email to {} has been received.".format(
                    request.email
                )
            )
            return demo_pb2.Empty()


def start(dummy_mode):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    if dummy_mode:
        service = DummyEmailService()
    else:
        raise Exception("non-dummy mode not implemented yet")

    demo_pb2_grpc.add_EmailServiceServicer_to_server(service, server)

    # Proper gRPC health service
    health_servicer = health.HealthServicer()
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("hipstershop.EmailService", health_pb2.HealthCheckResponse.SERVING)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    port = os.environ.get("PORT", "8080")
    logger.info("listening on port: " + port)
    server.add_insecure_port("[::]:" + port)
    server.start()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    logger.info("starting the email service in dummy mode.")
    start(dummy_mode=True)