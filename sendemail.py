import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from settings import EMAIL_PWD

email = 'dsapozhnikov1991@gmail.com' # Your email
password = EMAIL_PWD # Your email account password
send_to_email = 'vova.ilchenko@gmail.com' # Who you are sending the message to
subject = 'New Shiny Reservation has been created!' # The subject line
message = 'This is my message' # The message in the email

msg = MIMEMultipart()
msg['From'] = formataddr((str(Header('Hot Desk Reservation System', 'utf-8')), 'dsapozhnikov1991@gmail.com'))
msg['To'] = send_to_email
msg['Subject'] = subject


msg.attach(MIMEText(message, 'plain'))

server = smtplib.SMTP('smtp.gmail.com', 587) # Connect to the server
server.starttls() # Use TLS
server.login(email, password) # Login to the email server
text = msg.as_string() # You now need to convert the MIMEMultipart object to a string to send
server.sendmail(email, send_to_email, text) # Send the email
server.quit() # Logout of the email server
