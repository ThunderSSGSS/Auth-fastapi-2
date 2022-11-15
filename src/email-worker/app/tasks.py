from .celery import app
from .settings import EMAIL
import time
import smtplib


def _send_email(to:str, subject:str, message:str):

	# Outlook
	email_user = EMAIL['email']
	email_password = EMAIL['password']

	email_text = "From: "+email_user+"\n"
	email_text+="To: "+to+"\n"
	email_text+= "Subject: "+subject+"\n"
	email_text+= message

	#send email by outlook smtp
	try:
		server = smtplib.SMTP('imap-mail.outlook.com', 587)
		try:
			server.ehlo()
			server.starttls()
			server.ehlo()    
			server.login(email_user,email_password)
        
			server.sendmail(email_user,to,email_text)
		except smtplib.SMTPException:
			print('Email connection error!')
		finally:
			server.quit()
	except Exception:
		print('Network error!')


#_______________TASKS_________________________________#

@app.task(name='send_email')
def send_email(to, subject, message):
	_send_email(to,subject,message)


@app.task(name='send_signup_email')
def send_signup_email(to, random_code, data_dict):
	message = "Your signup code is: "+random_code
	print(message)
	_send_email(to,'Signup CODE',message)


@app.task(name='send_password_forget_email')
def send_password_forget_email(to, random_code, data_dict):
	message = "Your restaure password CODE is: "+random_code
	print(message)
	_send_email(to,'Restaure Password CODE',message)


@app.task(name='send_set_email')
def send_set_email(to, random_code, data_dict):
	message = "Your restaure password CODE is: "+random_code
	print(message)
	_send_email(to,'Restaure Password CODE',message)