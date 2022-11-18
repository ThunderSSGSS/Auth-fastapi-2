from celery import Celery
from celery.signals import worker_init
from time import sleep
from .settings import RABBITMQ_URI, DEFAULT_QUEUE, ADMIN_USER_EMAIL
#database
from .database import engine, Base, SessionLocal
from .signals import create_group, create_permission, create_group_permission, create_admin_user


broker=RABBITMQ_URI
app = Celery('users_db_celery', broker=broker, include=['app.tasks'])
app.conf.task_default_queue=DEFAULT_QUEUE


#___________SIGNALS_____________#
def create_tables():
	for i in range(1,101):
		try: 
			Base.metadata.create_all(bind=engine)
			break
		except:
			print('Error connecting to database. Try again in 6 seconds. ('+str(i)+'/100)')
			sleep(6)


@worker_init.connect
def define_database(**kwargs):
	create_tables()
	db = SessionLocal()
	setted=False

	#__________________GROUPS________________________#
	if create_group(db, 'normal'): setted=True

	#_______________PERMISSIONS________________________#
	
	#_________administrators_permissions__________#
	if create_permission(db, 'admin'): setted=True
	
	#users management permissions
	if create_permission(db, 'create_user'): setted=True
	if create_permission(db, 'read_user'): setted=True
	if create_permission(db, 'update_user'): setted=True
	if create_permission(db, 'delete_user'): setted=True
	
	#permissions management permissions
	if create_permission(db, 'create_permission'): setted=True
	if create_permission(db, 'read_permission'): setted=True
	if create_permission(db, 'delete_permission'): setted=True

	#groups managemnt permissions
	if create_permission(db, 'create_group'): setted=True
	if create_permission(db, 'read_group'): setted=True
	if create_permission(db, 'delete_group'): setted=True

	#grant permissions and groups managemnt permissions
	if create_permission(db, 'grant_permission_to'): setted=True
	if create_permission(db, 'remove_permission_from'): setted=True
	if create_permission(db, 'add_user_to_group'): setted=True
	if create_permission(db, 'remove_user_from_group'): setted=True

	#session managemnt permissions
	if create_permission(db, 'delete_session'): setted=True


	#_____________normal_users_permissions____________#
	#normal permissions
	if create_permission(db, 'logout'): setted=True
	if create_permission(db, 'set_own_password'): setted=True
	if create_permission(db, 'set_own_email'): setted=True
	if create_permission(db, 'set_own_username'): setted=True
	if create_permission(db, 'read_own_user_data'): setted=True
	
	#add permissions to normal group
	if create_group_permission(db, 'normal', 'set_own_password'): setted=True
	if create_group_permission(db, 'normal', 'set_own_email'): setted=True
	if create_group_permission(db, 'normal', 'set_own_username'): setted=True
	if create_group_permission(db, 'normal', 'read_own_user_data'): setted=True
	if create_group_permission(db, 'normal', 'logout'): setted=True

	#USER ADMIN
	if ADMIN_USER_EMAIL is not None:
		if create_admin_user(db, ADMIN_USER_EMAIL): setted=True

	if setted:
		db.commit()
		print('Database Defined')
	db.close()