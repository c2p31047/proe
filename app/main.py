import pandas as pd
import chardet
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from forms import LoginForm, RegisterForm
from .models import User, Shelter
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

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
        address = form.address.data if form.address.data else None
        phonenumber = form.phonenumber.data if form.phonenumber.data else None
        password = generate_password_hash(form.password.data)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('このメールアドレスはすでに登録されています。', 'danger')
            return redirect(url_for('main.register'))
        new_user = User(name=name, email=email, address=address, phonenumber=phonenumber, password=password)
        try:
            with current_app.app_context():
                db.session.add(new_user)
                db.session.commit()
            flash('ユーザー登録が完了しました。', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('ユーザー登録中にエラーが発生しました。', 'danger')
            print(e)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}にエラーがあります: {error}", 'danger')
    return render_template('register.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_username = request.form.get('username')
        new_address = request.form.get('address')
        new_work_address = request.form.get('work_address')
        new_email = request.form.get('email')
        new_phonenumber = request.form.get('phonenumber')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 現在のパスワードが正しいかチェック
        if not current_password:
            flash('現在のパスワードを入力してください', 'danger')
            return redirect(url_for('main.settings'))
        elif not check_password_hash(current_user.password, current_password):
            flash('現在のパスワードが正しくありません', 'danger')
            return redirect(url_for('main.settings'))

        # パスワードの確認（新しいパスワードが一致するか）
        if new_password and new_password != confirm_password:
            flash('新しいパスワードが一致しません', 'danger')
            return redirect(url_for('main.settings'))

        # ユーザー名とメールアドレスのバリデーション
        if not new_username:
            flash('ユーザー名を入力してください', 'danger')
            return redirect(url_for('main.settings'))
        if not new_email:
            flash('メールアドレスを入力してください', 'danger')
            return redirect(url_for('main.settings'))


        # メールアドレスが他のユーザーと重複していないか確認
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('このメールアドレスは既に他のユーザーに使用されています', 'danger')
            return redirect(url_for('main.settings'))

        # ユーザー情報の更新
        current_user.name = new_username
        current_user.address = new_address
        current_user.work_address = new_work_address
        current_user.email = new_email
        current_user.phonenumber = new_phonenumber

        # 新しいパスワードが設定された場合のみパスワードを変更
        if new_password:
            current_user.password = generate_password_hash(new_password)

        # データベースに変更を保存
        db.session.commit()
        flash('設定が更新されました', 'success')
        return redirect(url_for('main.index'))

    return render_template('settings.html')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main.errorhandler(403)
def forbidden_error(error):
    return render_template('index.html'), 403
