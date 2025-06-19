import os
from dotenv import load_dotenv

# config.py의 위치(multimodal_app/backend/app)를 기준으로
# 상위 디렉토리(multimodal_app/backend)에 있는 .env 파일의 경로를 계산합니다.
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))

# .env 파일이 존재하는지 확인하고 로드합니다.
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"Warning: '.env' file not found at '{dotenv_path}'. Make sure it exists.")


class Config:
    """
    Flask 애플리케이션의 기본 설정을 담는 클래스
    """
    # CSRF 보호와 세션 관리를 위해 SECRET_KEY 설정은 필수입니다.
    # 환경 변수에서 SECRET_KEY를 가져오고, 없으면 기본값을 사용합니다.
    # 운영 환경에서는 반드시 강력하고 안전한 키를 환경 변수로 설정해야 합니다.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-secure-default-secret-key')

    # SQLAlchemy 설정
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')

    # pymysql 드라이버를 사용하는 MariaDB/MySQL 연결 문자열
    # DB 정보가 하나라도 없을 경우를 대비한 방어 코드 추가
    if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            "?charset=utf8mb4"
        )
    else:
        SQLALCHEMY_DATABASE_URI = None # 또는 기본 로컬 DB 경로 지정
    
    # SQLAlchemy가 이벤트를 추적하지 않도록 하여 오버헤드를 줄입니다.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 다른 필요한 설정들을 여기에 추가할 수 있습니다.
    # 예: SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 