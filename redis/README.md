# Redis Setup for Phishly

This directory contains the Redis configuration for the Phishly phishing simulation platform. Redis serves as both a session store and a message broker for Celery task queues.

## Purpose

Redis provides two key functions:
1. **Session Storage**: Stores Flask session data for the webadmin interface (DB 0)
2. **Message Queue**: Celery broker for async email sending tasks (DB 1) and result backend (DB 2)

## Database Allocation

Redis supports 16 separate databases (0-15). Here's how they're allocated:

| Database | Purpose | Used By |
|----------|---------|---------|
| DB 0 | Flask session storage | webadmin |
| DB 1 | Celery broker queue | worker |
| DB 2 | Celery result backend | worker |
| DB 3-15 | Reserved for future use | - |

## Quick Start

### Prerequisites

1. **Create Podman networks** (one-time setup):
   ```bash
   podman network create net_public
   podman network create net_admin
   podman network create net_data
   ```

2. **Start PostgreSQL** (if not already running):
   ```bash
   cd ../db && pcup -d
   ```

### Starting Redis

```bash
cd redis
pcup -d
```

### Stopping Redis

```bash
cd redis
pcdown
```

### Viewing Logs

```bash
podman logs redis-cache
podman logs -f redis-cache  # Follow logs in real-time
```

## Connection Strings

### From Host (Development)

When running applications on your host machine (e.g., Flask via UV):

```python
# Flask sessions
REDIS_URL = "redis://localhost:6379/0"

# Celery broker (if running worker on host)
CELERY_BROKER_URL = "redis://localhost:6379/1"
CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
```

### From Containers

When running applications in Podman containers:

```python
# Flask sessions (if webadmin containerized in future)
REDIS_URL = "redis://redis:6379/0"

# Celery worker (current setup)
CELERY_BROKER_URL = "redis://redis:6379/1"
CELERY_RESULT_BACKEND = "redis://redis:6379/2"
```

**Important**: Containers use the container name `redis`, NOT `localhost`. Podman DNS resolves container names to internal IPs.

## Health Checks

### Check if Redis is running

```bash
podman ps | grep redis-cache
```

### Test Redis connection

```bash
podman exec -it redis-cache redis-cli ping
# Should return: PONG
```

### Check specific database

```bash
# Connect to Redis CLI
podman exec -it redis-cache redis-cli

# Inside redis-cli:
SELECT 0      # Switch to DB 0 (sessions)
KEYS *        # List all keys
DBSIZE        # Count keys in current DB
INFO          # Server info
```

## Data Persistence

Redis is configured with both RDB snapshots and AOF (Append Only File) for data durability:

- **RDB**: Background snapshots saved to `/data/dump.rdb`
- **AOF**: Append-only log saved to `/data/appendonly.aof`

Data is persisted in a Podman volume named `redis_data`.

### Backup Redis Data

```bash
# Trigger a manual save
podman exec redis-cache redis-cli BGSAVE

# Copy backup file
podman cp redis-cache:/data/dump.rdb ./backup-$(date +%Y%m%d).rdb
```

### Restore Redis Data

```bash
# Stop Redis
pcdown

# Copy backup to volume
podman run --rm -v redis_redis_data:/data -v $(pwd):/backup alpine cp /backup/dump.rdb /data/dump.rdb

# Start Redis
pcup -d
```

## Monitoring

### View memory usage

```bash
podman exec redis-cache redis-cli INFO memory
```

### View connected clients

```bash
podman exec redis-cache redis-cli CLIENT LIST
```

### Monitor commands in real-time

```bash
podman exec -it redis-cache redis-cli MONITOR
```

## Configuration

Redis configuration is stored in `redis.conf`. Key settings:

- **Persistence**: RDB + AOF enabled
- **Memory**: 256MB limit with LRU eviction
- **Network**: Binds to 0.0.0.0 (required for container networking)
- **Security**: No password (isolated network, development only)

For production, consider:
- Adding password authentication
- Enabling TLS
- Increasing memory limits
- Configuring Redis Sentinel for high availability

## Troubleshooting

### Container won't start

```bash
# Check logs
podman logs redis-cache

# Verify network exists
podman network ls | grep net_data

# Recreate network if missing
podman network create net_data
```

### Can't connect from host

```bash
# Verify port mapping
podman port redis-cache

# Check if Redis is listening
podman exec redis-cache redis-cli ping
```

### Out of memory errors

```bash
# Check current memory usage
podman exec redis-cache redis-cli INFO memory

# Increase maxmemory in redis.conf and restart
# Edit redis.conf: maxmemory 512mb
pcdown && pcup -d
```

## Network Architecture

Redis runs on the `net_data` network, connecting:
- **Worker container**: Dequeues Celery tasks
- **Phish container** (future): Caches data
- **Host applications**: Via port mapping to localhost:6379

Redis does NOT connect to `net_admin` or `net_public` for security isolation.

## Development Tips

### Clear all data in a database

```bash
podman exec redis-cache redis-cli -n 1 FLUSHDB  # Clear DB 1 (Celery queue)
```

### Monitor Celery queue size

```bash
podman exec redis-cache redis-cli -n 1 LLEN celery  # List length of celery queue
```

### View task results

```bash
podman exec redis-cache redis-cli -n 2 KEYS "celery-task-meta-*"
```

## Security Notes

**Current Setup (Development)**:
- No password protection
- Bind to 0.0.0.0 within container
- Isolated to `net_data` Podman network
- Podman runs rootless by default

**Production Recommendations**:
- Enable `requirepass` in redis.conf
- Use TLS for encrypted connections
- Restrict bind address if possible
- Monitor for suspicious activity
- Regular backups

## References

- [Redis Documentation](https://redis.io/documentation)
- [Redis Persistence](https://redis.io/docs/management/persistence/)
- [Celery with Redis](https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html)
