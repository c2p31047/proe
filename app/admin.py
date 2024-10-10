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