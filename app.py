import os
import random
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models import db, TempEmail, EmailMessage

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tempmail.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.secret_key = os.environ.get('SECRET_KEY', 'tempmail-secret-key-2024')

db.init_app(app)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
]

def get_headers():
    return {
        "Host": "api.internal.temp-mail.io",
        "Connection": "keep-alive",
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Application-Version": "2.2.14",
        "Application-Name": "web",
        "Origin": "https://temp-mail.io",
        "Referer": "https://temp-mail.io/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/domains', methods=['GET'])
def get_domains():
    try:
        response = requests.get(
            "https://api.internal.temp-mail.io/api/v3/domains",
            headers=get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            domains = [d['name'] for d in data.get('domains', [])]
            return jsonify({'success': True, 'domains': domains})
        return jsonify({'success': False, 'error': 'Failed to fetch domains'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/email/create/random', methods=['POST'])
def create_random_email():
    try:
        random_length = random.randint(10, 15)
        payload = {
            "min_name_length": random_length,
            "max_name_length": random_length
        }
        
        response = requests.post(
            "https://api.internal.temp-mail.io/api/v3/email/new",
            json=payload,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            email_address = data.get('email')
            token = data.get('token')
            
            existing = TempEmail.query.filter_by(email=email_address).first()
            if existing:
                existing.token = token
                existing.is_active = True
                db.session.commit()
                return jsonify({'success': True, 'email': existing.to_dict()})
            
            new_email = TempEmail(
                email=email_address,
                token=token,
                digit=str(random_length)
            )
            db.session.add(new_email)
            db.session.commit()
            
            return jsonify({'success': True, 'email': new_email.to_dict()})
        return jsonify({'success': False, 'error': 'Failed to create email'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/email/create/custom', methods=['POST'])
def create_custom_email():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        domain = data.get('domain', '').strip()
        
        if not name or not domain:
            return jsonify({'success': False, 'error': 'Name and domain are required'})
        
        payload = {
            "name": name,
            "domain": domain
        }
        
        response = requests.post(
            "https://api.internal.temp-mail.io/api/v3/email/new",
            json=payload,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            email_address = result.get('email')
            token = result.get('token')
            
            existing = TempEmail.query.filter_by(email=email_address).first()
            if existing:
                existing.token = token
                existing.is_active = True
                db.session.commit()
                return jsonify({'success': True, 'email': existing.to_dict()})
            
            new_email = TempEmail(
                email=email_address,
                token=token,
                digit=str(len(name))
            )
            db.session.add(new_email)
            db.session.commit()
            
            return jsonify({'success': True, 'email': new_email.to_dict()})
        return jsonify({'success': False, 'error': 'Failed to create email'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/email/<int:email_id>/inbox', methods=['GET'])
def check_inbox(email_id):
    try:
        email_account = TempEmail.query.get(email_id)
        if not email_account:
            return jsonify({'success': False, 'error': 'Email not found'})
        
        response = requests.get(
            f"https://api.internal.temp-mail.io/api/v3/email/{email_account.email}/messages",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            messages = response.json()
            
            for msg in messages:
                existing = EmailMessage.query.filter_by(message_id=msg.get('id')).first()
                if not existing:
                    received_at = None
                    if msg.get('created_at'):
                        try:
                            received_at = datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00'))
                        except:
                            received_at = datetime.utcnow()
                    
                    new_msg = EmailMessage(
                        message_id=msg.get('id'),
                        email_id=email_account.id,
                        from_email=msg.get('from', ''),
                        to_email=msg.get('to', email_account.email),
                        subject=msg.get('subject', '(No Subject)'),
                        body_text=msg.get('body_text', ''),
                        body_html=msg.get('body_html', ''),
                        cc=str(msg.get('cc', '')),
                        attachments=msg.get('attachments', []),
                        received_at=received_at
                    )
                    db.session.add(new_msg)
            
            db.session.commit()
            
            db_messages = EmailMessage.query.filter_by(email_id=email_id).order_by(EmailMessage.received_at.desc()).all()
            return jsonify({
                'success': True,
                'email': email_account.email,
                'messages': [m.to_dict() for m in db_messages]
            })
        elif response.status_code == 400:
            email_account.is_active = False
            db.session.commit()
            return jsonify({'success': False, 'error': 'Email expired'})
        return jsonify({'success': False, 'error': 'Failed to fetch inbox'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/emails', methods=['GET'])
def get_all_emails():
    try:
        emails = TempEmail.query.order_by(TempEmail.created_at.desc()).all()
        return jsonify({
            'success': True,
            'emails': [e.to_dict() for e in emails]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/email/<int:email_id>', methods=['GET'])
def get_email(email_id):
    try:
        email = TempEmail.query.get(email_id)
        if not email:
            return jsonify({'success': False, 'error': 'Email not found'})
        return jsonify({'success': True, 'email': email.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/email/<int:email_id>', methods=['DELETE'])
def delete_email(email_id):
    try:
        email = TempEmail.query.get(email_id)
        if not email:
            return jsonify({'success': False, 'error': 'Email not found'})
        
        db.session.delete(email)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Email deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/email/<int:email_id>/activate', methods=['POST'])
def activate_email(email_id):
    try:
        email_account = TempEmail.query.get(email_id)
        if not email_account:
            return jsonify({'success': False, 'error': 'Email not found'})
        
        name = email_account.email.split('@')[0]
        domain = email_account.email.split('@')[1]
        
        payload = {
            "name": name,
            "token": email_account.token,
            "domain": domain
        }
        
        response = requests.post(
            "https://api.internal.temp-mail.io/api/v3/email/new",
            json=payload,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            email_account.token = result.get('token', email_account.token)
            email_account.is_active = True
            db.session.commit()
            return jsonify({'success': True, 'email': email_account.to_dict()})
        return jsonify({'success': False, 'error': 'Failed to reactivate email'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/message/<int:message_id>', methods=['GET'])
def get_message(message_id):
    try:
        message = EmailMessage.query.get(message_id)
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'})
        return jsonify({'success': True, 'message': message.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
