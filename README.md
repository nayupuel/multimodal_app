<<<<<<< HEAD
# 콜봇 연동 멀티모달 입력 웹 애플리케이션

## 1. 프로젝트 개요

본 프로젝트는 콜봇의 음성 인터페이스로 처리하기 어려운 민감 정보(주민번호, 계좌번호 등)를 사용자가 웹 화면을 통해 안전하게 입력할 수 있도록 지원하는 멀티모달 웹 애플리케이션입니다.

## 2. 기술 스택

- **백엔드**: Python, Flask
- **프론트엔드**: HTML, CSS, JavaScript
- **서버 환경**: WSGI (Gunicorn 등)

## 3. 디렉토리 구조

```
/multimodal_app
├── backend/
│   ├── app/
│   │   ├── __init__.py         # Flask 애플리케이션 초기화
│   │   ├── routes.py           # API 엔드포인트 및 화면 라우팅 정의
│   │   ├── static/             # CSS, JavaScript, 이미지 등 정적 파일
│   │   └── templates/          # HTML 템플릿 파일
│   ├── run.py                  # Flask 애플리케이션 실행 스크립트
│   ├── requirements.txt        # Python 의존성 패키지 목록
│   └── .env.example            # 환경 변수 예시 파일
├── README.md                   # 프로젝트 설명 및 실행 방법 안내
└── .gitignore                  # Git 버전 관리에서 제외할 파일 목록
```

## 4. 설치 및 실행 방법

### 가. 사전 준비

- Python 3.8 이상
- `pip` 및 `venv`

### 나. 설치 절차

1.  **Git 저장소 복제**
    ```bash
    git clone [저장소 URL]
    cd multimodal_app
    ```

2.  **가상 환경 생성 및 활성화**
    ```bash
    # backend 디렉토리로 이동
    cd backend

    # 가상 환경 생성
    python -m venv venv

    # 가상 환경 활성화 (macOS/Linux)
    source venv/bin/activate
    # 가상 환경 활성화 (Windows)
    # venv\Scripts\activate
    ```

3.  **의존성 패키지 설치**
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수 설정**
    `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 내부에 필요한 환경 변수를 설정합니다.
    ```bash
    cp .env.example .env
    ```

### 다. 애플리케이션 실행

```bash
# backend 디렉토리에서 실행
flask run
```
애플리케이션은 기본적으로 `http://127.0.0.1:5000` 에서 실행됩니다.

## 5. 보안 고려사항

- 모든 민감 정보 전송 구간은 HTTPS를 사용해야 합니다.
- 서버 측 로그에 사용자 민감 정보(주민번호, 비밀번호 등)가 기록되지 않도록 주의합니다.
- CSRF 방어 및 보안 관련 HTTP 헤더가 기본적으로 적용되어 있습니다. 
=======
# multimodal_app
multimodal &amp; python version
>>>>>>> 0234b8bcbebf1e51c4b9808aff602e79c130494d
