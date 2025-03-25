import re
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

mail = Mail()
serializer = URLSafeTimedSerializer('chave_temporaria') 

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def send_verification_email(email, project_name, token, host_url, project=None):
    verification_url = host_url.rstrip('/') + f'/api/verify/{token}'
    
    sender = project.mail_username if project and project.mail_username else 'noreply@example.com'
    
    msg = Message('Confirme seu Email',
                 sender=sender,
                 recipients=[email])
    msg.html = f'''
    <h1>Confirme seu Email</h1>
    <p>Para confirmar seu email para {project_name}, clique no link abaixo:</p>
    <p><a href="{verification_url}">Clique aqui para verificar seu email</a></p>
    <p>Se você não solicitou este email, ignore esta mensagem.</p>
    '''
    msg.body = f'''Para confirmar seu email para {project_name}, clique no link abaixo:
    {verification_url}

    Se você não solicitou este email, ignore esta mensagem.'''
    
    try:
        if project and project.mail_username and project.mail_password:
            # Configurar o Flask-Mail com as credenciais do projeto
            current_app.config['MAIL_USERNAME'] = project.mail_username
            current_app.config['MAIL_PASSWORD'] = project.mail_password
            
            # Criar uma nova instância do Mail com as configurações atualizadas
            project_mail = Mail(current_app)
            project_mail.send(msg)
        else:
            mail.send(msg)
            
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        raise

def send_custom_email(recipients, subject, body,
                      html_content=None, sender=None,
                      attachments=None, cc=None, bcc=None, reply_to=None,
                      date=None, charset=None, extra_headers=None,
                      mail_options=None, rcpt_options=None, project=None):
    
    try:
        if project and project.mail_username and project.mail_password:
            # Configurar o Flask-Mail com as credenciais do projeto
            current_app.config['MAIL_USERNAME'] = project.mail_username
            current_app.config['MAIL_PASSWORD'] = project.mail_password
            sender = project.mail_username
            
            # Criar uma nova instância do Mail com as configurações atualizadas
            project_mail = Mail(current_app)
        else:
            project_mail = mail
            
        msg = Message(subject,
                     sender=sender,
                     recipients=recipients,
                     body=body,
                     html=html_content,
                     cc=cc,
                     bcc=bcc,
                     reply_to=reply_to,
                     date=date,
                     charset=charset,
                     extra_headers=extra_headers,
                     mail_options=mail_options,
                     rcpt_options=rcpt_options)

        if attachments:
            for attachment in attachments:
                msg.attach(*attachment)

        project_mail.send(msg)
        
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        raise
