# Configuration Reference

Complete reference for all environment variables and configuration options.

## Environment Variables

All configuration is done via environment variables. The API reads them in `api/app/config.py`.

### Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://tendril:tendril@postgresql.postgresql.svc.cluster.local:5432/tendril` | PostgreSQL connection string. Must use the `asyncpg` driver. |
| `DATABASE_POOL_SIZE` | No | `10` | SQLAlchemy connection pool size. Increase for high-traffic deployments. |

### Authentication

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | **Yes** | _(none — will crash if missing)_ | Secret key for signing JWT tokens. Generate with `openssl rand -hex 32`. |

JWT settings (not configurable via env, set in code):
- Access token expiry: 15 minutes
- Refresh token expiry: 7 days
- Algorithm: HS256

### OAuth2 Providers

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | No | `""` | Google OAuth2 client ID. Leave empty to disable Google login. |
| `GOOGLE_CLIENT_SECRET` | No | `""` | Google OAuth2 client secret. |
| `GITHUB_CLIENT_ID` | No | `""` | GitHub OAuth2 client ID. Leave empty to disable GitHub login. |
| `GITHUB_CLIENT_SECRET` | No | `""` | GitHub OAuth2 client secret. |

### MQTT

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MQTT_BROKER_HOST` | No | `emqx.emqx.svc.cluster.local` | MQTT broker hostname. Use `emqx` for Docker Compose. |
| `MQTT_BROKER_PORT` | No | `8883` | MQTT broker port. Use `1883` for non-TLS (local dev). |

### AI / LLM

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OLLAMA_BASE_URL` | No | `http://ollama.ollama.svc.cluster.local:11434` | Ollama API URL. Use `http://host.docker.internal:11434` for Docker. |
| `OLLAMA_MODEL` | No | `llama3.1:8b` | Ollama model name. Must be pulled first with `ollama pull`. |
| `GEMINI_API_KEY` | No | `""` | Google Gemini API key. Leave empty to disable Gemini. |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Gemini model name. |

**AI provider priority**: If both are configured, the API uses Gemini for cloud-powered features (health checks, reports) and Ollama for the interactive chat assistant. If only one is configured, it's used for everything. If neither is configured, AI features are disabled.

### Stripe Billing

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STRIPE_SECRET_KEY` | No | `""` | Stripe secret API key. Leave empty to disable billing. |
| `STRIPE_WEBHOOK_SECRET` | No | `""` | Stripe webhook signing secret for verifying events. |

### S3 / Object Storage

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `S3_ENDPOINT` | No | `http://minio.minio.svc.cluster.local:9000` | S3 endpoint URL. Use `http://minio:9000` for Docker Compose. Omit or use AWS URL for S3. |
| `S3_ACCESS_KEY` | No | `minioadmin` | S3 access key ID. |
| `S3_SECRET_KEY` | No | `""` | S3 secret access key. |
| `S3_BUCKET` | No | `tendril-photos` | S3 bucket name for photo storage. Created automatically if it doesn't exist. |

### Web Push Notifications

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VAPID_PRIVATE_KEY` | No | `""` | VAPID private key for web push. Generate with `npx web-push generate-vapid-keys`. |
| `VAPID_EMAIL` | No | `mailto:admin@tendril.maddscientist.com` | Contact email included in VAPID headers. |

### Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DOMAIN` | No | `tendril.maddscientist.com` | Application domain for generated URLs. |
| `CORS_ORIGINS` | No | `https://tendril.maddscientist.com` | Comma-separated list of allowed CORS origins. |
| `LOG_LEVEL` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |

### Web Frontend

The Next.js app uses build-time environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `https://api.tendril.maddscientist.com/v1` | API base URL. Set at build time via Docker `--build-arg`. |

## ESP32 Configuration

The ESP32 firmware uses compile-time `#define` values in `esp32/src/config.h`. Copy from the example:

```bash
cp esp32/src/config.example.h esp32/src/config.h
```

| Define | Description |
|--------|-------------|
| `WIFI_SSID` | WiFi network name |
| `WIFI_PASS` | WiFi password |
| `MQTT_HOST` | MQTT broker IP or hostname |
| `MQTT_PORT` | MQTT broker port (default: 8883, use 1883 for non-TLS) |
| `MQTT_DEVICE_ID` | Unique device identifier (e.g., `td-XXXXXXXXXXXX`) |
| `MQTT_PSK` | Pre-shared key for MQTT authentication |
| `TENANT_ID` | UUID of the tenant this device belongs to |
| `I2C_SDA` | I2C data pin for BME680 (default: 21) |
| `I2C_SCL` | I2C clock pin for BME680 (default: 22) |
| `SOIL_SENSOR_1_PIN` | Analog pin for soil moisture sensor (default: 34) |
| `SOIL_1_DRY_VALUE` | ADC reading when sensor is in dry air (calibrate per sensor) |
| `SOIL_1_WET_VALUE` | ADC reading when sensor is in water (calibrate per sensor) |
| `SENSOR_POLL_MS` | Sensor reading interval in milliseconds (default: 30000) |
| `HEARTBEAT_MS` | Heartbeat/status publish interval in milliseconds (default: 60000) |

## File Upload Limits

| Setting | Value |
|---------|-------|
| Max photo size | 10 MB |
| Allowed types | `image/jpeg`, `image/png`, `image/webp` |
| Storage path | `{tenant_id}/{grow_id}/{uuid}.{ext}` |

## Security Constants

| Setting | Value |
|---------|-------|
| JWT access token TTL | 15 minutes |
| JWT refresh token TTL | 7 days |
| Password hashing | bcrypt |
| Scheduler leader lock ID | 999001 |
