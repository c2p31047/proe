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
from geopy.geocoders import Nominatim
from geopy.distance import great_circle, geodesic
import re
import logging


logging.basicConfig(level=logging.DEBUG)


geolocator = Nominatim(user_agent="c2p31047@gmail.com")

main = Blueprint('main', __name__)

def get_coordinates(address):
    """住所から緯度経度を取得する関数"""
    geolocator = Nominatim(user_agent="MyAppName (your.email@example.com)")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

def find_nearest_shelter(user_address, shelters):
    """与えられた住所から最寄りの避難所を見つける関数"""
    user_coordinates = get_coordinates(user_address)
    if user_coordinates is None:
        logging.debug(f"Invalid address: {user_address}")
        return None  # 住所が無効な場合

    nearest_shelter = None
    min_distance = float('inf')

    for shelter in shelters:
        shelter_coordinates = (shelter.latitude, shelter.longitude)
        distance = geodesic(user_coordinates, shelter_coordinates).kilometers

        logging.debug(f"Shelter: {shelter.name}, Distance: {distance} km")

        if distance < min_distance:
            min_distance = distance
            nearest_shelter = shelter

    logging.debug(f"Nearest Shelter: {nearest_shelter.name if nearest_shelter else 'None'}")
    return nearest_shelter

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
        # 新しいユーザー情報を取得
        new_username = request.form.get('username')  # ユーザー名
        new_address = request.form.get('address')  # 自宅の住所
        new_work_address = request.form.get('work_address')  # 勤務先の住所
        new_email = request.form.get('email')  # メールアドレス
        new_phonenumber = request.form.get('phonenumber')  # 電話番号
        new_password = request.form.get('password')  # 新しいパスワード
        current_password = request.form.get('current_password')  # 現在のパスワード

        # ユーザー名の更新
        if new_username:
            current_user.name = new_username

        # 電話番号の更新
        if new_phonenumber:
            current_user.phonenumber = new_phonenumber

        # メールアドレスの更新
        if new_email:
            current_user.email = new_email

        # 住所の更新と最寄りの避難所の登録
        if new_address:
            shelters = Shelter.query.all()  # 全ての避難所を取得
            nearest_shelter_home = find_nearest_shelter(new_address, shelters)
            if nearest_shelter_home:
                current_user.shelter_id = nearest_shelter_home.id
                logging.debug(f"Home Shelter ID: {current_user.shelter_id}")
            else:
                logging.debug("住所から近くの避難所が見つからない")

            current_user.address = new_address  # 住所を更新

        # 勤務先の住所の更新と最寄りの避難所の登録
        if new_work_address:
            shelters = Shelter.query.all()  # 全ての避難所を取得
            nearest_shelter_work = find_nearest_shelter(new_work_address, shelters)
            if nearest_shelter_work:
                current_user.work_shelter_id = nearest_shelter_work.id
                logging.debug(f"Work Shelter ID: {current_user.work_shelter_id}")
            else:
                logging.debug("職場の近くから近くの避難所が見つからない")

            current_user.work_address = new_work_address  # 勤務先の住所を更新

        # 新しいパスワードの更新
        if new_password:
            if check_password_hash(current_user.password, current_password):  # 現在のパスワードが正しいか確認
                current_user.password = generate_password_hash(new_password)  # パスワードをハッシュ化して保存
            else:
                flash('現在のパスワードが正しくありません。', 'danger')

        # データベースに変更を保存
        db.session.commit()

        # 更新されたユーザー情報を確認
        updated_user = User.query.get(current_user.id)
        logging.debug(f"Updated User: {updated_user.name}, Shelter ID: {updated_user.shelter_id}")

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
