
#name2-js   ,name-python
from flask import Flask,render_template,request,session,redirect,flash


import math

import os

from flask_mail import Mail

from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

from werkzeug.utils import secure_filename

import json

with open("config.json","r") as c:
    params=json.load(c)["params"]

local_server=True

app=Flask(__name__)

app.secret_key='super-secret-key'

app.config['UPLOAD_FOLDER']=params['upload_location']

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)

mail=Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)
# sno,name,email,phone_no,date,msg
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(20),nullable=False)
    phone_no = db.Column(db.String(12),nullable=False)
    date = db.Column(db.String(12), nullable=True)
    msg = db.Column(db.String(120), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),nullable=False)
    tag_line = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(21),nullable=False)
    content = db.Column(db.String(120),nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file=db.Column(db.String(12),nullable=True)
class Admin(db.Model):
    user=db.Column(db.Integer, nullable=False)
    pass=db.Column(db.String(50), nullable=False)


@app.route("/")
def home():

    # flash("subscribe to this channel",'success')
    posts = Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_post']))
    # [0:params['no_of_post']]

    page=(request.args.get('page'))
    # page=int(page)
    if(not str(page).isnumeric()):
        page=1
    posts=posts[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    # last
    elif (page==last):
        prev="/?page="+str(page-1)
        next="#"
    else:
        prev = "/?page=" + str(page-1)
        next = "/?page=" + str(page+1)



    return render_template("index.html",params=params,posts=posts,prev=prev,next=next)


@app.route("/about")
def about():
    return render_template("about.html",params=params)


@app.route("/contact",methods=['GET','POST'])
def contact():

    if (request.method=='POST'):
        '''ADD ENTRY TO DATABASE'''
        name=request.form.get('name')
        email=request.form.get('email')    #name inn form
        phone = request.form.get('phone')
        message = request.form.get('message')
        # sno,name,email,phone_no,date,msg
        entry=Contacts(name=name,email=email,phone_no=phone,date=datetime.now(),msg=message)
        db.session.add(entry)
        db.session.commit()
        # mail.send_message("new message from "+name,sender=email,recipients=[params['gmail-user']],
        #                   body=message+"\n"+phone)
        flash("Thanks for submitting your details .We will get back you soon ","success")
    return render_template("contact.html", params=params)


@app.route("/post/<string:post_slug>",methods=["GET"])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params,post=post)



@app.route("/edit/<string:sno>",methods=["GET","POST"])
def edit(sno):
    if ("user" in session and session["user"] == params["admin_user"]):
        if request.method=="POST":
            box_title=request.form.get('title')
            tline=request.form.get('tline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            date=datetime.now()
            img_file=request.form.get('img_file')
            if sno=='0':
                post=Posts(title=box_title,slug=slug,content=content,date=date,tag_line=tline,img_file=img_file)
                db.session.add(post)
                db.session.commit()


            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.tag_line=tline
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template("edit.html",params=params,post=post,sno=sno)


@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if ("user" in session and session["user"] == params["admin_user"]):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/login')


@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if ("user" in session and session["user"] == params["admin_user"]):
        if (request.method=="POST"):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "Uploaded Successfully"

@app.route("/login",methods=['GET','POST'])
def login():
    if ("user" in session and session["user"]==params["admin_user"]):
        posts=Posts.query.filter_by.all()
        user=


        return render_template("dashboard.html",params=params,posts=posts)
    if request.method=="POST":
        username=request.form.get('uname')
        userpass = request.form.get('pass')
        if(username==params['admin_user'] and userpass==params['admin_password']):
            # set session variable
            session['user']=username
            posts=Posts.query.all()
            return render_template("dashboard.html",params=params,posts=posts)

    return render_template("login.html",params=params)



@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/login")




app.run(debug=True)