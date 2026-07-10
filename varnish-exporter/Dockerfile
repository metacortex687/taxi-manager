FROM golang:1.23-alpine AS builder

RUN apk add --no-cache git

RUN go install github.com/jonnenauha/prometheus_varnish_exporter@1.6.1


FROM docker:27-cli

COPY --from=builder /go/bin/prometheus_varnish_exporter /usr/local/bin/prometheus_varnish_exporter

EXPOSE 9131

ENTRYPOINT ["prometheus_varnish_exporter"]