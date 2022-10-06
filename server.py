import os
import flask
from sqlalchemy import false, or_
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
from flask import Flask, flash, jsonify, redirect, url_for, render_template, send_from_directory, request, Response, session, send_file, abort
import time
from random import randint
import json
import flask_admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
import random

filePath = os.path.realpath(__file__)
filePath = filePath.replace('\\server.py', '')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KutyaFasz!123'
app.config['UPLOAD_FOLDER'] = './static/uploads'
app.permanent_session_lifetime = timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{filePath}/datasheets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
admin = flask_admin.Admin(app, name='Datasheets')

#databases
class Datasheets(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String)
    subtitle = db.Column(db.String)
    desc = db.Column(db.String)
    basePath = db.Column(db.String)
    imgName = db.Column(db.String)
    pdfName = db.Column(db.String)
    
    def __repr__(self):
        return f'{self.id}; {self.title}'

with app.app_context():
    db.create_all()
#admin panel

admin.add_view(ModelView(Datasheets, db.session))

admin.add_link(MenuLink(name='Site', url='/'))

#ip functions
@app.before_request
def showIp():
    print(request.headers.get('X-FORWARDED-FOR'))

@app.route('/')
def index():
    sheets = db.session.query(Datasheets).all()
    return render_template('index.html', serach=False, sheets=sheets)

@app.route('/search')
def search():
    squery = request.args["q"]
    sheets = db.session.query(Datasheets).filter(or_(Datasheets.title.contains(squery), Datasheets.subtitle.contains(squery))).all()
    return render_template('index.html', search=True, sheets=sheets, squery=squery)

@app.route('/api/upload', methods=["POST", "GET"])
def upload():
    icon = request.files["icon"]
    pdf = request.files["pdf"]
    title = request.form["title"]
    subtitle = request.form["subtitle"]
    desc = request.form["desc"]

    try:
        id = int(db.session.query(Datasheets).order_by(Datasheets.id.desc()).first().id) + 1
    except:
        id = 1
    
    basePath = f".\\static\\sheets\\{id}\\"
    
    try:
        os.mkdir(basePath)
    except:
        pass
    
    try:
        with open(f"{basePath}{icon.filename}", "wb") as iconFile:
            iconFile.write(icon.read())
        with open(f"{basePath}{pdf.filename}", "wb") as pdfFile:
            pdfFile.write(pdf.read())
    except:
        return abort(500)
    
    db.session.add(Datasheets(id=id, title=title, subtitle=subtitle, desc=desc, basePath=basePath, imgName=icon.filename, pdfName=pdf.filename))
    db.session.commit()
    return redirect('/')

@app.context_processor
def handle_context():
    return dict(session=session)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969, debug=True)