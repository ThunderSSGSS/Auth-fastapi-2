from .celery import app
from .settings import EMAIL
import time
import smtplib


def _send_email(to, subject, message):
	gmail_user = EMAIL['email']
	gmail_password = EMAIL['password']
	sent_from = gmail_user

	body =message

	email_text = "From: "+sent_from+"\n"
	email_text+="To: "+to+"\n"
	email_text+= "Subject: "+subject+"\n"
	email_text+= "\n"+body
	
	print("THE MESSAGE: ",message)
	server=None
	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com',465)
		server.ehlo()
		server.login(gmail_user,gmail_password)
		server.sendmail(sent_from,to,email_text)
		server.close()
		print("____MESSAGE_SENDED")
	except:
		print("____MESSAGE NOT SENDED")
		pass



@app.task(name='send_email')
def send_email(to, subject, message):
	_send_email(to,subject,message)


@app.task(name='send_signup_email')
def send_signup_email(to, random_key, data_dict):
	message = "Voce Abriu uma conta na APP, Use o numero para validar:\n"+str(random_key)
	print("_________RANDOM_Signup__: ",random_key)
	#_send_email(to,"NOVA CONTA",message)


@app.task(name='send_password_forget_email')
def send_password_forget_email(to, random_key, data_dict):
	print("_________RANDOM_Password__: ",random_key)


@app.task(name='send_set_email')
def send_set_email(to, random_key, data_dict):
	print("_______SET_EMAIL_Password__: ",random_key)