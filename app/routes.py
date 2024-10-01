import pandas as pd
import chardet
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from forms import LoginForm, RegisterForm
from .models import User, Shelter, Admin
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

main = Blueprint('main', __name__)

@main.route('/')
def index():
    shelters = Shelter.query.all() 
    shelters_dict = [shelter.to_dict() for shelter in shelters]
    return render_template('index.html', shelters=shelters_dict)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('ログインに失敗しました。', 'danger')
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        address = form.address.data
        phonenumber = form.phonenumber.data
        password = generate_password_hash(form.password.data)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('このメールアドレスはすでに登録されています。', 'danger')
            return redirect(url_for('main.register'))
        new_user = User(name=name, email=email, address=address, phonenumber=phonenumber, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('ユーザー登録が完了しました。')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

import re

@main.route('/admin/upload_shelter', methods=['GET', 'POST'])
def upload_shelter():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません。')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('ファイル名がありません。')
            return redirect(request.url)
        if file:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filepath)

            try:
                # エンコード自動検出
                with open(filepath, 'rb') as f:
                    raw = f.read()
                    result = chardet.detect(raw)
                    encoding = result['encoding']

                df = pd.read_csv(filepath, encoding=encoding)
                df.columns = df.columns.str.replace('\n', '')

                # データベースに書き込む
                for _, row in df.iterrows():
                    # すでに登録されている避難所を除外
                    existing_shelter = Shelter.query.filter_by(name=row['名称']).first()
                    if existing_shelter is None:
                        # 収容人数を整数に変換
                        capacity_str = row['想定収容人数']
                        capacity = None
                        if isinstance(capacity_str, str):
                            # 人数の部分のみ抽出
                            match = re.search(r'(\d{1,3}(?:,\d{3})*)', capacity_str)
                            if match:
                                # カンマを削除して整数に変換
                                digits = match.group(0).replace(',', '')
                                capacity = int(digits)

                        shelter = Shelter(
                            name=row['名称'],
                            address=row['住所'],
                            latitude=row['緯度'],
                            longitude=row['経度'],
                            capacity=capacity,
                            hightide=row.get('災害種別_高潮', False),
                            earthquake=row.get('災害種別_地震', False),
                            tsunami=row.get('災害種別_津波', False),
                            inland_flooding=row.get('災害種別_内水氾濫', False),
                            volcano=row.get('災害種別_火山現象', False),
                            landslide=row.get('災害種別_崖崩れ、土石流及び地滑り', False),
                            flood=row.get('災害種別_洪水', False)
                        )
                        db.session.add(shelter)

                db.session.commit()
                flash('ファイルが正常にアップロードされ、データが保存されました。')
            except Exception as e:
                db.session.rollback()
                flash(f'エラーが発生しました: {str(e)}')
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
            return redirect(url_for('main.manage_shelters'))

    return render_template('upload_shelter.html')




def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@main.errorhandler(403)
def forbidden_error(error):
    return render_template('index.html'), 403

@main.route('/admin/add_admin', methods=['GET', 'POST'])
@admin_required
def add_admin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_admin = Admin(name=name, email=email, password=password)
        db.session.add(new_admin)
        db.session.commit()
        flash('新しい管理者が追加されました')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('add_admin.html')

@main.route('/admin/add_shelter', methods=['GET', 'POST'])
@admin_required
def add_shelter():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        altitude = request.form['altitude']

        existing_shelter = Shelter.query.filter_by(name=name).first()
        if existing_shelter:
            flash('この避難所は既に存在します。', 'danger')
            return redirect(url_for('main.add_shelter'))

        new_shelter = Shelter(name=name, address=address, latitude=latitude, longitude=longitude, altitude=altitude)
        db.session.add(new_shelter)
        db.session.commit()
        flash('新しい避難所が追加されました', 'success')
        return redirect(url_for('main.manage_shelters'))

    return render_template('add_shelter.html')


@main.route('/admin/shelter')
@admin_required
def manage_shelters():
    shelters = Shelter.query.all()
    return render_template('manage_shelters.html', shelters=shelters)

@main.route('/admin/shelter/edit/<int:shelter_id>', methods=['GET', 'POST'])
@admin_required
def edit_shelter(shelter_id):
    shelter = Shelter.query.get(shelter_id)
    if request.method == 'POST':
        shelter.name = request.form['name']
        shelter.address = request.form['address']
        shelter.latitude = request.form['latitude']
        shelter.longitude = request.form['longitude']
        shelter.altitude = request.form['altitude']
        db.session.commit()
        flash('避難所情報が更新されました')
        return redirect(url_for('main.manage_shelters'))

    return render_template('edit_shelter.html', shelter=shelter)

@main.route('/admin/delete_shelter/<int:shelter_id>', methods=['GET'])
@admin_required
def delete_shelter(shelter_id):
    shelter = Shelter.query.get(shelter_id)
    if shelter:
        db.session.delete(shelter)
        db.session.commit()
        flash('避難所が削除されました')
    return redirect(url_for('main.manage_shelters'))

@main.route('/admin/manage_admins')
@admin_required
def manage_admins():
    admins = Admin.query.all()
    return render_template('manage_admins.html', admins=admins)

@main.route('/admin/edit_admin/<int:admin_id>', methods=['GET', 'POST'])
@admin_required
def edit_admin(admin_id):
    admin = Admin.query.get(admin_id)
    if request.method == 'POST':
        admin.name = request.form['name']
        admin.email = request.form['email']
        db.session.commit()
        return redirect(url_for('main.manage_admins'))
    return render_template('edit_admin.html', admin=admin)

@main.route('/admin/delete_admin/<int:admin_id>', methods=['GET'])
@admin_required
def delete_admin(admin_id):
    admin = Admin.query.get(admin_id)
    if admin:
        db.session.delete(admin)
        db.session.commit()
    return redirect(url_for('main.manage_admins'))

@main.route('/admin/promote', methods=['POST'])
@admin_required
def promote_user_by_email():
    email = request.form['email']
    user = User.query.filter_by(email=email).first()

    existing_admin = Admin.query.filter_by(email=email).first()
    if existing_admin:
        flash('このメールアドレスは既に登録されています。', 'error')
        return redirect(url_for('main.add_admin'))

    if user:
        new_admin = Admin(email=user.email, name=user.name, password=user.password)
        db.session.add(new_admin)
        db.session.commit()
        flash('管理者が追加されました.')
    else:
        flash('ユーザーが見つかりません.')
    return redirect(url_for('main.add_admin'))

@main.route('/shelter/<int:shelter_id>')
def shelter_detail(shelter_id):
    shelter = Shelter.query.get_or_404(shelter_id)  # IDに基づいて避難所を取得
    return render_template('shelter_detail.html', shelter=shelter)

