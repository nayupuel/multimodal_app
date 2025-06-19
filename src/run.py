import os
import sys
from dotenv import load_dotenv

# 프로젝트의 루트 디렉토리를 경로에 추가 (multimodal_app)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- .env 파일 로딩 (절대 경로 지정) ---
# run.py가 있는 디렉토리(backend)에 .env 파일이 있다고 가정
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded .env file from: {dotenv_path}")
else:
    print(f"Warning: .env file not found at {dotenv_path}")

from app import create_app
from app.models import db

# create_app 팩토리 함수를 사용하여 Flask 애플리케이션 인스턴스를 생성
app = create_app()

if __name__ == '__main__':
    # 디버그 모드로 애플리케이션 실행
    # host='0.0.0.0'은 외부에서도 접근 가능하도록 설정
    app.run(host='0.0.0.0', port=5003, debug=True) 