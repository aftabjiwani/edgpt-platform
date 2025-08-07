# SSL/HTTPS Troubleshooting Guide

## 🔍 **Common SSL/HTTPS Issues and Solutions**

This guide documents the SSL/HTTPS issues encountered in the EdGPT Platform and their solutions, based on real production troubleshooting experience.

## 🚨 **Issue: 502 Bad Gateway Errors**

### **Symptoms**
- All domains returning 502 Bad Gateway errors
- HTTPS pages not loading
- Nginx error logs showing connection failures

### **Root Cause Analysis**

#### **Initial Suspicion: SSL Certificate Issues**
- ❌ **Assumption**: SSL certificates were expired or invalid
- ❌ **Assumption**: Certificate coverage was incomplete
- ❌ **Assumption**: Let's Encrypt renewal failed

#### **Actual Root Cause: Nginx Proxy Port Mismatch**
- ✅ **Reality**: Nginx was configured to proxy to port 8094
- ✅ **Reality**: Flask app was running on port 8082
- ✅ **Reality**: SSL certificates were valid and working correctly

### **Diagnostic Steps**

#### **1. Check SSL Certificate Status**
```bash
# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/edgpt.ai/fullchain.pem -text -noout | grep -A 2 "Validity"

# Check Subject Alternative Names (SAN)
openssl x509 -in /etc/letsencrypt/live/edgpt.ai/fullchain.pem -text -noout | grep -A 10 "Subject Alternative Name"
```

**Expected Output**:
```
Validity
    Not Before: Aug  4 08:04:59 2025 GMT
    Not After : Nov  2 08:04:58 2025 GMT

X509v3 Subject Alternative Name: 
    DNS:businessbrokergpt.ai, DNS:cpafirm.ai, DNS:edgpt.ai, DNS:gptsites.ai, DNS:lawfirmgpt.ai, DNS:www.businessbrokergpt.ai, DNS:www.cpafirm.ai, DNS:www.edgpt.ai, DNS:www.gptsites.ai, DNS:www.lawfirmgpt.ai
```

#### **2. Check Nginx Error Logs**
```bash
tail -20 /var/log/nginx/error.log
```

**Key Error Pattern**:
```
[error] connect() failed (111: Unknown error) while connecting to upstream, 
client: X.X.X.X, server: edgpt.ai, request: "GET /signup HTTP/2.0", 
upstream: "http://127.0.0.1:8094/signup", host: "gptsites.ai"
```

#### **3. Identify Port Mismatch**
```bash
# Check what nginx is configured to proxy to
grep -r "proxy_pass" /etc/nginx/sites-enabled/

# Check what port Flask app is actually running on
ps aux | grep python | grep app.py
netstat -tlnp | grep python
```

### **Solution Steps**

#### **1. Fix Nginx Configuration**
```bash
# Find all references to wrong port
grep -r "8094" /etc/nginx/

# Replace with correct port
sed -i 's/8094/8082/g' /etc/nginx/sites-enabled/edgpt-domains

# Verify changes
grep -r "8082" /etc/nginx/sites-enabled/edgpt-domains
```

#### **2. Test and Reload Nginx**
```bash
# Test configuration
nginx -t

# Reload if test passes
nginx -s reload
systemctl reload nginx
```

#### **3. Verify Flask App Port**
```bash
# Check Flask app is running on correct port
ps aux | grep python | grep app.py
ss -tlnp | grep 8082

# If needed, restart Flask app on correct port
cd /var/www/edgpt
kill <flask-pid>
python3 app.py &
```

#### **4. Test Resolution**
```bash
# Test local connection
curl -I http://localhost:8082/health

# Test through nginx proxy
curl -I https://edgpt.ai/health
```

## 🔧 **Prevention Strategies**

### **1. Configuration Management**
- **Document port assignments** in deployment guides
- **Use environment variables** for port configuration
- **Maintain configuration templates** with correct values

### **2. Monitoring and Alerting**
- **Health check endpoints** for application monitoring
- **Nginx log monitoring** for proxy errors
- **SSL certificate expiration alerts**

### **3. Deployment Checklist**
```bash
# Pre-deployment verification
□ Check Flask app port configuration
□ Verify nginx proxy_pass settings match
□ Test SSL certificate validity
□ Confirm all domains in certificate SAN
□ Test health endpoints
□ Verify database connectivity
```

## 📊 **SSL Certificate Management**

### **Certificate Coverage Verification**
```bash
# Check all domains covered by certificate
openssl x509 -in /etc/letsencrypt/live/edgpt.ai/fullchain.pem -text -noout | grep -A 20 "Subject Alternative Name"
```

### **Multi-Domain Certificate Setup**
```bash
# Example certbot command for multi-domain certificate
certbot certonly --nginx \
  -d edgpt.ai -d www.edgpt.ai \
  -d gptsites.ai -d www.gptsites.ai \
  -d lawfirmgpt.ai -d www.lawfirmgpt.ai \
  -d cpafirm.ai -d www.cpafirm.ai \
  -d businessbrokergpt.ai -d www.businessbrokergpt.ai
```

### **Certificate Renewal**
```bash
# Test renewal
certbot renew --dry-run

# Force renewal if needed
certbot renew --force-renewal
```

## 🔍 **Debugging Tools**

### **SSL Testing Tools**
```bash
# Test SSL configuration
openssl s_client -connect edgpt.ai:443 -servername edgpt.ai

# Check SSL grade
curl -s "https://api.ssllabs.com/api/v3/analyze?host=edgpt.ai"
```

### **Network Connectivity**
```bash
# Test port connectivity
telnet localhost 8082
nc -zv localhost 8082

# Check listening ports
ss -tlnp | grep :8082
netstat -tlnp | grep :8082
```

### **Application Health**
```bash
# Test Flask app directly
curl http://localhost:8082/health

# Test through nginx proxy
curl https://edgpt.ai/health

# Check response headers
curl -I https://edgpt.ai/
```

## 📋 **Common Error Patterns**

### **502 Bad Gateway**
- **Cause**: Upstream server (Flask) not reachable
- **Check**: Port mismatch, app not running, firewall blocking
- **Solution**: Fix nginx proxy_pass configuration

### **SSL Certificate Errors**
- **Cause**: Certificate expired, wrong domain, missing SAN
- **Check**: Certificate validity, domain coverage
- **Solution**: Renew certificate, update SAN list

### **Connection Timeouts**
- **Cause**: Flask app overloaded, database locks
- **Check**: Application logs, database performance
- **Solution**: Optimize queries, increase timeouts

### **Mixed Content Warnings**
- **Cause**: HTTP resources loaded on HTTPS pages
- **Check**: Template URLs, asset references
- **Solution**: Update all URLs to HTTPS

## 🎯 **Best Practices**

### **Configuration**
- **Use consistent port numbers** across environments
- **Document all port assignments** in deployment guides
- **Use configuration files** instead of hardcoded values
- **Version control nginx configurations**

### **Monitoring**
- **Implement health checks** for all services
- **Monitor SSL certificate expiration**
- **Set up log aggregation** for error tracking
- **Use uptime monitoring** for early detection

### **Security**
- **Enable HSTS headers** for enhanced security
- **Use strong SSL ciphers** and protocols
- **Implement certificate pinning** where appropriate
- **Regular security audits** of SSL configuration

## 🚀 **Production Deployment**

### **Pre-Deployment Checklist**
```bash
# 1. Verify SSL certificates
openssl x509 -in /path/to/cert.pem -text -noout | grep -A 2 "Validity"

# 2. Test nginx configuration
nginx -t

# 3. Check Flask app configuration
grep -n "port=" backend/app.py

# 4. Verify proxy_pass settings
grep -n "proxy_pass" /etc/nginx/sites-enabled/*

# 5. Test health endpoints
curl http://localhost:8082/health
```

### **Post-Deployment Verification**
```bash
# 1. Test all domains
for domain in edgpt.ai gptsites.ai lawfirmgpt.ai cpafirm.ai taxprepgpt.ai businessbrokergpt.ai; do
  echo "Testing $domain..."
  curl -I https://$domain/health
done

# 2. Verify SSL grades
for domain in edgpt.ai gptsites.ai lawfirmgpt.ai cpafirm.ai taxprepgpt.ai businessbrokergpt.ai; do
  echo "SSL test for $domain..."
  openssl s_client -connect $domain:443 -servername $domain < /dev/null
done

# 3. Check nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 📞 **Emergency Response**

### **If 502 Errors Occur**
1. **Check Flask app status**: `ps aux | grep python`
2. **Verify port configuration**: `grep proxy_pass /etc/nginx/sites-enabled/*`
3. **Test local connectivity**: `curl http://localhost:8082/health`
4. **Check nginx logs**: `tail -20 /var/log/nginx/error.log`
5. **Restart services if needed**: `systemctl restart nginx`

### **If SSL Errors Occur**
1. **Check certificate validity**: `openssl x509 -in /path/to/cert.pem -text -noout`
2. **Verify domain coverage**: Check Subject Alternative Names
3. **Test certificate chain**: `openssl verify -CAfile /path/to/chain.pem /path/to/cert.pem`
4. **Renew if expired**: `certbot renew`

This troubleshooting guide is based on real production experience and should help prevent and resolve similar SSL/HTTPS issues in the future.

