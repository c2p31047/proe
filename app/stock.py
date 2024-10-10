from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from .models import User, Shelter, Stock, StockActivity, StockCategory, Admin
from datetime import datetime
from functools import wraps

stock_bp = Blueprint('stock', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# 在庫の編集
@stock_bp.route('/admin/edit_stock/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_stock(id):
    shelters = Shelter.query.all()
    stock = Stock.query.get_or_404(id)

    admin = Admin.query.filter_by(email=current_user.email).first()
    if admin is None:
        flash('管理者が見つかりません。', 'error')
        return redirect(url_for('stock.stock_list'))

    if request.method == 'POST':
        stock.stockname = request.form['stockname']
        stock.quantity = request.form['quantity']
        stock.unit = request.form['unit']
        stock.location = request.form['location']
        stock.note = request.form['note']
        stock.expiration = datetime.strptime(request.form['expiration'], '%Y-%m-%d')
        stock.condition = request.form['condition']

        db.session.commit()

        # 使用履歴に「編集」した履歴を追加する
        stock_activity = StockActivity(
            admin_id=admin.id,
            shelter_id=stock.shelter_id,
            stock_id=stock.id,
            date=datetime.now(),
            type="編集",
            content=f"{stock.stockname} の情報を更新しました"
        )
        db.session.add(stock_activity)
        db.session.commit()

        return redirect(url_for('stock.stock_list'))
    return render_template('edit_stock.html', stock=stock, shelters=shelters)

#備品の追加
@stock_bp.route('/admin/add_stock', methods=['GET', 'POST'])
@admin_required
def add_stock():

    shelters = Shelter.query.filter((Shelter.other == None) | (Shelter.other == '')).all()
    categories = StockCategory.query.all()
    
    admin = Admin.query.filter_by(email=current_user.email).first()
    if admin is None:
        flash('管理者が見つかりません。', 'error')
        return redirect(url_for('stock.stock_list'))

    if request.method == 'POST':
        new_stock = Stock(
            shelter_id=request.form['shelter_id'],
            category_id=request.form['category_id'],
            stockname=request.form['stockname'],
            quantity=request.form['quantity'],
            unit=request.form['unit'],
            location=request.form['location'],
            note=request.form['note'],
            expiration=datetime.strptime(request.form['expiration'], '%Y-%m-%d').date(),
            condition=request.form['condition']
        )
        db.session.add(new_stock)
        db.session.commit()

        # stock_activityに「追加」した履歴を追加する
        stock_activity = StockActivity(
            admin_id=admin.id,
            shelter_id=request.form['shelter_id'],
            stock_id=new_stock.id,
            date=datetime.now(),
            type="追加",
            content=f"{request.form['stockname']} を追加しました"
        )
        db.session.add(stock_activity)
        db.session.commit()

        return redirect(url_for('stock.stock_list'))
    return render_template('add_stock.html', shelters=shelters, categories=categories)

# 在庫の削除をするエンドポイント
@stock_bp.route('/admin/delete_stock/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_stock(id):
    stock = Stock.query.get_or_404(id)
    
    admin = Admin.query.filter_by(email=current_user.email).first()
    if admin is None:
        flash('管理者が見つかりません。', 'error')
        return redirect(url_for('stock.stock_list'))
    
    db.session.delete(stock)
    db.session.commit()

    # stock_activityに「削除」した履歴を追加する
    stock_activity = StockActivity(
        admin_id=admin.id,
        shelter_id=stock.shelter_id,
        stock_id=stock.id,
        type="削除",
        content=f"{stock.stockname} を削除しました",
        date=datetime.utcnow()
    )
    db.session.add(stock_activity)
    db.session.commit()

    return redirect(url_for('stock.stock_list'))

# 使用履歴・編集履歴の表示
@stock_bp.route('/admin/activity_stock', methods=['GET', 'POST'])
def activity_stock():
    shelters = Shelter.query.all()
    activities = []
    selected_shelter_name = None  # 選択したシェルター名を保持する変数
    selected_shelter_id = None  # 選択したシェルターIDを保持する変数

    if request.method == 'POST':
        selected_shelter_id = request.form.get('shelter_id')  # 選択されたシェルターIDを取得
        selected_shelter = Shelter.query.get(selected_shelter_id)  # 選択されたシェルターを取得
        if selected_shelter:
            selected_shelter_name = selected_shelter.name  # 選択したシェルターの名前を取得
        # 選択されたシェルターIDでフィルター
        activities = StockActivity.query.filter_by(shelter_id=selected_shelter_id).all()

    return render_template( 
        'stock_activity.html',
        activities=activities,
        shelters=shelters,
        selected_shelter_name=selected_shelter_name,
        selected_shelter_id=selected_shelter_id
    )




# 備品一覧の表示 - 現在は使っていない
@stock_bp.route('/admin/stock_list')
def stock_list():
    shelters = Shelter.query.all()
    stocks = Stock.query.all()
    return render_template('list_stock.html', stocks=stocks, shelters=shelters)