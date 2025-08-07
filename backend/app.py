"""
EdGPT Platform - Multi-Domain AI Website Conversion Platform
Main Flask Application with Domain Routing and Logo Support

Features:
- Domain-specific template routing for 6 business verticals
- User authentication and admin dashboard
- Trial signup and conversion process
- Code generator for widget integration
- Mobile-responsive design with proper logos
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)

# Database setup
DATABASE = 'edgpt_platform.db'

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            website_url TEXT,
            business_name TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Trial requests table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS trial_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            website_url TEXT NOT NULL,
            business_name TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Analytics table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            page_path TEXT NOT NULL,
            user_agent TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin user if it doesn't exist
    admin_email = 'admin@edgpt.ai'
    admin_password = 'admin123'
    admin_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    
    try:
        conn.execute('''
            INSERT OR IGNORE INTO users (email, password_hash, is_admin, business_name)
            VALUES (?, ?, ?, ?)
        ''', (admin_email, admin_hash, True, 'EdGPT Admin'))
        conn.commit()
    except Exception as e:
        print(f"Admin user creation error: {e}")
    
    conn.close()

# Initialize database
init_db()

# Domain-specific template mapping
DOMAIN_TEMPLATES = {
    'edgpt.ai': 'enhanced_landing_with_slideshow.html',
    'gptsites.ai': 'gptsites_landing.html', 
    'lawfirmgpt.ai': 'lawfirmgpt_landing.html',
    'cpafirm.ai': 'cpafirm_landing.html',
    'taxprepgpt.ai': 'taxprepgpt_landing.html',
    'businessbrokergpt.ai': 'businessbrokergpt_landing.html'
}

# Domain-specific configurations
DOMAIN_CONFIGS = {
    'edgpt.ai': {
        'name': 'EdGPT',
        'industry': 'Education',
        'color': '#3B82F6',
        'icon': '🎓',
        'title': 'Transform Your School Website Into an Intelligent EdGPT',
        'description': 'Convert your school website into an AI assistant that provides instant answers to parents, students, and staff 24/7.'
    },
    'gptsites.ai': {
        'name': 'GPTSites',
        'industry': 'Business',
        'color': '#3B82F6',
        'icon': '💼',
        'title': 'Transform Your Business Website Into an Intelligent GPTsite',
        'description': 'Convert your business website into an AI assistant that provides instant answers to customers 24/7.'
    },
    'lawfirmgpt.ai': {
        'name': 'LawFirmGPT',
        'industry': 'Legal',
        'color': '#1E40AF',
        'icon': '⚖️',
        'title': 'Transform Your Law Firm Website Into an Intelligent GPTsite',
        'description': 'Convert your law firm website into an AI assistant that provides instant answers to clients 24/7.'
    },
    'cpafirm.ai': {
        'name': 'CPAFirm',
        'industry': 'Accounting',
        'color': '#059669',
        'icon': '🧮',
        'title': 'Transform Your Accounting Firm Website Into an Intelligent GPTsite',
        'description': 'Convert your accounting firm website into an AI assistant that provides instant answers to clients 24/7.'
    },
    'taxprepgpt.ai': {
        'name': 'TaxPrepGPT',
        'industry': 'Tax Preparation',
        'color': '#059669',
        'icon': '💰',
        'title': 'Transform Your Tax Preparation Website Into an Intelligent GPTsite',
        'description': 'Convert your tax preparation website into an AI assistant that provides instant answers to taxpayers 24/7.'
    },
    'businessbrokergpt.ai': {
        'name': 'BusinessBrokerGPT',
        'industry': 'Business Brokerage',
        'color': '#7C3AED',
        'icon': '🏢',
        'title': 'Transform Your Business Brokerage Website Into an Intelligent GPTsite',
        'description': 'Convert your business brokerage website into an AI assistant that provides instant answers to buyers and sellers 24/7.'
    }
}

def get_template_for_domain(host):
    """Get the appropriate template based on the request domain"""
    # Remove port if present
    domain = host.split(':')[0]
    
    # Check for exact domain match
    if domain in DOMAIN_TEMPLATES:
        return DOMAIN_TEMPLATES[domain]
    
    # Check for subdomain matches (e.g., www.edgpt.ai)
    for registered_domain in DOMAIN_TEMPLATES:
        if domain.endswith(registered_domain):
            return DOMAIN_TEMPLATES[registered_domain]
    
    # Default to EdGPT template
    return DOMAIN_TEMPLATES['edgpt.ai']

def get_domain_config(host):
    """Get domain-specific configuration"""
    domain = host.split(':')[0]
    
    # Check for exact domain match
    if domain in DOMAIN_CONFIGS:
        return DOMAIN_CONFIGS[domain]
    
    # Check for subdomain matches
    for registered_domain in DOMAIN_CONFIGS:
        if domain.endswith(registered_domain):
            return DOMAIN_CONFIGS[registered_domain]
    
    # Default to EdGPT config
    return DOMAIN_CONFIGS['edgpt.ai']

def log_analytics(domain, page_path):
    """Log page view analytics"""
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO analytics (domain, page_path, user_agent, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (domain, page_path, request.headers.get('User-Agent', ''), 
              request.remote_addr))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Analytics logging error: {e}")

@app.route('/')
def home():
    """Main landing page with domain-specific templates and logos"""
    try:
        # Get the appropriate template based on the request domain
        template_name = get_template_for_domain(request.host)
        domain_config = get_domain_config(request.host)
        
        # Log analytics
        log_analytics(request.host, '/')
        
        print(f"🌐 Domain: {request.host} → Template: {template_name}")
        return render_template(template_name, domain_config=domain_config)
    except Exception as e:
        # Fallback to EdGPT template if there's an error
        print(f"Template error for {request.host}: {str(e)}")
        return render_template('enhanced_landing_with_slideshow.html', 
                             domain_config=DOMAIN_CONFIGS['edgpt.ai'])

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "domains": list(DOMAIN_TEMPLATES.keys())
    })

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Trial signup page and form processing"""
    if request.method == 'GET':
        try:
            domain_config = get_domain_config(request.host)
            log_analytics(request.host, '/signup')
            return render_template('fixed_signup_template.html', domain_config=domain_config)
        except Exception as e:
            return f"Template error: {str(e)}", 500
    
    elif request.method == 'POST':
        try:
            # Get form data
            email = request.form.get('email', '').strip()
            website_url = request.form.get('website_url', '').strip()
            business_name = request.form.get('business_name', '').strip()
            phone = request.form.get('phone', '').strip()
            
            # Basic validation
            if not email or not website_url:
                error_msg = "Email and website URL are required"
                if request.is_json:
                    return jsonify({"error": error_msg}), 400
                else:
                    return f"Error: {error_msg}", 400
            
            # Store trial request
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO trial_requests (email, website_url, business_name, phone)
                VALUES (?, ?, ?, ?)
            ''', (email, website_url, business_name, phone))
            conn.commit()
            conn.close()
            
            # Redirect to conversion process
            return redirect(url_for('conversion_process'))
            
        except Exception as e:
            print(f"Signup error: {str(e)}")
            if request.is_json:
                return jsonify({"error": f"Signup failed: {str(e)}"}), 500
            else:
                return f"Signup failed: {str(e)}", 500

@app.route('/conversion')
def conversion_process():
    """Website conversion process page"""
    try:
        domain_config = get_domain_config(request.host)
        log_analytics(request.host, '/conversion')
        return render_template('conversion_process_fixed.html', domain_config=domain_config)
    except Exception as e:
        return f"Template error: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and authentication"""
    if request.method == 'GET':
        try:
            domain_config = get_domain_config(request.host)
            log_analytics(request.host, '/login')
            return render_template('enhanced_login.html', domain_config=domain_config)
        except Exception as e:
            return f"Template error: {str(e)}", 500
    
    elif request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username or not password:
                return jsonify({"error": "Username and password are required"}), 400
            
            # Hash the password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Check credentials
            conn = get_db_connection()
            user = conn.execute('''
                SELECT * FROM users WHERE email = ? AND password_hash = ?
            ''', (username, password_hash)).fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['is_admin'] = user['is_admin']
                
                if user['is_admin']:
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                return jsonify({"error": "Invalid credentials"}), 401
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        domain_config = get_domain_config(request.host)
        log_analytics(request.host, '/dashboard')
        return render_template('enhanced_dashboard_with_email_settings.html', 
                             domain_config=domain_config)
    except Exception as e:
        return f"Template error: {str(e)}", 500

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with code generator and analytics"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    try:
        domain_config = get_domain_config(request.host)
        log_analytics(request.host, '/admin/dashboard')
        
        # Get analytics data
        conn = get_db_connection()
        analytics = conn.execute('''
            SELECT domain, COUNT(*) as views, DATE(created_at) as date
            FROM analytics 
            GROUP BY domain, DATE(created_at)
            ORDER BY date DESC, views DESC
            LIMIT 50
        ''').fetchall()
        
        trial_requests = conn.execute('''
            SELECT * FROM trial_requests 
            ORDER BY created_at DESC 
            LIMIT 20
        ''').fetchall()
        
        conn.close()
        
        return render_template('admin_dashboard.html', 
                             domain_config=domain_config,
                             analytics=analytics,
                             trial_requests=trial_requests)
    except Exception as e:
        return f"Template error: {str(e)}", 500

@app.route('/api/generate-code', methods=['POST'])
def generate_integration_code():
    """Generate custom integration code for domains"""
    try:
        data = request.get_json()
        domain = data.get('domain', 'edgpt.ai')
        customization = data.get('customization', {})
        
        # Get domain configuration
        config = DOMAIN_CONFIGS.get(domain, DOMAIN_CONFIGS['edgpt.ai'])
        
        # Apply customizations
        widget_color = customization.get('color', config['color'])
        widget_position = customization.get('position', 'bottom-right')
        widget_size = customization.get('size', 'medium')
        
        # Generate the integration code using string formatting instead of f-strings
        html_code = '''<!-- {name} Chat Widget -->
<div id="{name_lower}-chat-widget"></div>
<script>
(function() {{
    // Widget configuration
    const config = {{
        domain: '{domain}',
        name: '{name}',
        color: '{color}',
        position: '{position}',
        size: '{size}',
        poweredBy: '{name}'
    }};
    
    // Create widget container
    const widget = document.createElement('div');
    widget.id = 'gptsite-widget';
    widget.style.cssText = `
        position: fixed;
        {pos_right}: 20px;
        {pos_top}: 20px;
        width: {width};
        height: 500px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        z-index: 10000;
        display: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    // Create chat interface
    widget.innerHTML = `
        <div style="background: {color}; color: white; padding: 15px; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 20px;">{icon}</span>
                <span style="font-weight: 600;">{name} Assistant</span>
            </div>
            <button onclick="toggleWidget()" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer;">×</button>
        </div>
        <div style="padding: 20px; height: 380px; overflow-y: auto;">
            <div style="background: #f3f4f6; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                Hi! I'm your {industry_lower} assistant. I can help you with information about our services. What would you like to know?
            </div>
        </div>
        <div style="padding: 15px; border-top: 1px solid #e5e7eb;">
            <div style="display: flex; gap: 8px;">
                <input type="text" placeholder="Type your message..." style="flex: 1; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; outline: none;">
                <button style="background: {color}; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer;">Send</button>
            </div>
            <div style="text-align: center; margin-top: 8px; font-size: 12px; color: #6b7280;">
                Powered by <a href="https://{domain}" target="_blank" style="color: {color}; text-decoration: none;">{name}</a>
            </div>
        </div>
    `;
    
    // Create toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'gptsite-toggle';
    toggleBtn.style.cssText = `
        position: fixed;
        {pos_right}: 20px;
        {pos_top}: 20px;
        width: 60px;
        height: 60px;
        background: {color};
        border: none;
        border-radius: 50%;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        z-index: 10001;
        transition: transform 0.2s;
    `;
    toggleBtn.innerHTML = '{icon}';
    toggleBtn.onclick = function() {{ toggleWidget(); }};
    
    // Toggle function
    window.toggleWidget = function() {{
        const isVisible = widget.style.display !== 'none';
        widget.style.display = isVisible ? 'none' : 'block';
        toggleBtn.style.transform = isVisible ? 'scale(1)' : 'scale(0.9)';
    }};
    
    // Append to page
    document.body.appendChild(widget);
    document.body.appendChild(toggleBtn);
    
    console.log('{name} widget loaded successfully');
}})();
</script>'''.format(
            name=config['name'],
            name_lower=config['name'].lower(),
            domain=domain,
            color=widget_color,
            position=widget_position,
            size=widget_size,
            pos_right=widget_position.split('-')[1],
            pos_top=widget_position.split('-')[0],
            width={'small': '300px', 'medium': '350px', 'large': '400px'}[widget_size],
            icon=config['icon'],
            industry_lower=config['industry'].lower()
        )
        
        css_code = '''/* {name} Widget Styles */
#{name_lower}-chat-widget {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

.gptsite-widget-container {{
    position: fixed;
    {pos_right}: 20px;
    {pos_top}: 20px;
    z-index: 10000;
}}

.gptsite-widget-toggle {{
    background: {color};
    border: none;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    color: white;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    transition: transform 0.2s;
}}

.gptsite-widget-toggle:hover {{
    transform: scale(1.05);
}}'''.format(
            name=config['name'],
            name_lower=config['name'].lower(),
            color=widget_color,
            pos_right=widget_position.split('-')[1],
            pos_top=widget_position.split('-')[0]
        )
        
        return jsonify({
            'success': True,
            'html': html_code,
            'css': css_code,
            'config': config,
            'customization': customization
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def get_analytics():
    """Get analytics data for admin dashboard"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        
        # Domain views
        domain_views = conn.execute('''
            SELECT domain, COUNT(*) as views
            FROM analytics 
            WHERE created_at >= date('now', '-30 days')
            GROUP BY domain
            ORDER BY views DESC
        ''').fetchall()
        
        # Daily views
        daily_views = conn.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as views
            FROM analytics 
            WHERE created_at >= date('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''').fetchall()
        
        # Trial signups
        trial_signups = conn.execute('''
            SELECT COUNT(*) as count
            FROM trial_requests 
            WHERE created_at >= date('now', '-30 days')
        ''').fetchone()
        
        conn.close()
        
        return jsonify({
            'domain_views': [dict(row) for row in domain_views],
            'daily_views': [dict(row) for row in daily_views],
            'trial_signups': trial_signups['count']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(error):
    """Custom 404 page"""
    domain_config = get_domain_config(request.host)
    return render_template('404.html', domain_config=domain_config), 404

@app.errorhandler(500)
def server_error(error):
    """Custom 500 page"""
    domain_config = get_domain_config(request.host)
    return render_template('500.html', domain_config=domain_config), 500

if __name__ == '__main__':
    print("🚀 Starting EdGPT Platform with Domain Routing...")
    print("📍 Landing page: http://localhost:8082")
    print("📍 Signup page: http://localhost:8082/signup") 
    print("📍 Health check: http://localhost:8082/health")
    print("🌐 Domain routing enabled for all 6 domains:")
    for domain, template in DOMAIN_TEMPLATES.items():
        print(f"   • {domain} → {template}")
    
    app.run(host='0.0.0.0', port=8082, debug=False)

