# email_utils.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Lock

class EmailSender:
    _instance = None
    _lock = Lock()

    def __new__(cls, smtp_server, smtp_port, smtp_username, smtp_password, sender_email):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmailSender, cls).__new__(cls)
                cls._instance.smtp_server = smtp_server
                cls._instance.smtp_port = smtp_port
                cls._instance.smtp_username = smtp_username
                cls._instance.smtp_password = smtp_password
                cls._instance.sender_email = sender_email
                cls._instance.server = None
                cls._instance._connect()  # Initialize the SMTP connection
            return cls._instance

    def _connect(self):
        """Establish the SMTP connection."""
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)  # Added timeout for connection stability
            self.server.starttls()
            self.server.login(self.smtp_username, self.smtp_password)
            print("SMTP connection established and logged in.")
        except Exception as e:
            print(f"Failed to connect to SMTP server: {e}")
            self.server = None  # Ensure server is set to None if connection fails
            raise

    def send_email(self, subject, body, to_email):
        """Send an email, maintaining the connection."""
        try:
            if self.server is None or not self._is_connected():
                print("Reconnecting to the SMTP server...")
                self._connect()

            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = to_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            self.server.sendmail(self.sender_email, to_email, message.as_string())
            print(f"Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"Error while sending email: {e}")
            return False

    def _is_connected(self):
        """Check if the connection to the SMTP server is alive."""
        try:
            return self.server.noop()[0] == 250  # Return True if SMTP connection is active
        except Exception as e:
            print(f"SMTP connection lost: {e}")
            return False

    def close(self):
        """Close the SMTP connection."""
        if self.server:
            try:
                self.server.quit()
                print("SMTP connection closed.")
            except Exception as e:
                print(f"Error closing SMTP connection: {e}")
            finally:
                self.server = None  # Ensure server is None after quitting
