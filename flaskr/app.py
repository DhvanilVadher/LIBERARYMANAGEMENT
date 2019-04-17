from flask import Flask,render_template,request, session, flash, redirect, url_for,session,logging,request
import sqlite3
import json
import datetime, time
from flask import g
import hashlib
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from data import *
from datetime import date,datetime
DATABASE = 'database4.db'
app = Flask(__name__)
app.secret_key = "myfirstdbkey"
conn = sqlite3.connect(DATABASE)
c = conn.cursor()
#conn.execute('DROP TABLE USER IF EXIST')
conn.execute('CREATE TABLE IF NOT EXISTS USER (UID INTEGER PRIMARY KEY AUTOINCREMENT'
                                                +',NAME VARCHAR(10) NOT NULL'
                                                +',PASSWORD VARCHAR(100)NOT NULL'
                                                +',EMAIL VARCHAR(50)'
                                                +',TYPE INTEGER NOT NULL'
                                                +',ADDRESS VARCHAR(100)'
                                                +',BOOKCNT INTEGER DEFAULT 0 )')
conn.execute('CREATE TABLE IF NOT EXISTS AUTHOR (AID INTEGER PRIMARY KEY AUTOINCREMENT'
                                                +',NAME VARCHAR(10) NOT NULL'
                                                +',EMAIL VARCHAR(50),'
                                                +'ADDRESS VARCHAR(100) ) ')
conn.execute('CREATE TABLE IF NOT EXISTS PUBLISHER (PID INTEGER PRIMARY KEY AUTOINCREMENT'
                                                +',NAME VARCHAR(10) NOT NULL'
                                                +',EMAIL VARCHAR(50)'
                                                +',ADDRESS VARCHAR(100) ) ')
conn.execute('CREATE TABLE IF NOT EXISTS WRITE (BID INTEGER'
                                                +',AID INTEGER,FOREIGN KEY(BID) REFERENCES BOOK(BID)'
                                                +',FOREIGN KEY(AID) REFERENCES AUTHOR(AID))')
conn.execute('CREATE TABLE IF NOT EXISTS BOOK (BID INTEGER PRIMARY KEY AUTOINCREMENT'
                                                +',TITLE VARCHAR(30) NOT NULL'
                                                +',LANGUAGE VARCHAR(10) NOT NULL'
                                                +',BOOKCNT INTEGER DEFAULT 0,'
                                                +'TYPE VARCHAR(20) NOT NULL'
                                                +',SHELF_NO VARCHAR(5) NOT NULL'
                                                +',ATID INTEGER NOT NULL'
                                                +',PBID INTEGER NOT NULL,'
                                                +'FOREIGN KEY(ATID) REFERENCES AUTHOR(AID),'
                                                +'FOREIGN KEY(PBID) REFERENCES PUBLISHER(PID) )')
conn.execute('CREATE TABLE IF NOT EXISTS BORROWS (TID INTEGER PRIMARY KEY AUTOINCREMENT'
                                                +',UID INTEGER NOT NULL'
                                                +',BID INTEGER NOT NULL'
                                                +',STARTDATE TEXT'
                                                +',ENDDATE TEXT'
                                                +',FOREIGN KEY(UID) REFERENCES USER(UID)'
                                                +',FOREIGN KEY(BID) REFERENCES BOOK(BID) ) ')
# c.execute('SELECT * FROM blog;')

conn.commit()
print(c.fetchone())
conn.close()

class BOOK(Form):
    TITLE = StringField('TITLE',[validators.DataRequired()])
    LANGUAGE =StringField('LANGUAGE',[validators.DataRequired(),validators.AnyOf(['EN','HN','GUJ'])])
    TYPE = StringField('TYPE',[validators.DataRequired(),validators.AnyOf(['SCI','MAT','ENG','COM'])])
    SHELF = StringField('SHELF',[validators.DataRequired()])
    AUTHOR = StringField('AUTHOR',[validators.DataRequired()])
    BOOKCNT = StringField('BOOKCNT',[validators.DataRequired()])
    PUBLISHER = StringField('PUBLISHER',[validators.DataRequired()])

class AUTHOR(Form):
    NAME=StringField('NAME',[validators.DataRequired()])
    EMAIL=StringField('EMAIL',[validators.DataRequired()])
    ADDRESS=StringField('ADDRESS',[validators.DataRequired()])

class FRB(Form):
    BOOKID = StringField('BOOKID',[validators.DataRequired()])
    UID = StringField('UID',[validators.DataRequired()])
    FETCH_RETURN_BORROW = StringField('FETCH_RETURN_BORROW',[validators.DataRequired(),validators.AnyOf(['F','R','B'])])

class SEARCH(Form):
    SEARCHHERE = StringField('SEARCHHERE',[validators.DataRequired()])

class RegisterForm(Form):
    NAME = StringField('NAME',[validators.Length(min=1,max=20),validators.DataRequired()])
    EMAIL = StringField('EMAIL',[validators.Length(min=1,max=29)])
    PASSWORD =PasswordField('PASSWORD',[
    validators.DataRequired(),
    validators.EqualTo('CONFIRM',message='Passwords do not match')
    ])
    print("aaaaa")
    ADDRESS = StringField('ADDRESS',[validators.Length(min=1,max=100)])
    TYPE = StringField('TYPE',[validators.AnyOf(['1','2','3'])])
    CONFIRM = PasswordField('CONFIRM')

class LoginForm(Form):
    NAME = StringField('NAME',[validators.Length(min=1,max=20),validators.DataRequired()])
    PASSWORD=PasswordField('PASSWORD',[
    validators.DataRequired(),
    validators.EqualTo('CONFIRM',message='Passwords do not match')
    ])

@app.route('/aduser',methods=['GET','POST'])
def aduser():
        form = RegisterForm(request.form)
        print("bbbb")
        if request.method == 'POST' and form.validate():
            with sqlite3.connect(DATABASE) as conn:
                cur=conn.cursor()
                NAME = request.form['NAME']
                PASSWORD = request.form['PASSWORD']
                EMAIL = request.form['EMAIL']
                SALT = '777'
                actualP = PASSWORD+SALT
                h = hashlib.md5(actualP.encode())
                ADDRESS = request.form['ADDRESS']
                TYPE = request.form['TYPE']
                data = cur.execute('SELECT * FROM USER WHERE NAME=? OR PASSWORD=?;',(NAME,h.hexdigest()))
                data=cur.fetchall()
                if len(data)>0:
                        flash('Name or password already registered')
                        return "<script>alert('USER EXISTS');window.location='/'</script>"
                else:
                        cur.execute('INSERT INTO USER(NAME,PASSWORD,EMAIL,TYPE,ADDRESS) VALUES(?,?,?,?,?);',(NAME,h.hexdigest(),EMAIL,2,ADDRESS))
                        conn.commit()
                        print("dhvanil")
                        return "<script>alert('Yeah You registerend successfull');window.location='/'</script>"
                        conn.close()
        else:
            return render_template('register.html',form = form)


@app.route('/frb',methods=['GET','POST'])
def frb():
    form = FRB(request.form)
    if session.get('loggedin')==True :
        if form.validate():
            BOOKID = request.form['BOOKID']
            UID = request.form['UID']
            FETCH_RETURN_BORROW = request.form['FETCH_RETURN_BORROW']
            print(FETCH_RETURN_BORROW)
            if FETCH_RETURN_BORROW=='B':
                print("bbbb")
                with sqlite3.connect(DATABASE) as conn:
                    print('bbbb')
                    TODAY = str(date.today())
                    cur = conn.cursor()
                    p=cur.execute('SELECT * FROM BOOK WHERE BID = ?',(int(BOOKID),))
                    p=cur.fetchall()
                    q=cur.execute('SELECT * FROM USER WHERE UID = ?',(int(UID),))
                    q=cur.fetchall()
                    if len(p)>0 and len(q)>0:
                        z=cur.execute('SELECT BOOKCNT FROM BOOK WHERE BID = ?',(BOOKID,))
                        z=cur.fetchone()[0]
                        y=cur.execute('SELECT BOOKCNT FROM USER WHERE UID = ?',(UID,))
                        y=cur.fetchone()[0]
                        if z>0 and y<=4:
                            cur.execute('UPDATE USER SET BOOKCNT=(SELECT BOOKCNT FROM USER WHERE UID=?)+1 WHERE UID=?',(UID,UID))
                            cur.execute('UPDATE BOOK SET BOOKCNT=(SELECT BOOKCNT FROM BOOK WHERE BID=?)-1 WHERE BID=?',(BOOKID,BOOKID))
                            cur.execute('INSERT INTO BORROWS (UID,BID,STARTDATE) VALUES (?,?,?)',(int(UID),int(BOOKID),TODAY))
                            conn.commit()
                            return "<script>alert('Successfully added');window.location='/frb'</script>"
                        elif z<=0:
                            return "<script>alert('BOOK NOT AVALIABLE');window.location='/frb'</script>"
                        else:
                            return "<script>alert('MAXIMUM BORROWED BOOKS =3');window.location='/frb'</script>"
                    elif len(p)<=0:
                        return "<script>alert('BOOK NOT AVALIABLE');window.location='/frb'</script>"
                    else :
                        return "<script>alert('USER NOT AVALIABLE');window.location='/frb'</script>"
                    return "hi"
                conn.close()
            elif FETCH_RETURN_BORROW =='R':
                print("rrrr")
                with sqlite3.connect(DATABASE) as conn:
                    print('rrrr')
                    TODAY = str(date.today())
                    cur = conn.cursor()
                    p=cur.execute('SELECT * FROM BOOK WHERE BID = ?',(int(BOOKID),))
                    p=cur.fetchall()
                    q=cur.execute('SELECT * FROM USER WHERE UID = ?',(int(UID),))
                    q=cur.fetchall()
                    if len(p)>0 and len(q)>0:
                        z=cur.execute('SELECT BOOKCNT FROM BOOK WHERE BID = ?',(BOOKID,))
                        z=cur.fetchone()[0]
                        y=cur.execute('SELECT BOOKCNT FROM USER WHERE UID = ?',(UID,))
                        y=cur.fetchone()[0]
                        if y>0:
                            cnt= cur.execute('SELECT BOOKCNT FROM USER WHERE UID = ?',(UID,))
                            cnt= cur.fetchone()[0]
                            cnt2 =cur.execute('SELECT BOOKCNT FROM BOOK WHERE BID = ?',(BOOKID,))
                            cnt2= cur.fetchone()[0]
                            cur.execute('UPDATE USER SET BOOKCNT=? WHERE UID=?',(int(cnt)+1,UID))
                            cur.execute('UPDATE BOOK SET BOOKCNT=? WHERE BID=?',(int(cnt)-1,BOOKID))
                            cur.execute('UPDATE BORROWS SET ENDDATE=? WHERE UID=? AND BID = ?',(TODAY,int(UID),int(BOOKID)))
                            d =  cur.execute('SELECT STARTDATE FROM BORROWS WHERE UID=? AND BID = ? ORDER BY TID DESC;',(int(UID),int(BOOKID)))
                            d =  cur.fetchone()[0]
                            print(str(d)+'')
                            e =  cur.execute('SELECT ENDDATE FROM BORROWS WHERE UID=? AND BID = ? ORDER BY TID DESC',(int(UID),int(BOOKID)))
                            e =  cur.fetchone()[0]
                            d = datetime.strptime(d, "%Y-%m-%d")
                            e = datetime.strptime(e, "%Y-%m-%d")
                            s=abs((d-e).days)
                            if s-15>0:
                                s=s-15
                            conn.commit()
                            return "<script>alert('SUccessfully Returned Panelty = "+str(s)+"');window.location='/frb'</script>"
                        else:
                            return "<script>alert('NO BOOK BORROWED');window.location='/frb'</script>"
                    elif len(p)<=0:
                        return "<script>alert('BOOK NOT AVALIABLE');window.location='/frb'</script>"
                    else :
                        return "<script>alert('USER NOT AVALIABLE');window.location='/frb'</script>"
                    return "hi2"
                conn.close()
            else:
                return "<script>alert('Enter Data wisely');window.location='/frb'</script>"
        else:
            form=FRB(request.form)
            return render_template('frb.html',form=form)
    else:
        return "<script>alert('you are not logged in ');window.location='/'</script>"

@app.route('/search',methods=['GET','POST'])
def search():
    form2= SEARCH(request.form)
    if request.method=='POST':
        print('post')
        SEARCHHERE = request.form['SEARCHHERE']
        if form2.validate():
            SEARCHHERE = request.form['SEARCHHERE']
            conn1 = sqlite3.connect(DATABASE)
            cur1= conn1.cursor()
            SQL = cur1.execute('SELECT * FROM BOOK WHERE TITLE LIKE ?',('%'+SEARCHHERE+'%',))
            SQL = cur1.fetchall()
            print(SQL)
            print('RRRRRRRRRRRRR')
            return render_template('SearchBook.html',form = form2,data=SQL)
    else:
        return render_template('SearchBook.html',form=form2)


article = Articles()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/adbok',methods=['GET','POST'])

def adbok():
    if session.get('loggedin') == False:
        return "<script>alert('you are NOT logged in');window.location='/'</script>"
    else:
        form = BOOK(request.form)
        if request.method == 'POST' and form.validate():
            with sqlite3.connect(DATABASE) as conn:
                cur=conn.cursor()
                TITLE = request.form['TITLE']
                LANGUAGE = request.form['LANGUAGE']
                TYPE = request.form['TYPE']
                SHELF = request.form['SHELF']
                BOOK_COUNT = request.form['BOOKCNT']
                AUTHOR = request.form['AUTHOR']
                PUBLISHER = request.form['PUBLISHER']
                cur= conn.cursor()
                data = cur.execute('SELECT NAME FROM AUTHOR WHERE NAME=?;',(AUTHOR,))
                data = data.fetchall()
                if len(data)==0:
                    return "<script>alert('Author is not Known');</script>"
                data  = cur.execute('SELECT * FROM PUBLISHER WHERE NAME=?;',(PUBLISHER,))
                data = data.fetchall()
                if len(data)==0:
                    return "<script>alert('PUBLISHER is not Known');</script>"
                AID = cur.execute('SELECT AID FROM AUTHOR WHERE NAME = ?;',(AUTHOR,))
                AID = cur.fetchone()[0]
                PID = cur.execute('SELECT PID FROM PUBLISHER WHERE NAME = ?;',(PUBLISHER,))
                PID = cur.fetchone()[0]
                cur.execute('INSERT INTO BOOK(TITLE,LANGUAGE,BOOKCNT,TYPE,SHELF_NO,ATID,PBID) VALUES(?,?,?,?,?,?,?);',(TITLE,LANGUAGE,int(BOOK_COUNT),TYPE,SHELF,int(AID),int(PID)))
                conn.commit()
                return "<script>alert('Successfully Added In');window.location='/'</script>"
                conn.close()
        else:
            return render_template ('adbok.html',form=form)

@app.route('/adauth',methods=['GET','POST'])
def adauth():
    if session.get('loggedin')==False:
        return "<script>alert('you are already logged in');window.location='/login'</script>"
    else:
        form = AUTHOR(request.form)
        if request.method == 'POST' and form.validate():
            with sqlite3.connect(DATABASE) as conn:
                cur = conn.cursor()
                NAME = request.form['NAME']
                EMAIL = request.form['EMAIL']
                ADDRESS = request.form['ADDRESS']
                print(NAME)
                print(EMAIL)
                data = cur.execute('SELECT * FROM AUTHOR WHERE NAME=?;',(NAME,))
                data = data.fetchall()
                if len(data)!=0:
                    return "<script>alert('Author is Known'); window.location='/adauth'</script>"
                cur.execute('INSERT INTO AUTHOR(NAME,EMAIL,ADDRESS) VALUES(?,?,?);',(NAME,EMAIL,ADDRESS))
                conn.commit()
                print("dhvanil")
                return "<script>alert('Successfully Logged In');window.location='/'</script>"
                conn.close()
        else:
            return render_template('adauth.html',form = form)


@app.route('/adpub',methods=['GET','POST'])
def adpub():
    form = AUTHOR(request.form)
    if session.get('loggedin')==False:
        return "<script>alert('you are already logged in');window.location='/login'</script>"
    else:
        if request.method == 'POST' and form.validate():
            with sqlite3.connect(DATABASE) as conn:
                cur = conn.cursor()
                NAME = request.form['NAME']
                EMAIL = request.form['EMAIL']
                ADDRESS = request.form['ADDRESS']
                print(NAME)
                data = cur.execute('SELECT * FROM PUBLISHER WHERE NAME=?;',(NAME,))
                data = data.fetchall()
                if len(data)!=0:
                    return "<script>alert('Author is Known'); window.location='/adpub'</script>"
                cur.execute('INSERT INTO PUBLISHER(NAME,EMAIL,ADDRESS) VALUES(?,?,?);',(NAME,EMAIL,ADDRESS))
                conn.commit()
                print("dhvanil")
                return "<script>alert('Successfully Logged In');window.location='/'</script>"
                conn.close()
        else:
            return render_template('adpub.html',form = form)

@app.route('/logout',methods=['GET','POST'])
def logout():
    print(session.keys())
    session.clear()
    print(session.keys())
    flash('Logged out')
    return redirect(url_for('index'))

@app.route('/articles')
def articles():
    return render_template('articles.html',articles = article)

@app.route('/articles/<string:id>/')
def singlearticle(id):
    return render_template('singlearticle.html',id = id,articles = article)


@app.route('/register',methods=['GET','POST'])
def register():
    if session.get('loggedin'):
        return "<script>alert('you are already logged in');window.location='/'</script>"
    form = RegisterForm(request.form)
    print("bbbb")
    if request.method == 'POST' and form.validate():
        with sqlite3.connect(DATABASE) as conn:
            cur=conn.cursor()
            NAME = request.form['NAME']
            PASSWORD = request.form['PASSWORD']
            EMAIL = request.form['EMAIL']
            SALT = '777'
            actualP = PASSWORD+SALT
            h = hashlib.md5(actualP.encode())
            ADDRESS = request.form['ADDRESS']
            TYPE = request.form['TYPE']
            data = cur.execute('SELECT * FROM USER WHERE NAME=? OR PASSWORD=?;',(NAME,h.hexdigest()))
            data=cur.fetchall()
            if len(data)>0:
                    flash('Name or password already registered')
                    return "<script>alert('USER EXISTS');window.location='/'</script>"
            else:
                    cur.execute('INSERT INTO USER(NAME,PASSWORD,EMAIL,TYPE,ADDRESS) VALUES(?,?,?,?,?);',(NAME,h.hexdigest(),EMAIL,int(TYPE),ADDRESS))
                    conn.commit()
                    print("dhvanil")
                    return "<script>alert('Yeah You registerend successfull');window.location='/'</script>"
                    conn.close()
    else:
        return render_template('register.html',form = form)

@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('loggedin'):
        return "<script>alert('You are already loggedin');window.location='/'</script>"
    else:
        form2= LoginForm(request.form)
        if request.method =='POST':
            with sqlite3.connect(DATABASE) as conn:
                cur1 = conn.cursor()
                NAME = request.form['NAME']
                PASSWORD = request.form['PASSWORD']
                SALT = '777'
                actualP = PASSWORD+SALT
                h = hashlib.md5(actualP.encode())
                data = cur1.execute('SELECT * FROM USER WHERE NAME=? and PASSWORD = ?;',(NAME,h.hexdigest()))
                data = cur1.fetchall()
                if len(data)>0:
                    session['loggedin']=True
                    session['name']=NAME
                    flash('You are successfully logged in')
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html',form=form2)
        else:
            return render_template('login.html',form = form2)
@app.route('/userbook')
def userbook():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    data=cur.execute('SELECT * FROM USER')
    data=cur.fetchall()
    data2=cur.execute('SELECT * FROM BOOK')
    data2=cur.fetchall()
    return render_template('userbook.html',data=data,data2=data2)

if __name__ == '__main__':
    app.run(port=5001,debug = True)
