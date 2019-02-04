from flask import Flask, render_template, request,url_for ,redirect
from flask_mail import Mail,Message
import sqlite3,getpass,time,os,random

app = Flask(__name__)
mail=Mail(app)

userData = sqlite3.connect(os.path.abspath(os.path.dirname(__file__))+'/Database/userdata.db',check_same_thread=False)
feedData= sqlite3.connect(os.path.abspath(os.path.dirname(__file__))+'/Database/techfeeds.db',check_same_thread=False)

def config():
	app.config['MAIL_SERVER']='smtp.gmail.com'
	app.config['MAIL_PORT'] = 465
	app.config['MAIL_USERNAME'] = 'test.111.anonymous@gmail.com'
	app.config['MAIL_PASSWORD'] = 'test111@123' 
	app.config['MAIL_USE_TLS'] = False
	app.config['MAIL_USE_SSL'] = True
	mail=Mail(app)


def retrive(data,table_name,something_else=''):
	data=data.execute("select * from "+table_name+something_else)
	return data.fetchall()

def randsend(data,table_name):
	feeds=data.execute("select max(feed_no),min(feed_no) from "+table_name)
	feeds=feeds.fetchall()
	loop_feed=data.execute("select count(feed_no) from "+table_name)
	loop_feed=loop_feed.fetchall()
	email=[]
	print(loop_feed[0])
	for j in range(loop_feed[0]):
		ran=random.randrange(feeds[0][1],feeds[0][0])
		final=data.execute("select * from "+table_name+" where feed_no="+str(ran))
		final=final.fetchall()
		email.append(final)
	print(email)
	while check(email[0],email[1])==False:
		if check(email[0],email[1])==True:
			return email
			break
		else:
			ran=random.randrange(feeds[0][1],feeds[0][0])
			final=data.execute("select feed_no,feed_links from "+table_name+" where feed_no="+str(ran))
			final=final.fetchall()
			check(email[0],email[1])

	return email
	
	
def check(ran,links):
	try:
		userData.execute('create table history(si integer primary key,links varchar(20))')
	except:
		try:
			userData.execute('insert into history(si,links) values(?,?)',(ran,links))
			userData.commit()
			return True
		except:
			return False
		


		
	
def mail_sender(user_value,feed_vlaue1,feed_vlaue2):
	msg=Message('hello '+user_value[1],sender="feed at",recipients=[user_value[2]])
	#msg.body="Title:"+feed_vlaue[2]+"\nSummary:"+feed_vlaue[3]+'\nLinke:'+feed_vlaue[1]
	msg.html=render_template('email_template.html',title1=feed_vlaue1[3],title2=feed_vlaue2[3],summary1=feed_vlaue1[4],summary2=feed_vlaue2[4],feed_link1=feed_vlaue1[1],feed_link2=feed_vlaue2[1])
	mail.send(msg)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/subscribe')
def subscribe():
	return render_template('subscribe.html')

@app.route('/result',methods=['GET','POST'])
def result():
	try:
		userData.execute('CREATE TABLE user(si integer primary key,name varchar(20),email varchar(50),time int,last int)')
	except:
		pass
	userData.execute('INSERT INTO user(name,email,time,last) VALUES(?,?,?,?)',(request.form['username'],request.form['email_id'],request.form['time'],0))
	userData.commit()
	return render_template('result.html')	

@app.route('/send')
def send():
	 feed_vlaue=randsend(feedData,'techfeeds')
	 users=userData
	 for i in range(0,len(feed_vlaue),2):
	 	maxim=users.execute('select max(time) from user where last='+str(i))
	 	maxim=maxim.fetchall()
	 	min,sec=0,0
	 	while min<maxim[0][0]:
	 		if sec==60:
	 			min+=1
	 			sec=0
	 			for user_value in retrive(users,'user',' where (last<'+str(feed_vlaue[i][0])+' and time='+str(min)+')'):
	 				if user_value != '':
	 					mail_sender(user_value,feed_vlaue[i],feed_vlaue[i])
	 					value=userData
	 					value.execute('update user set last='+str(feed_vlaue[i][0])+' where (last<'+str(feed_vlaue[i][0])+' and time='+str(min)+')')
	 					value.commit()
	 					print('Done')

	 		sec+=1
	 		time.sleep(1)
	 		print('{}min:{}sec'.format(min,sec))
	 return "thank you"

@app.route('/admin')
def admin():
	return render_template('adminSignin.html')

@app.route('/j_acegi_security_check',methods=['GET','POST'])
def Check():
	if request.form['j_username']=='admin' and request.form['j_password']=='admin':
		Data=retrive(feedData,'techfeeds')
		return render_template('db_table.html',data=Data)
	else:
		return render_template('adminSignin.html',info="please check username or password")

@app.route('/save',methods=['GET','POST'])	
def add():
	opt=request.form['opt']
	if opt=='add':
		test=feedData.execute("""select * from techfeeds where feed_links = ?""",[request.form['feedLinks']])
		if len(test.fetchall()) == 0:
			feedData.execute('insert into techfeeds(feed_links,tags,summary) values(?,?,?)',(request.form['feedLinks'],request.form['tags'],request.form['summary']))		
			info = "new feed inserted"
		else:
			return render_template('db_table.html',info="feed link already existing",data=retrive(feedData,'techfeeds'))
	elif opt=='delete':
		feedData.execute('delete from techfeeds where feed_no='+request.form['feedNo'])
		info = "feed deleted"
	elif opt=='update':
		feedData.execute("""update techfeeds set feed_links = ? ,tags = ? ,summary = ? where feed_no = ?""",(request.form['feedLinks'],request.form['tags'],request.form['summary'],request.form['feedNo']))
		info = "feed updated"
	feedData.commit()
	return render_template('db_table.html',data=retrive(feedData,'techfeeds'),info=info)

if __name__== "__main__":
	config()
	app.run()
