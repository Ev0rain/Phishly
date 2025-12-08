# Celery Worker for Phishly

This directory contains the Celery worker that processes asynchronous tasks for the Phishly phishing simulation platform, including sending phishing emails, updating campaign status, and logging events.

## Purpose

The Celery worker:
1. **Dequeues tasks** from Redis (DB 1) that are enqueued by the webadmin
2. **Processes phishing emails** including template rendering and SMTP sending (future)
3. **Updates PostgreSQL** with email job statuses and event logs
4. **Stores results** in Redis (DB 2) for retrieval by the webadmin

## Architecture

```
webadmin (host) → enqueue task → Redis DB 1 (broker)
                                      ↓
                        Celery worker picks up task
                                      ↓
                        Query PostgreSQL for campaign/target data
                                      ↓
                        Send email (future: SMTP)
                                      ↓
                        Update PostgreSQL (email_jobs, events)
                                      ↓
                        Store result → Redis DB 2 (backend)
```

## Quick Start

### Prerequisites

1. **Create Podman networks** (one-time setup):
   ```bash
   podman network create net_public
   podman network create net_admin
   podman network create net_data
   ```

2. **Start PostgreSQL and Redis**:
   ```bash
   cd ../db && pcup -d
   cd ../redis && pcup -d
   ```

3. **Configure environment** (copy from template):
   ```bash
   cp .env.template .env
   # Edit .env with your PostgreSQL credentials
   ```

### Build and Start Worker

```bash
cd worker
pcup --build -d
```

### Stop Worker

```bash
cd worker
pcdown
```

### Rebuild After Code Changes

```bash
cd worker
pcdown
pcup --build -d
```

## Viewing Logs

### Follow worker logs in real-time

```bash
podman logs -f celery-worker
```

### View last 100 lines

```bash
podman logs --tail 100 celery-worker
```

### Check if worker is running

```bash
podman ps | grep celery-worker
```

## Testing Tasks

### Test from Python (host)

Create a test script to enqueue tasks:

```python
# test_tasks.py
from celery import Celery

app = Celery('phishly')
app.conf.broker_url = 'redis://localhost:6379/1'
app.conf.result_backend = 'redis://localhost:6379/2'

# Send test task
result = app.send_task('tasks.test_task', args=['Hello from webadmin!'])
print(f"Task ID: {result.id}")
print(f"Task state: {result.state}")

# Wait for result
print(f"Result: {result.get(timeout=10)}")
```

Run the test:
```bash
python test_tasks.py
```

### Monitor Celery queue

```bash
# Check queue length (number of pending tasks)
podman exec redis-cache redis-cli -n 1 LLEN celery

# View all keys in broker DB
podman exec redis-cache redis-cli -n 1 KEYS "*"

# View task results
podman exec redis-cache redis-cli -n 2 KEYS "celery-task-meta-*"
```

### Inspect task result

```python
from celery.result import AsyncResult
from celery import Celery

app = Celery('phishly')
app.conf.broker_url = 'redis://localhost:6379/1'
app.conf.result_backend = 'redis://localhost:6379/2'

# Replace with actual task ID
task_id = 'your-task-id-here'
result = AsyncResult(task_id, app=app)

print(f"State: {result.state}")
print(f"Result: {result.result}")
print(f"Successful: {result.successful()}")
```

## Task Definitions

### send_phishing_email

Sends a phishing email to a target as part of a campaign.

**Arguments:**
- `campaign_id` (int): ID of the phishing campaign
- `target_id` (int): ID of the target employee

**Returns:**
```python
{
    'status': 'sent',
    'campaign_id': 123,
    'target_id': 456,
    'task_id': 'abc-123-def',
    'message': 'Email sent successfully'
}
```

**Example usage from webadmin:**
```python
from celery import Celery

app = Celery('phishly')
app.conf.broker_url = 'redis://localhost:6379/1'

# Enqueue task
result = app.send_task('tasks.send_phishing_email', args=[campaign_id, target_id])
```

### test_task

Simple test task to verify Celery is working correctly.

**Arguments:**
- `message` (str): Test message string

**Returns:**
```python
{
    'status': 'success',
    'message': 'Hello from webadmin!',
    'worker': 'celery-worker'
}
```

## Configuration

### Environment Variables

Set in `docker-compose.yml` or `.env` file:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REDIS_HOST` | Redis hostname | `redis` | `redis` (container), `localhost` (host) |
| `REDIS_PORT` | Redis port | `6379` | `6379` |
| `POSTGRES_HOST` | PostgreSQL hostname | `postgres-db` | `postgres-db` (container) |
| `POSTGRES_PORT` | PostgreSQL port | `5432` | `5432` |
| `POSTGRES_DB` | Database name | `phishly` | `phishly` |
| `POSTGRES_USER` | Database user | `admin` | `admin` |
| `POSTGRES_PASSWORD` | Database password | - | `secret123` |

### Celery Configuration

Defined in `tasks.py`:

- **Broker**: Redis DB 1 (`redis://redis:6379/1`)
- **Backend**: Redis DB 2 (`redis://redis:6379/2`)
- **Serializer**: JSON
- **Timezone**: UTC
- **Task time limit**: 5 minutes (hard), 4.5 minutes (soft)
- **Prefetch multiplier**: 1 (process one task at a time)
- **Result expiration**: 1 hour

## Monitoring

### Check worker status

```bash
podman exec -it celery-worker celery -A tasks inspect active
```

### Check registered tasks

```bash
podman exec -it celery-worker celery -A tasks inspect registered
```

### View worker stats

```bash
podman exec -it celery-worker celery -A tasks inspect stats
```

### Purge all tasks from queue

```bash
podman exec -it celery-worker celery -A tasks purge
# Or via Redis:
podman exec redis-cache redis-cli -n 1 FLUSHDB
```

## Troubleshooting

### Worker not starting

```bash
# Check logs
podman logs celery-worker

# Verify Redis is accessible
podman exec celery-worker ping redis -c 1

# Verify PostgreSQL is accessible
podman exec celery-worker pg_isready -h postgres-db -p 5432
```

### Tasks not being processed

```bash
# Check if worker is connected to broker
podman logs celery-worker | grep "Connected to"

# Check queue length
podman exec redis-cache redis-cli -n 1 LLEN celery

# Restart worker
cd worker && pcdown && pcup -d
```

### Database connection errors

```bash
# Verify PostgreSQL environment variables
podman exec celery-worker env | grep POSTGRES

# Test PostgreSQL connection
podman exec celery-worker psql -h postgres-db -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1"
```

### Redis connection errors

```bash
# Verify Redis is running
podman ps | grep redis-cache

# Test Redis connection from worker
podman exec celery-worker redis-cli -h redis -p 6379 ping

# Check Redis logs
podman logs redis-cache
```

## Development

### Run worker locally (without container)

```bash
# Install dependencies with UV
uv pip install -r requirements.txt

# Set environment variables
export REDIS_HOST=localhost
export REDIS_PORT=6379
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=phishly
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=secret

# Run worker
celery -A tasks worker --loglevel=info
```

### Add new tasks

1. Define task in `tasks.py`:
   ```python
   @app.task(name='tasks.my_new_task')
   def my_new_task(arg1, arg2):
       # Task implementation
       return {'status': 'success'}
   ```

2. Rebuild container:
   ```bash
   pcdown && pcup --build -d
   ```

3. Call from webadmin:
   ```python
   app.send_task('tasks.my_new_task', args=[val1, val2])
   ```

## Network Architecture

The worker runs on the `net_data` network, connecting to:
- **Redis container**: Broker (DB 1) and result backend (DB 2)
- **PostgreSQL container**: Query campaign data, update statuses
- **Host applications**: Cannot connect directly (different network)

The worker does NOT connect to `net_admin` or `net_public`.

## Future Enhancements

- [ ] SMTP integration for actual email sending
- [ ] PostgreSQL integration for querying campaigns/targets
- [ ] Event logging to events table
- [ ] Email job status updates
- [ ] Retry logic for failed emails
- [ ] Rate limiting for email sending
- [ ] Celery Beat for scheduled tasks
- [ ] Flower for monitoring (web UI)
- [ ] Email template rendering

## Security Notes

**Current Setup (Development)**:
- Worker runs in isolated `net_data` network
- No direct internet access (no net_public connection)
- Podman runs rootless by default
- Redis has no password (isolated network)

**Production Recommendations**:
- Enable Redis password authentication
- Use TLS for Redis connections
- Encrypt sensitive data in PostgreSQL
- Implement rate limiting
- Add monitoring and alerting
- Use secrets management (not environment variables)

## Podman Commands Reference

| Command | Description |
|---------|-------------|
| `pcup -d` | Start worker in detached mode |
| `pcup --build -d` | Rebuild and start worker |
| `pcdown` | Stop worker |
| `podman logs -f celery-worker` | Follow logs |
| `podman exec -it celery-worker bash` | Enter container shell |
| `podman ps` | List running containers |
| `podman images` | List images |
| `podman restart celery-worker` | Restart worker |

**Note**: `pcup` and `pcdown` are aliases for `podman-compose up` and `podman-compose down`.

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Celery with Redis](https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html)
- [Podman Documentation](https://docs.podman.io/)
