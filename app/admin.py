from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from .models import Admin, AdminShelter, Shelter, User, StockActivity,StockCategory, Stock
from functools import wraps
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.errorhandler(403)
def forbidden_error(error):
    return redirect(url_for('main.index')), 403

@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# 管理者を追加するエンドポイント
@admin_bp.route('/admin/add_admin', methods=['GET', 'POST'])
@admin_required
def add_admin():
    return render_template('add_admin.html')

# メールアドレスから管理者権限をもったユーザーを追加するエンドポイント - 機能のみ
@admin_bp.route('/admin/promote', methods=['POST'])
@admin_required
def promote_user_by_email():
    email = request.form['email']
    user = User.query.filter_by(email=email).first()

    existing_admin = Admin.query.filter_by(email=email).first()
    if existing_admin:
        flash('このメールアドレスは既に登録されています。', 'error')
        return redirect(url_for('admin.add_admin'))

    if user:
        new_admin = Admin(email=user.email, name=user.name, password=user.password)
        db.session.add(new_admin)
        db.session.commit()
        flash('管理者が追加されました.')
    else:
        flash('ユーザーが見つかりません.')
    return redirect(url_for('admin.add_admin'))

# 避難所の編集のエンドポイント
@admin_bp.route('/edit_admin_shelter/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_admin_shelter(id):
    admin_shelter = AdminShelter.query.get_or_404(id)
    if request.method == 'POST':
        admin_shelter.admin_id = request.form['admin_id']
        admin_shelter.shelter_id = request.form['shelter_id']
        try:
            db.session.commit()
            flash('編集が成功しました', 'success')
            return redirect(url_for('admin.admin_shelters'))
        except:
            db.session.rollback()
            flash('編集に失敗しました', 'danger')
    admins = Admin.query.all()
    shelters = Shelter.query.all()
    return render_template('edit_admin_shelter.html', admin_shelter=admin_shelter, admins=admins, shelters=shelters)

# 管理者一覧を表示するエンドポイント
@admin_bp.route('/admin/manage_admins')
@admin_required
def manage_admins():
    admins = Admin.query.all()
    return render_template('manage_admins.html', admins=admins)

# 管理者を編集するエンドポイント
@admin_bp.route('/admin/edit_admin/<int:admin_id>', methods=['GET', 'POST'])
@admin_required
def edit_admin(admin_id):
    admin = Admin.query.get(admin_id)
    if request.method == 'POST':
        admin.name = request.form['name']
        admin.email = request.form['email']
        db.session.commit()
        return redirect(url_for('admin.manage_admins'))
    return render_template('edit_admin.html', admin=admin)

# 管理者権限を削除するエンドポイント
@admin_bp.route('/admin/delete_admin/<int:admin_id>', methods=['GET'])
@admin_required
def delete_admin(admin_id):
    admin = Admin.query.get(admin_id)
    if admin:
        db.session.delete(admin)
        db.session.commit()
    return redirect(url_for('admin.manage_admins'))

#備品の追加
@admin_bp.route('/admin/add_stock', methods=['GET', 'POST'])
@admin_required
def add_stock():

    shelters = Shelter.query.all()
    categories = StockCategory.query.all()

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
            admin_id=current_user.id,
            shelter_id=request.form['shelter_id'],
            stock_id=new_stock.id,
            date=datetime.now(),
            type="追加",
            content=f"{request.form['stockname']} を追加しました"
        )
        db.session.add(stock_activity)
        db.session.commit()

        return redirect(url_for('admin.stock_list'))
    return render_template('add_stock.html', shelters=shelters, categories=categories)

# 在庫の編集する機能のエンドポイント
@admin_bp.route('/admin/edit_stock/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_stock(id):
    shelters = Shelter.query.all()
    stock = Stock.query.get_or_404(id)
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
            admin_id=current_user.id(),
            shelter_id=stock.shelter_id,
            stock_id=stock.id,
            type="編集",
            content=f"{stock.stockname} の情報を更新しました"
        )
        db.session.add(stock_activity)
        db.session.commit()

        return redirect(url_for('stock_list'))
    return render_template('edit_stock.html', stock=stock, shelters=shelters)

# 在庫の削除をするエンドポイント
@admin_bp.route('/admin/delete_stock/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_stock(id):
    stock = Stock.query.get_or_404(id)
    db.session.delete(stock)
    db.session.commit()

    # stock_activityに「削除」した履歴を追加する
    stock_activity = StockActivity(
        admin_id=current_user.id(),
        shelter_id=stock.shelter_id,
        stock_id=stock.id,
        type="削除",
        content=f"{stock.stockname} を削除しました",
        date=datetime.utcnow()
    )
    db.session.add(stock_activity)
    db.session.commit()

    return redirect(url_for('admin.stock_list'))

# 使用履歴の表示 - 現在は使っていない
@admin_bp.route('/admin/activity_stock/<int:stock_id>')
def stock_activity(stock_id):
    activities = StockActivity.query.filter_by(stock_id=stock_id).all()
    return render_template('stock_activity.html', activities=activities)

# 備品一覧の表示 - 現在は使っていない
@admin_bp.route('/admin/stock_list')
def stock_list():
    shelters = Shelter.query.all()
    stocks = Stock.query.all()
    return render_template('list_stock.html', stocks=stocks, shelters=shelters)


@admin_bp.route('/admin/list_category', methods=['GET'])
def list_category():
    categories = StockCategory.query.all()
    return render_template('list_category.html', categories=categories)

@admin_bp.route('/admin/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category_name = request.form['category']
        other_info = request.form['other']

        existing_category = StockCategory.query.filter_by(category=category_name).first()
        if existing_category:
            flash('このカテゴリはすでに存在します。', 'error')
            return redirect(url_for('admin.add_category'))

        new_category = StockCategory(category=category_name, other=other_info)
        db.session.add(new_category)
        db.session.commit()

        flash('新しいカテゴリが追加されました。', 'success')
        return redirect(url_for('admin.list_category'))

    return render_template('add_category.html')

@admin_bp.route('/admin/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = StockCategory.query.get_or_404(id)

    if request.method == 'POST':
        category.category = request.form['category']
        category.other = request.form['other']
        db.session.commit()

        flash('カテゴリが更新されました。', 'success')
        return redirect(url_for('admin.list_category'))

    return render_template('edit_category.html', category=category)

@admin_bp.route('/admin/delete_category/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_category(id):
    category = StockCategory.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('カテゴリが削除されました。', 'success')
    return redirect(url_for('admin.list_category'))