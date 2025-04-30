from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Project, VerificationStatus
from utils import is_valid_email, send_verification_email, serializer, send_custom_email
from datetime import datetime, timedelta
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Blueprint('api', __name__)

# O limiter deve ser inicializado após a definição do Blueprint
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'api_key' not in data:
        return jsonify({'error': 'Email e api_key são obrigatórios'}), 400

    email = data['email']
    api_key = data['api_key']
    
    if not is_valid_email(email):
        return jsonify({'error': 'Email inválido'}), 400

    project = Project.query.filter_by(api_key=api_key).first()
    if not project:
        return jsonify({'error': 'Projeto não encontrado'}), 404

    user = User.query.filter_by(email=email).first()
    
    if user:
        verification = VerificationStatus.query.filter_by(
            user_id=user.id,
            project_id=project.id
        ).first()
        if verification and verification.verified:
            return jsonify({'message': 'Este email já está verificado para este projeto'}), 400

    if not user:
        user = User(email=email)
        user.projects.append(project)
        db.session.add(user)
    elif project not in user.projects:
        user.projects.append(project)

    verification = VerificationStatus.query.filter_by(
        user_id=user.id, 
        project_id=project.id
    ).first()

    if not verification:
        verification = VerificationStatus(user_id=user.id, project_id=project.id)
        db.session.add(verification)

    try:
        db.session.commit()
        token_data = {'email': email, 'api_key': api_key}
        token = serializer.dumps(token_data, salt='email-verification')
        
        try:
            send_verification_email(email, project.name, token, request.host_url, project=project)
        except Exception as mail_error:
            print(f"Erro ao enviar email: {str(mail_error)}")
            return jsonify({'error': f'Erro ao enviar email: {str(mail_error)}'}), 500
        
        return jsonify({
            'message': 'Registro realizado com sucesso. Verifique seu email.',
            'user': {
                'id': user.id,
                'email': user.email,
                'project': project.name,
                'verified': verification.verified
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar usuário: {str(e)}")
        return jsonify({'error': f'Erro ao registrar usuário: {str(e)}'}), 500

@app.route('/verify/<token>')
def verify_email(token):
    try:
        token_data = serializer.loads(token, salt='email-verification', max_age=3600)
        email = token_data['email']
        api_key = token_data['api_key']

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        project = Project.query.filter_by(api_key=api_key).first()
        if not project:
            return jsonify({'error': 'Projeto não encontrado'}), 404

        verification = VerificationStatus.query.filter_by(
            user_id=user.id,
            project_id=project.id
        ).first()

        if not verification:
            return jsonify({'error': 'Verificação não encontrada'}), 404

        if verification.verified:
            return jsonify({'message': 'Email já está verificado para este projeto'}), 200

        verification.verified = True
        verification.verified_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Email verificado com sucesso',
            'project': verification.project.name
        }), 200

    except Exception as e:
        return jsonify({'error': 'Token inválido ou expirado'}), 400

@app.route('/check-verification', methods=['POST'])
@jwt_required()
def check_verification():
    email = request.args.get('email')
    api_key = request.args.get('api_key')
    
    if not email or not api_key:
        return jsonify({'error': 'Email e api_key são obrigatórios'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'verified': False, 'message': 'Email não encontrado'}), 404
        
    project = Project.query.filter_by(api_key=api_key).first()
    if not project:
        return jsonify({'verified': False, 'message': 'Projeto não encontrado'}), 404

    verification = VerificationStatus.query.filter_by(
        user_id=user.id,
        project_id=project.id
    ).first()
    
    if not verification:
        return jsonify({'verified': False, 'message': 'Verificação não encontrada'}), 404
        
    return jsonify({
        'verified': verification.verified,
        'verified_at': verification.verified_at.isoformat() if verification.verified_at else None
    })

@app.route('/users')
@jwt_required()
def list_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'verified': user.verified,
        'created_at': user.created_at.isoformat()
    } for user in users])

@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Nome do projeto é obrigatório'}), 400
        
    name = data['name']
    description = data.get('description', '')
    mail_username = data.get('mail_username')
    mail_password = data.get('mail_password').replace(' ', '')

    project = Project(
        name=name,
        description=description,
        mail_username=mail_username,
        mail_password=mail_password
    )
    
    try:
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Projeto criado com sucesso',
            'project': {
                'id': project.id,
                'api_key': project.api_key,
                'name': project.name,
                'description': project.description,
                'mail_username': project.mail_username
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'api_key' not in data:
        return jsonify({'error': 'API key do projeto é obrigatória'}), 400

    api_key = data['api_key']
    project = Project.query.filter_by(api_key=api_key).first()
    
    if not project:
        return jsonify({'error': 'Projeto não encontrado'}), 404

    try:
        # Gera o token com o ID do projeto
        access_token = create_access_token(
            identity=str(project.id),
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'project': {
                'id': project.id,
                'api_key': project.api_key,
                'name': project.name,
                'description': project.description
            },
            'access_token': access_token
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if not admin_email or not admin_password:
        return jsonify({'error': 'Credenciais de administrador não configuradas'}), 500
    
    if data['email'] != admin_email or data['password'] != admin_password:
        return jsonify({'error': 'Credenciais inválidas'}), 401
    
    access_token = create_access_token(identity=admin_email)
    return jsonify({'access_token': access_token}), 200

@app.route('/projects', methods=['GET'])
@jwt_required()
def list_projects():
    projects = Project.query.all()
    return jsonify({
        'projects': [{
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'api_key': project.api_key,
            'mail_username': project.mail_username,
            'created_at': project.created_at.isoformat()
        } for project in projects]
    }), 200

@app.route('/send-custom-email', methods=['POST'])
def send_custom_email_route():
    data = request.get_json()

    required_params = ['recipients', 'api_key']
    if not all(param in data for param in required_params):
        return jsonify({'error': f'Parâmetros obrigatórios: {required_params}'}), 400

    if not isinstance(data['recipients'], list) or not all(is_valid_email(email) for email in data['recipients']):
        return jsonify({'error': 'Lista de destinatários inválida'}), 400

    project = Project.query.filter_by(api_key=data['api_key']).first()
    if not project:
        return jsonify({'error': 'Projeto não encontrado'}), 404

    try:
        subject = data.get('subject', 'Sem assunto')
  
        body = data.get('body', '')
        html_content = data.get('html_content')
        sender = data.get('sender')
        assert sender, 'Sender is required'
        attachments = data.get('attachments')
        cc = data.get('cc')
        bcc = data.get('bcc')
        reply_to = data.get('reply_to')
        date = data.get('date')
        charset = data.get('charset')
        extra_headers = data.get('extra_headers')
        mail_options = data.get('mail_options')
        rcpt_options = data.get('rcpt_options')

        send_custom_email(
            recipients=data['recipients'],
            subject=subject,
            body=body,
            html_content=html_content,
            sender=sender,
            attachments=attachments,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            date=date,
            charset=charset,
            extra_headers=extra_headers,
            mail_options=mail_options,
            rcpt_options=rcpt_options,
            project=project
        )

        return jsonify({
            'message': 'Email enviado com sucesso',
            'details': {
                'recipients_count': len(data['recipients']),
                'subject': subject,
                'api_key': data['api_key'],
                'project_name': project.name
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao enviar email: {str(e)}'}), 500
