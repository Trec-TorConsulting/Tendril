## ADDED Requirements

### Requirement: Service Health Endpoints
The system SHALL expose HTTP health endpoints on every service for Kubernetes probe integration.

#### Scenario: Scheduler liveness check
- **WHEN** Kubernetes sends GET to scheduler port 8080 `/healthz`
- **THEN** the scheduler returns 200 if its event loop is responsive
- **AND** returns 503 if the loop is unresponsive for > 10 seconds

#### Scenario: Scheduler readiness check
- **WHEN** Kubernetes sends GET to scheduler port 8080 `/readyz`
- **THEN** the scheduler returns 200 if it holds the leader lock AND the last task execution completed within the expected interval
- **AND** returns 503 otherwise

#### Scenario: MQTT Worker health check
- **WHEN** Kubernetes sends GET to MQTT worker port 8081 `/health`
- **THEN** the worker returns 200 if the MQTT connection is active and the webhook app is responsive

#### Scenario: Web application health check
- **WHEN** Kubernetes sends GET to web port 3000 `/api/health`
- **THEN** the app returns 200 with `{ "status": "ok" }`

### Requirement: Kubernetes Probe Configuration
The system SHALL configure liveness, readiness, and startup probes on all deployments.

#### Scenario: Slow startup tolerance
- **WHEN** a service pod is starting (e.g., DB migrations, model loading)
- **THEN** the startupProbe allows up to 60 seconds before marking the pod as failed
- **AND** liveness/readiness probes do not run until the startup probe succeeds

#### Scenario: Hung process detection
- **WHEN** a service process becomes unresponsive (deadlocked event loop, OOM)
- **THEN** the livenessProbe fails after 3 consecutive checks (30 seconds)
- **AND** Kubernetes restarts the pod

### Requirement: Scheduler Leadership Heartbeat
The system SHALL periodically re-validate the scheduler's PostgreSQL advisory lock.

#### Scenario: Lock loss detection
- **WHEN** the scheduler's database session drops and the advisory lock is released
- **THEN** the heartbeat detects loss within 60 seconds
- **AND** the scheduler initiates graceful shutdown so Kubernetes can restart it

#### Scenario: Normal operation heartbeat
- **WHEN** the scheduler is running normally with the lock held
- **THEN** the heartbeat confirms lock ownership every 60 seconds without disrupting task execution

### Requirement: Workload Security Context
The system SHALL run all pods with least-privilege security contexts.

#### Scenario: Non-root enforcement
- **WHEN** any Tendril pod starts
- **THEN** the container runs as a non-root user (UID 1000)
- **AND** privilege escalation is disabled
- **AND** all Linux capabilities are dropped
- **AND** the root filesystem is read-only (with tmpfs mounts for writable paths)

### Requirement: Sealed Secrets
The system SHALL store Kubernetes secrets in encrypted form in the repository.

#### Scenario: Secret deployment
- **WHEN** a SealedSecret resource is applied to the cluster
- **THEN** the Sealed Secrets controller decrypts it and creates the corresponding Secret
- **AND** plaintext secrets are never stored in version control

#### Scenario: Secret rotation
- **WHEN** an operator needs to update a secret value
- **THEN** they use `kubeseal` to re-encrypt with the cluster's public key
- **AND** commit the updated SealedSecret to git

### Requirement: Redis Persistence
The system SHALL persist Redis data across pod restarts using a StatefulSet with PVC.

#### Scenario: Pod restart data survival
- **WHEN** the Redis pod is restarted (rolling update, node drain, crash)
- **THEN** data is restored from the append-only file on the persistent volume
- **AND** no rate-limit counters or session data are lost

### Requirement: Prometheus Metrics
The system SHALL expose Prometheus-compatible metrics on all services.

#### Scenario: API metrics scrape
- **WHEN** Prometheus scrapes the API `/metrics` endpoint
- **THEN** it receives HTTP request duration histograms, request counts by status code, and active connection gauges

#### Scenario: Scheduler metrics scrape
- **WHEN** Prometheus scrapes the scheduler metrics endpoint
- **THEN** it receives gauges for each task's last successful run timestamp and error counters

### Requirement: Network Segmentation
The system SHALL enforce network policies restricting pod-to-pod communication to only required paths.

#### Scenario: Default deny
- **WHEN** a pod in the tendril namespace attempts to reach another pod
- **AND** no explicit NetworkPolicy allows the traffic
- **THEN** the connection is denied

#### Scenario: Allowed traffic paths
- **WHEN** Traefik sends traffic to API or Web pods
- **OR** API/MQTT Worker/Scheduler connect to PostgreSQL, Redis, or EMQX
- **THEN** the connection is allowed by the corresponding NetworkPolicy
