import pandas as pd
import chardet
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from app import db
from .models import Shelter, Stock, StockActivity
from werkzeug.utils import secure_filename
from functools import wraps
import re

shelter_bp = Blueprint('shelter', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@shelter_bp.errorhandler(403)
def forbidden_error(error):
    return redirect(url_for('main.index')), 403

@shelter_bp.route('/admin/upload_shelter', methods=['GET', 'POST'])
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
            return redirect(url_for('shelter.manage_shelters'))

    return render_template('upload_shelter.html')

@shelter_bp.route('/admin/add_shelter', methods=['GET', 'POST'])
@admin_required
def add_shelter():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        #altitude = request.form['altitude']

        existing_shelter = Shelter.query.filter_by(name=name).first()
        if existing_shelter:
            flash('この避難所は既に存在します。', 'danger')
            return redirect(url_for('shelter.add_shelter'))

        new_shelter = Shelter(name=name, address=address, latitude=latitude, longitude=longitude, altitude=altitude)
        db.session.add(new_shelter)
        db.session.commit()
        flash('新しい避難所が追加されました', 'success')
        return redirect(url_for('shelter.manage_shelters'))

    return render_template('add_shelter.html')

@shelter_bp.route('/admin/manage_shelters')
@admin_required
def manage_shelters():
    shelters = Shelter.query.all()
    return render_template('manage_shelters.html', shelters=shelters)

@shelter_bp.route('/admin/shelter/edit/<int:shelter_id>', methods=['GET', 'POST'])
@admin_required
def edit_shelter(shelter_id):
    shelter = Shelter.query.get(shelter_id)
    stock = Stock.query.all()
    if request.method == 'POST':
        shelter.name = request.form['name']
        shelter.address = request.form['address']
        shelter.latitude = request.form['latitude']
        shelter.longitude = request.form['longitude']
        #shelter.altitude = request.form['altitude']
        db.session.commit()
        flash('避難所情報が更新されました')
        return redirect(url_for('shelter.manage_shelters'))

    return render_template('edit_shelter.html', shelter=shelter, stock=stock)

@shelter_bp.route('/shelter/<int:shelter_id>')
def shelter_detail(shelter_id):
    shelter = Shelter.query.get_or_404(shelter_id)
    stocks = Stock.query.filter_by(shelter_id=shelter.id).all()
    return render_template('shelter_detail.html', shelter=shelter, stocks=stocks)

@shelter_bp.route('/admin/delete_shelter/<int:shelter_id>', methods=['GET'])
@admin_required
def delete_shelter(shelter_id):
    shelter = Shelter.query.get(shelter_id)
    if shelter:
        db.session.delete(shelter)
        db.session.commit()
        flash('避難所が削除されました')
    return redirect(url_for('shelter.manage_shelters'))