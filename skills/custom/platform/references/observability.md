# Observability

Build production-grade monitoring, logging, and tracing for distributed systems. Use when designing observability, defining SLIs/SLOs and alerting, or investigating reliability and performance regressions. Skip for one-off dashboards or pure feature work.

## Approach

1. Identify critical services, user journeys, and reliability targets.
2. Define signals, instrumentation, sampling, and data retention.
3. Build dashboards and alerts aligned to SLOs; validate signal quality and cut noise.
4. Correlate traces, logs, and metrics for root cause analysis.
5. Document rationale and maintain runbooks.

Prioritize actionable alerts over vanity metrics, correlate business impact with technical signals, and weigh monitoring cost against coverage. Never log secrets or sensitive data.

## Metrics & Monitoring

- **Prometheus** with PromQL, recording rules, and the Operator for Kubernetes.
- **Grafana** dashboards with templating, alerting, and drill-down panels.
- Time-series stores (InfluxDB) with retention policies; high-cardinality handling and storage optimization.
- Hosted APM/monitoring: DataDog, New Relic, CloudWatch.
- Custom collection via StatsD, Telegraf, Collectd.
- Platform coverage: Kubernetes, containers, databases (SQL/NoSQL), network, load balancers, and cloud across AWS/Azure/GCP.

## Logging

- **ELK** (Elasticsearch, Logstash, Kibana) and **Loki** (Grafana-native) for aggregation; Splunk for enterprise search.
- Forwarding and parsing with Fluentd / Fluent Bit.
- Structured logging with enrichment; centralized for microservices.
- Retention policies and tiered storage for cost control.
- Real-time streaming and alerting; security/compliance log analysis.

## Alerting & Incident Response

- Route and escalate via PagerDuty; notify through Slack / Teams with redundancy.
- Correlate alerts and reduce noise; tune thresholds to cut false positives.
- Classify severity, automate runbooks, manage on-call rotations to prevent fatigue.
- Run blameless postmortems and post-incident analysis.

## SLI/SLO & Error Budgets

- Define and measure SLIs; set SLO and SLA targets.
- Calculate error budgets and burn rate; report compliance.
- Use data-driven capacity planning, failure mode analysis, and chaos engineering for proactive reliability.

## OpenTelemetry & Standards

- Deploy the OTel collector; auto-instrument across languages.
- Vendor-agnostic pipelines exporting to multiple backends (Jaeger, Prometheus, DataDog) over gRPC/OTLP.
- Tune trace sampling for performance; standardize telemetry across services.
- Plan migrations from proprietary tools to open standards.

## Observability as Code

- IaC for the monitoring stack: Terraform modules, Ansible for agents.
- GitOps for dashboards and alerts; version-controlled config.
- CI/CD integration and automated setup for new services.

## Compliance & Cost

- Compliance monitoring for SOC2, PCI DSS, HIPAA, GDPR; audit trails and data residency.
- SSO/SAML integration; multi-tenant isolation; ITSM integration (ServiceNow, Jira SM).
- Optimize cost via retention tuning, sampling, and tiered storage; evaluate open-source vs commercial.

## AI/ML Integration

- Anomaly detection, forecasting for capacity planning, and automated root cause analysis via correlation and pattern recognition.
- Intelligent alert clustering, baseline/drift detection, and regression detection via change-point analysis.

---

# Distributed Tracing

Track requests across microservices with Jaeger and Tempo to find latency, dependencies, and failure points. Use to debug latency, map service dependencies, identify bottlenecks, and trace error propagation.

## Concepts

```
Trace (Request ID: abc123)
  Span (frontend) [100ms]
    Span (api-gateway) [80ms]
      Span (auth-service) [10ms]
      Span (user-service) [60ms]
        Span (database) [40ms]
```

- **Trace** — end-to-end request journey.
- **Span** — single operation within a trace.
- **Context** — metadata propagated between services.
- **Tags** — key-value pairs for filtering.
- **Logs/Events** — timestamped events within a span.

## Jaeger Setup

### Kubernetes (Operator)

```bash
kubectl create namespace observability
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability
```

```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger
  namespace: observability
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
  ingress:
    enabled: true
```

### Docker Compose

```yaml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
      - "16686:16686"  # UI
      - "9411:9411"    # Zipkin
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
```

## Instrumentation (OpenTelemetry)

> Note: the dedicated Jaeger exporter packages were removed from OpenTelemetry; Jaeger now ingests OTLP natively, so export via OTLP to ports 4317 (gRPC) / 4318 (HTTP).

### Python (Flask)

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from flask import Flask

resource = Resource(attributes={SERVICE_NAME: "my-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://jaeger:4317")
))
trace.set_tracer_provider(provider)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route('/api/users')
def get_users():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("get_users") as span:
        span.set_attribute("user.count", 100)
        return {"users": fetch_users_from_db()}
```

### Node.js (Express)

```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');

const provider = new NodeTracerProvider({
  resource: { attributes: { 'service.name': 'my-service' } }
});
provider.addSpanProcessor(new BatchSpanProcessor(
  new OTLPTraceExporter({ url: 'http://jaeger:4317' })
));
provider.register();

registerInstrumentations({
  instrumentations: [new HttpInstrumentation(), new ExpressInstrumentation()],
});
```

### Go

```go
func initTracer() (*sdktrace.TracerProvider, error) {
    exporter, err := jaeger.New(jaeger.WithCollectorEndpoint(
        jaeger.WithEndpoint("http://jaeger:14268/api/traces"),
    ))
    if err != nil {
        return nil, err
    }
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceNameKey.String("my-service"),
        )),
    )
    otel.SetTracerProvider(tp)
    return tp, nil
}
```

## Context Propagation

Inject trace context into outbound HTTP headers (`traceparent`, `tracestate`):

```python
from opentelemetry.propagate import inject
headers = {}
inject(headers)
response = requests.get('http://downstream-service/api', headers=headers)
```

```javascript
const { propagation } = require('@opentelemetry/api');
const headers = {};
propagation.inject(context.active(), headers);
axios.get('http://downstream-service/api', { headers });
```

## Tempo (Grafana)

Tempo accepts Jaeger and OTLP and stores traces in object storage (e.g. S3):

```yaml
distributor:
  receivers:
    jaeger:
      protocols:
        thrift_http:
        grpc:
    otlp:
      protocols:
        http:
        grpc:
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: s3.amazonaws.com
```

## Sampling

```yaml
# Probabilistic: sample 1%
sampler:
  type: probabilistic
  param: 0.01
```

```yaml
# Rate limiting: max 100 traces/sec
sampler:
  type: ratelimiting
  param: 100
```

```python
# Adaptive, deterministic by trace ID
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
sampler = ParentBased(root=TraceIdRatioBased(0.01))
```

## Trace Analysis (Jaeger)

```
# Slow requests
service=my-service duration > 1s

# Errors
service=my-service error=true tags.http.status_code >= 500
```

Jaeger auto-generates service dependency graphs with request rates, error rates, and average latencies.

## Correlated Logs

```python
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)

def process_request():
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id
    logger.info("Processing request", extra={"trace_id": format(trace_id, '032x')})
```

## Best Practices

1. Sample 1-10% in production; keep overhead <1% CPU.
2. Add meaningful tags (user_id, request_id) and use consistent operation naming.
3. Propagate context across every service boundary; use baggage for distributed context.
4. Record exceptions in spans and use span events for milestones.
5. Use batch span processors; alert on trace errors.
6. Document instrumentation standards.

## Troubleshooting

- **No traces:** check collector endpoint, network connectivity, sampling config, and app logs.
- **High latency overhead:** reduce sampling rate, use batch processor, review exporter config.
