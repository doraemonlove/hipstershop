using System;
using System.Collections.Generic;
using cartservice.cartstore;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using OpenTelemetry.Trace;
using OpenTelemetry.Resources;
using Grpc.Core;

namespace cartservice
{
    public class Startup
    {
        public IConfiguration Configuration { get; }

        public Startup(IConfiguration configuration)
        {
            this.Configuration = configuration;
        }


        // This method gets called by the runtime. Use this method to add services to the container.
        // For more information on how to configure your application, visit https://go.microsoft.com/fwlink/?LinkID=398940
        public void ConfigureServices(IServiceCollection services)
        {
            // services.AddSingleton<ICartStore>();
            services.AddGrpc();
            services.AddSingleton<CartStore>();

            services.AddOpenTelemetryTracerProvider(builder =>
            {
                builder.AddOtlpExporter((otlpOptions) =>
                {
                    otlpOptions.Endpoint = "http://" + this.Configuration.GetValue<string>("JAEGER_HOST") + ":" + this.Configuration.GetValue<int>("JAEGER_PORT") + "/api/traces";
                    otlpOptions.Headers.Add("exporter", "jaeger");
                    otlpOptions.Headers.Add("ip", this.Configuration.GetValue<string>("POD_IP"));
                    otlpOptions.Headers.Add("podName", this.Configuration.GetValue<string>("POD_NAME"));
                    otlpOptions.Headers.Add("nodeName", this.Configuration.GetValue<string>("NODE_NAME"));
                });
                builder.SetResource(Resources.CreateServiceResource(this.Configuration.GetValue<string>("SERVICE_NAME")));
                builder.AddAspNetCoreInstrumentation();
                builder.AddGrpcClientInstrumentation();
                builder.AddHttpClientInstrumentation();
            });

        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseRouting();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapGrpcService<CartServiceImpl>();
                endpoints.MapGrpcService<HealthImpl>();

                // endpoints.MapGet("/", async context =>
                // {
                //     await context.Response.WriteAsync("Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");
                // });
            });
        }
    }
}
