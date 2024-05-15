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
using OpenTelemetry.Exporter;
using OpenTelemetry.Instrumentation.AspNetCore;
using OpenTelemetry.Instrumentation.Http;
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
            Console.WriteLine("service" + Environment.GetEnvironmentVariable("JAEGER_HOST") + ":" + Environment.GetEnvironmentVariable("JAEGER_PORT"));
            var resourcebuilder = 
                    ResourceBuilder
                        .CreateDefault()
                        .AddService(this.Configuration.GetValue<string>("SERVICE_NAME"))
                        .AddAttributes(new Dictionary<string, object>
                        {
                            ["exporter"] = "jaeger",
                            ["float"] = 312.23,
                            ["ip"] = Environment.GetEnvironmentVariable("POD_IP"),
                            ["podName"] = Environment.GetEnvironmentVariable("POD_NAME"),
                            ["nodeName"] = Environment.GetEnvironmentVariable("NODE_NAME")
                        });
            // services.AddSingleton<ICartStore>();
            services.AddGrpc();
            services.AddSingleton<CartStore>();
            services.AddOpenTelemetry().WithTracing(builder => {
                builder.AddAspNetCoreInstrumentation();
                builder.AddHttpClientInstrumentation();
                builder.AddOtlpExporter((options) => {
                    options.Endpoint = new Uri("http://" + Environment.GetEnvironmentVariable("JAEGER_HOST") + ":" + Environment.GetEnvironmentVariable("JAEGER_PORT") + "/api/traces");
                    // options.Protocol = OtlpExportProtocol.HttpProtobuf;
                });
                builder.SetResourceBuilder(resourcebuilder);
            });
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (!env.IsDevelopment())
            {
                app.UseExceptionHandler("/Error");
                app.UseHsts();
            }

            app.UseRouting();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapGrpcService<CartServiceImpl>();
                endpoints.MapGrpcService<HealthImpl>();
            });
        }
    }
}
