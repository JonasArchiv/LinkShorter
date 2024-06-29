from flask import Flask, request, redirect, abort, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'secret_salt'  # Change on Public
db = SQLAlchemy(app)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    custom_short = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    accessed_link = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


if not os.path.exists('instance/db.db'):
    with app.app_context():
        db.create_all()
        print("Datenbank erstellt.")

PASSWORD = 'yourpassword'  # Update with your password


@app.route('/s/')
def create_short_url_second():
    return redirect('/s')


@app.route('/s', methods=['GET', 'POST'])
def create_short_url():
    if request.method == 'POST':
        password = request.form.get('password')
        if password != PASSWORD:
            abort(403)
        original_url = request.form['url']
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'http://' + original_url
        custom_short = request.form.get('short')
        if not custom_short:
            return "Custom short link is required", 400
        link = Link(original_url=original_url, custom_short=custom_short)
        db.session.add(link)
        db.session.commit()
        return f"Short link: {request.url_root}s/{link.custom_short}"
    else:
        return render_template('create_short_url.html')


@app.route('/s/<string:custom_short>')
def redirect_to_url(custom_short):
    link = Link.query.filter_by(custom_short=custom_short).first()
    if link is None:
        abort(404)
    if not link.is_active:
        return "URL wurde deaktiviert", 403

    ip_address = request.remote_addr
    access_log = AccessLog(ip_address=ip_address, accessed_link=custom_short)
    db.session.add(access_log)
    db.session.commit()

    return redirect(link.original_url)


@app.route('/s/list', methods=['GET', 'POST'])
def list_links():
    password = request.args.get('password')
    if password != PASSWORD:
        abort(403)
    if request.method == 'POST':
        link_id = request.form.get('id')
        link = Link.query.get(link_id)
        if link is None:
            abort(404)
        link.original_url = request.form.get('url')
        link.custom_short = request.form.get('short')
        link.is_active = request.form.get('is_active') == 'on'
        db.session.commit()
        return redirect('/s/list?password=' + PASSWORD)
    else:
        links = Link.query.all()
        return render_template('list_short_url.html', links=links)


@app.route('/s/logs')
def view_logs():
    password = request.args.get('password')
    if password != PASSWORD:
        abort(403)
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).all()
    return render_template('short_log.html', logs=logs)


if __name__ == '__main__':
    app.run(debug=True)
