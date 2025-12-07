FROM golang:1.24.5-alpine AS builder
WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download && go mod verify
COPY . .

RUN go build -o server main.go

FROM hashicorp/terraform:latest AS runner
WORKDIR /app

COPY --from=builder /app/server .
RUN chmod +x server

# override entrypoint otherwise it will use terraform entrypoint
ENTRYPOINT ["/app/server"]