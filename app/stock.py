from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from .models import User, Shelter, Stock, StockActivity, StockCategory
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

        return redirect(url_for('stock.stock_list'))
    return render_template('edit_stock.html', stock=stock, shelters=shelters)

# 在庫の削除
@stock_bp.route('/admin/delete_stock/<int:id>', methods=['POST'])
@admin_required
def delete_stock(id):
    stock = Stock.query.get_or_404(id)
    db.session.delete(stock)
    db.session.commit()

    # 使用履歴に「削除」イベントを記録
    stock_activity = StockActivity(
        admin_id=1,  # 管理者のID
        shelter_id=stock.shelter_id,
        stock_id=stock.id,
        type="削除",
        content=f"{stock.stockname} を削除しました"
    )
    db.session.add(stock_activity)
    db.session.commit()

    return redirect(url_for('stock_list'))

# 使用履歴の表示
@stock_bp.route('/admin/activity_stock/<int:stock_id>')
def stock_activity(stock_id):
    activities = StockActivity.query.filter_by(stock_id=stock_id).all()
    return render_template('stock_activity.html', activities=activities)

@stock_bp.route('/admin/stock_list')
def stock_list():
    stocks = Stock.query.all()
    return render_template('list_stock.html', stocks=stocks)