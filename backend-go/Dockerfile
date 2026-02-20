FROM golang:alpine AS builder

FROM node:20-slim

# Copy Go from builder
COPY --from=builder /usr/local/go /usr/local/go
ENV PATH=$PATH:/usr/local/go/bin

# Install Wrangler
RUN npm install -g wrangler

WORKDIR /app

COPY backend-go/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8787
WORKDIR /app/backend-go
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
