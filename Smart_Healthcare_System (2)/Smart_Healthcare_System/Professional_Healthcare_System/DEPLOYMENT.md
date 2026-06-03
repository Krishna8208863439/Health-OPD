# 🚀 Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- 100MB free disk space

### Installation Steps

1. **Navigate to Project Directory**
```bash
cd Professional_Healthcare_System
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Create Hospital Logo**
```bash
python create_logo.py
```

4. **Run Application**
```bash
python app.py
```

5. **Access Application**
```
http://localhost:5002
```

## Production Deployment

### Option 1: Deploy with Gunicorn (Linux/Mac)

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5002 app:app
```

### Option 2: Deploy with Waitress (Windows)

1. **Install Waitress**
```bash
pip install waitress
```

2. **Create serve.py**
```python
from waitress import serve
from app import app

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5002)
```

3. **Run**
```bash
python serve.py
```

### Option 3: Deploy on Heroku

1. **Create Procfile**
```
web: gunicorn app:app
```

2. **Create runtime.txt**
```
python-3.11.0
```

3. **Deploy**
```bash
heroku create your-healthcare-app
git push heroku main
```

### Option 4: Deploy on PythonAnywhere

1. Upload all files to PythonAnywhere
2. Create virtual environment
3. Install requirements
4. Configure WSGI file
5. Reload web app

### Option 5: Deploy with Docker

1. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python create_logo.py

EXPOSE 5002

CMD ["python", "app.py"]
```

2. **Build and Run**
```bash
docker build -t healthcare-system .
docker run -p 5002:5002 healthcare-system
```

## Environment Configuration

### Production Settings

Update `app.py` for production:

```python
import os

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['DEBUG'] = False
app.config['TESTING'] = False
```

### Environment Variables

Create `.env` file:
```
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///healthcare_system.db
FLASK_ENV=production
```

## Database Setup

### SQLite (Default)
- Automatically created on first run
- File: `healthcare_system.db`
- No additional setup required

### PostgreSQL (Production)

1. **Install psycopg2**
```bash
pip install psycopg2-binary
```

2. **Update Database Connection**
```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///healthcare_system.db')
engine = create_engine(DATABASE_URL)
```

## Security Checklist

- [ ] Change SECRET_KEY to random string
- [ ] Set DEBUG = False in production
- [ ] Use HTTPS in production
- [ ] Enable CSRF protection
- [ ] Set secure session cookies
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Enable SQL injection protection
- [ ] Use environment variables for secrets
- [ ] Regular security updates

## Performance Optimization

### 1. Enable Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

### 2. Compress Responses
```python
from flask_compress import Compress

Compress(app)
```

### 3. Use CDN for Static Files
- Host CSS/JS on CDN
- Use CDN for Bootstrap and Chart.js

### 4. Database Optimization
- Add indexes to frequently queried columns
- Use connection pooling
- Implement query caching

## Monitoring

### Application Monitoring

1. **Add Logging**
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

2. **Error Tracking**
- Use Sentry for error tracking
- Monitor application performance
- Track user analytics

### Health Check Endpoint

Add to `app.py`:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

## Backup Strategy

### Database Backup

1. **Automated Backup Script**
```python
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy('healthcare_system.db', f'backups/db_backup_{timestamp}.db')
```

2. **Schedule Backups**
- Daily database backups
- Weekly full system backups
- Store backups off-site

### PDF Reports Backup
- Regular backup of `static/reports/` folder
- Archive old reports monthly
- Cloud storage integration

## Scaling

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Multiple application instances
- Shared database server
- Centralized file storage

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Enable caching
- Use async processing

## Maintenance

### Regular Tasks
- [ ] Update dependencies monthly
- [ ] Review security patches
- [ ] Monitor disk space
- [ ] Check error logs
- [ ] Backup database
- [ ] Test disaster recovery
- [ ] Update documentation

### Update Process
1. Test updates in staging environment
2. Backup production database
3. Deploy updates during low-traffic period
4. Monitor for errors
5. Rollback if issues occur

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port
netstat -ano | findstr :5002
# Kill process
taskkill /PID <process_id> /F
```

**Database Locked**
- Close all connections
- Restart application
- Check file permissions

**PDF Generation Fails**
- Verify Pillow installation
- Check logo file exists
- Ensure write permissions on static/reports/

**Charts Not Displaying**
- Check Chart.js CDN link
- Verify JavaScript console for errors
- Ensure data endpoint returns valid JSON

## Support

### Getting Help
- Check documentation files
- Review error logs
- Test in development mode
- Check GitHub issues

### Reporting Issues
Include:
- Python version
- Operating system
- Error messages
- Steps to reproduce

## Checklist for Production

- [ ] All dependencies installed
- [ ] Hospital logo created
- [ ] Database initialized
- [ ] Secret key changed
- [ ] Debug mode disabled
- [ ] HTTPS enabled
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Error tracking enabled
- [ ] Performance optimized
- [ ] Security hardened
- [ ] Documentation updated

---

**Ready for Production! 🎉**

For questions or support, refer to README.md and other documentation files.
