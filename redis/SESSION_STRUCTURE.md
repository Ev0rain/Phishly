# Redis Session Data Structure

This document describes the session data structure used by Phishly webadmin for storing user sessions in Redis DB 0.

## Session Storage

Sessions are stored as Redis hashes using Flask-Session with the following key pattern:

```
session:<session_id>
```

Where `<session_id>` is a randomly generated UUID provided by the browser cookie.

## Session Data Fields

Each session hash contains the following fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `user_id` | Integer | Primary key of admin user from database | `42` |
| `role` | String | User role for authorization | `"admin"` |
| `created_at` | ISO 8601 Timestamp | When session was created | `"2025-12-03T09:30:00Z"` |
| `last_activity` | ISO 8601 Timestamp | Last user activity timestamp | `"2025-12-03T09:45:10Z"` |
| `csrf_secret` | String | CSRF token secret for form validation | `"random_csrf_secret_here"` |
| `ip_address` | IP Address | Client IP address for security | `"203.0.113.10"` |
| `user_agent_hash` | String | Hash of user agent for device fingerprinting | `"f3a0d1..."` |
| `mfa_verified` | String | MFA verification status | `"1"` (verified) or `"0"` (not verified) |

## Session Example

```redis
HSET session:abc123
  user_id 42
  role "admin"
  created_at "2025-12-03T09:30:00Z"
  last_activity "2025-12-03T09:45:10Z"
  csrf_secret "random_csrf_secret_here"
  ip_address "203.0.113.10"
  user_agent_hash "f3a0d1..."
  mfa_verified "1"

EXPIRE session:abc123 1800
```

## Session Lifecycle

### 1. Session Creation (Login)

When a user logs in successfully:

1. **Generate session ID**: Random UUID
2. **Create session hash**: Set all fields in Redis
3. **Set TTL**: Default 1800 seconds (30 minutes)
4. **Set cookie**: Browser receives session cookie

```python
from flask import session
import secrets

# After successful login
session['user_id'] = user.id
session['role'] = user.role
session['created_at'] = datetime.utcnow().isoformat()
session['last_activity'] = datetime.utcnow().isoformat()
session['csrf_secret'] = secrets.token_hex(32)
session['ip_address'] = request.remote_addr
session['user_agent_hash'] = hashlib.sha256(request.user_agent.string.encode()).hexdigest()[:8]
session['mfa_verified'] = "1" if mfa_enabled else "0"
```

### 2. Session Validation (Each Request)

On every authenticated request:

1. **Check session exists**: Verify session key exists in Redis
2. **Validate user_id**: Ensure user exists in database
3. **Check role**: Verify user has required permissions
4. **Update last_activity**: Refresh activity timestamp
5. **Extend TTL**: Reset expiration to 1800 seconds

```python
from flask import session

# Middleware check
if 'user_id' not in session:
    return redirect('/login')

# Update activity
session['last_activity'] = datetime.utcnow().isoformat()
```

### 3. Session Expiration

Sessions expire automatically after 30 minutes of inactivity:

- **TTL tracking**: Redis automatically removes expired keys
- **Keyspace notifications**: Redis can notify on expiration (optional)
- **Manual cleanup**: Use `session_manager.py cleanup` for maintenance

### 4. Session Termination (Logout)

When user logs out:

1. **Delete session key**: Remove from Redis
2. **Clear cookie**: Browser cookie is invalidated

```python
from flask import session

# Logout
session.clear()
```

## Security Considerations

### CSRF Protection

The `csrf_secret` field stores a unique token for each session:

- Used to validate form submissions
- Prevents cross-site request forgery attacks
- Regenerated on each login

### IP Address Validation

The `ip_address` field enables IP-based security:

- **Strict mode**: Reject requests from different IPs
- **Logging mode**: Log suspicious IP changes
- **Disabled**: No IP validation (for dynamic IPs)

### User Agent Fingerprinting

The `user_agent_hash` helps detect session hijacking:

- Hash of browser user agent string
- Detects when session is used from different device
- Shorter hash (8 chars) for storage efficiency

### MFA Verification

The `mfa_verified` flag tracks multi-factor authentication:

- `"1"`: User completed MFA challenge
- `"0"`: MFA pending or not required
- Can require MFA for sensitive operations

## Session Management

### List All Sessions

```bash
# Using Redis CLI
podman exec redis-cache redis-cli -n 0 KEYS "session:*"

# Using session_manager.py
python redis/session_manager.py list
```

### Get Session Details

```bash
# Using Redis CLI
podman exec redis-cache redis-cli -n 0 HGETALL session:abc123

# Using session_manager.py
python redis/session_manager.py get abc123
```

### Delete Session (Force Logout)

```bash
# Using Redis CLI
podman exec redis-cache redis-cli -n 0 DEL session:abc123

# Using session_manager.py
python redis/session_manager.py delete abc123
```

### Extend Session TTL

```bash
# Using Redis CLI
podman exec redis-cache redis-cli -n 0 EXPIRE session:abc123 3600

# Using session_manager.py (extend to 1 hour)
python redis/session_manager.py extend abc123 --ttl 3600
```

### Session Statistics

```bash
# Using session_manager.py
python redis/session_manager.py stats
```

Output:
```json
{
  "total_sessions": 5,
  "active_users": 3,
  "database": 0,
  "timestamp": "2025-12-03T10:00:00Z"
}
```

## Flask-Session Configuration

Configure Flask-Session in webadmin to use Redis DB 0:

```python
from flask import Flask
from flask_session import Session
import redis

app = Flask(__name__)

# Session configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(
    host='localhost',
    port=6379,
    db=0,  # DB 0 for sessions
    decode_responses=False  # Flask-Session handles encoding
)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
app.config['SESSION_USE_SIGNER'] = True  # Sign session cookies
app.config['SESSION_KEY_PREFIX'] = 'session:'  # Key prefix

Session(app)
```

## Monitoring Sessions

### Real-time Session Monitoring

```bash
# Monitor all commands in DB 0
podman exec -it redis-cache redis-cli -n 0 MONITOR
```

### Session Expiration Events

If keyspace notifications are enabled (`notify-keyspace-events Ex`):

```bash
# Subscribe to expiration events
podman exec -it redis-cache redis-cli -n 0 PSUBSCRIBE '__keyevent@0__:expired'
```

### Memory Usage

```bash
# Check memory used by sessions
podman exec redis-cache redis-cli -n 0 INFO memory
```

## Best Practices

1. **Session TTL**: Keep sessions short (30 minutes) for security
2. **Cleanup**: Run periodic cleanup to remove orphaned sessions
3. **Monitoring**: Track active sessions and unusual patterns
4. **Security**: Validate IP and user agent on sensitive operations
5. **MFA**: Require MFA for admin accounts
6. **Rotation**: Regenerate session ID after privilege escalation
7. **Logging**: Log session creation, termination, and suspicious activity

## Troubleshooting

### Session Not Found

User keeps getting logged out:

```bash
# Check if session exists
podman exec redis-cache redis-cli -n 0 EXISTS session:abc123

# Check TTL
podman exec redis-cache redis-cli -n 0 TTL session:abc123
```

Possible causes:
- Session expired (TTL reached 0)
- Redis restarted without persistence
- Wrong database number
- Wrong session ID in cookie

### Session Not Expiring

Sessions not expiring automatically:

```bash
# Check if TTL is set
podman exec redis-cache redis-cli -n 0 TTL session:abc123

# Output -1 means no expiration set
# Output -2 means key doesn't exist
# Output > 0 means seconds until expiration
```

Fix:
```bash
# Set TTL manually
podman exec redis-cache redis-cli -n 0 EXPIRE session:abc123 1800
```

### Too Many Sessions

Redis running out of memory:

```bash
# Count sessions
podman exec redis-cache redis-cli -n 0 EVAL "return #redis.call('keys', 'session:*')" 0

# Cleanup expired
python redis/session_manager.py cleanup

# Increase maxmemory in redis.conf if needed
```

## References

- [Flask-Session Documentation](https://flask-session.readthedocs.io/)
- [Redis Hash Commands](https://redis.io/commands#hash)
- [Redis Key Expiration](https://redis.io/commands/expire)
- [Redis Keyspace Notifications](https://redis.io/docs/manual/keyspace-notifications/)
