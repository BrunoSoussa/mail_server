import smtplib
import ssl
from email.mime.text import MIMEText

# Configurações do email
subject = "emproho"
body = "Este é o corpo da mensagem."
sender = "contato@jm2.tec.br"
recipients = ["marcosayres.brasil@gmail.com"]
password = "tNd9MPYpf0Yt"  # sua senha Zoho

def send_email_starttls_with_context(subject, body, sender, recipients, password):
    # Cria o objeto MIMEText
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    # Cria um contexto SSL que usa os certificados raíz do sistema
    context = ssl.create_default_context()

    # Conecta em texto claro na porta 587 e faz upgrade para TLS usando o contexto
    with smtplib.SMTP("smtp.zoho.com", 587) as smtp:
        smtp.ehlo()  # identifica o cliente para o servidor
        smtp.starttls(context=context)  # sobe para TLS
        smtp.ehlo()  # re-identifica já em TLS
        smtp.login(sender, password)  # faz login
        smtp.sendmail(sender, recipients, msg.as_string())  # envia mensagem

    print("Email enviado com STARTTLS + SSLContext na porta 587!")

if __name__ == "__main__":
    send_email_starttls_with_context(subject, body, sender, recipients, password)
