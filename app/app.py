from flask import Flask
from main import main as main_bp
from admin import admin_bp
from shelter import shelter_bp
from stock import stock_bp

app = Flask(__name__)

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(shelter_bp, url_prefix='/shelter')
app.register_blueprint(stock_bp, url_prefix='/stock')

if __name__ == '__main__':
    app.run(debug=True)
