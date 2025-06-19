import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 객체 생성
db = SQLAlchemy()

# CSRF 보호를 위한 객체 생성
csrf = CSRFProtect()

def create_app(config_class=None):
    """
    애플리케이션 팩토리 함수.
    Flask 앱 인스턴스를 생성하고 설정합니다.
    """
    app = Flask(__name__, instance_relative_config=True)

    # --- 설정(Configuration) ---
    # 기본 설정은 config.py에서 로드
    from .config import Config
    app.config.from_object(Config)

    if config_class:
        app.config.from_object(config_class)

    # 환경 변수에서 SECRET_KEY 로드 (config.py보다 우선)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-you-should-change')

    # 인스턴스 폴더가 없으면 생성
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # --- 로깅(Logging) 설정 ---
    if not app.debug and not app.testing:
        # 운영 모드일 때의 로깅 설정
        log_dir = os.path.join(app.instance_path, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'),
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')
    else:
        # 디버그 모드일 때의 로깅 설정 (콘솔에 더 상세히 출력)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info("Application starting in DEBUG mode")

    # --- 확장 기능 초기화(Extension Initialization) ---
    # SQLAlchemy 초기화
    db.init_app(app)

    # CSRF 보호 초기화
    csrf.init_app(app)

    # Flask-Talisman 초기화 (보안 헤더 설정)
    # 개발 환경(app.debug=True)에서는 HTTPS를 강제하지 않음
    Talisman(
        app,
        content_security_policy=None,  # 필요 시 구체적인 CSP 정책 설정
        force_https=not app.debug
    )

    # --- 블루프린트 등록(Blueprint Registration) ---
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

    return app 