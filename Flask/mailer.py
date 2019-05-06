import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer:

    # The mailer uses this SMTP-server to send mails.
    # Port 587 is secure TLS on google smtp-server.
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)

    def __init__(self, email, password, envelope_name=None):
        """
        The Mailer is used to send mails on behalf of the specified user.
        The envelope name is the envelope sender of the mail. By default this equals the from-sender.
        :param email: The email to send from
        :param password: Password to login to email
        :param envelope_name: The envelope-sender of the email
        """
        self.email = email
        self.password = password
        if envelope_name:
            self.envelope_name = envelope_name
        else:
            self.envelope_name = self.email

    def open_server(self):
        """
        Must be used before sending mails with the mailer.
        Readies the mailer for use with encryption and the set mail-login.
        """
        self.smtp_server.ehlo()
        self.smtp_server.starttls()
        self.smtp_server.login(self.email, self.password)

    def close_server(self):
        """
        Should be used after sending mails with the sender to
        ensure that the connection does not stay open.
        """
        self.smtp_server.quit()

    def send_mail(self, subject, content, receiver, mime_type="plain"):
        """
        Sends a mail to the specified receiver from the mail that was specified as login.
        :param subject: The subject of the mail
        :param content: The content of the mail
        :param receiver: The receiver of the mail
        :param mime_type: What kind of MIME-type is the content (i.e. 'plain', 'html' etc. )
        """
        message = self.generate_message(subject, content, receiver, mime_type)
        self.smtp_server.sendmail(self.email, receiver, message.as_string())

    def generate_message(self, subject, content, receiver, mime_type):
        """
        Generates a mail of the given mime-type with the given content.
        :param subject: The subject of the mail
        :param content: The content of the mail
        :param receiver: The receiver of the mail
        :param mime_type: The MIME-type for the mail
        """
        msg = MIMEMultipart('alternative')
        msg['subject'] = subject
        msg['from'] = self.email
        msg['to'] = receiver
        content = MIMEText(content, mime_type)
        msg.attach(content)
        return msg

    def send_password_reset(self, receiver, password):
        """
        Sends a mail to the receiver, informing the user about its new password.
        :param receiver: The receiver of the mail
        :param password: The new password
        """
        content = """\
        <html>
            <head><head>
            <body>
            <h2>Nytt passord</h2>
            <p>Du har bedt om å få tilsendt et nytt passord. Ditt nye passord er: <span style="font-weight : bold;">{}</span> <br> 
            Vennligst endre passordet dit ved å gå til "Profil" når du <a href="www.fikto.no">logger inn</a></p>
            <p><br>Obs: Vennligst ikke svar på denne mailen.</p>
            </body>
        </html>
        """.format(password)
        self.send_mail("Nytt Passord", content, receiver, mime_type='html')

    def send_new_user(self, receiver, password):
        """
        Sends a mail to the receiver, informing them that they now have a user for our app and provides them with a
        password they can use to login.
        :param receiver: The receiver of the mail.
        :param password: The password of the user.
        """
        content = """\n
        <html>
            <head></head>
            <body>
            <h2>Velkommen!</h2>
            <p>Du er nå registrert hos oss og kan nå <a href="www.fikto.no">logge inn</a> for å bruke vår applikasjon</p>
            <p>Epost: {} <br> Passord: {} </p>
            <p><br>Obs: Vennligts ikke svar på denne mailen.</p>
            </body>
        </html>
        """.format(receiver, password)
        self.send_mail("Velkommen til oss!", content, receiver, mime_type='html')











