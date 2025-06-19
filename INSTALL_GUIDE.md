# AWS EC2 배포 가이드 (Amazon Linux 2)

이 문서는 `multimodal_app` 프로젝트를 AWS EC2 (Amazon Linux 2) 환경에 배포하는 과정을 안내합니다. 웹 서버는 Nginx, WSGI 서버는 Gunicorn을 사용합니다.

---

### 사전 준비: `requirements.txt`

배포를 시작하기 전, `backend/requirements.txt` 파일에 다음 패키지들이 포함되어 있는지 확인합니다.

```
Flask
Flask-SQLAlchemy
Werkzeug
gunicorn
python-dotenv
```

---

### 1단계: EC2 인스턴스 생성 및 연결

1.  **EC2 인스턴스 시작**
    - **AWS Management Console** > **EC2** > **인스턴스 시작**으로 이동합니다.
    - **AMI:** `Amazon Linux 2 AMI` 선택 (Free-tier)
    - **인스턴스 유형:** `t2.micro` 선택 (Free-tier)
    - **키 페어:** 기존 키 페어를 선택하거나 새로 생성 후 `.pem` 파일을 다운로드합니다.

2.  **네트워크 설정**
    - **보안 그룹**에서 다음 인바운드 규칙을 추가합니다.
      - **SSH (포트 22):** 소스를 `내 IP`로 설정하여 보안을 강화합니다.
      - **HTTP (포트 80):** 소스를 `Anywhere` (0.0.0.0/0)로 설정합니다.
      - **HTTPS (포트 443):** 소스를 `Anywhere` (0.0.0.0/0)로 설정합니다.

3.  **EC2 인스턴스 접속**
    - 인스턴스 생성이 완료되면 **퍼블릭 IPv4 주소**를 복사합니다.
    - 로컬 터미널에서 아래 명령어를 실행하여 서버에 접속합니다.
      ```bash
      # 1. 키 파일 권한 변경 (최초 한 번만)
      chmod 400 /path/to/your-key.pem

      # 2. SSH 접속 (사용자: ec2-user)
      ssh -i /path/to/your-key.pem ec2-user@<EC2_PUBLIC_IP_ADDRESS>
      ```

---

### 2단계: 서버 기본 환경 설정

EC2 인스턴스에 접속한 상태에서 아래 명령어를 실행합니다.

1.  **패키지 업데이트:**
    ```bash
    sudo yum update -y
    ```
2.  **개발 도구 및 필수 패키지 설치:**
    ```bash
    sudo yum groupinstall "Development Tools" -y
    sudo yum install python3-devel nginx git -y
    ```

---

### 3단계: 애플리케이션 코드 배포

1.  **Git으로 소스 코드 클론:**
    ```bash
    git clone <YOUR_GIT_REPOSITORY_URL>
    ```
2.  **(대안) SCP로 코드 전송:**
    로컬 터미널에서 아래 명령어로 프로젝트 폴더 전체를 EC2에 복사합니다.
    ```bash
    scp -i /path/to/your-key.pem -r /local/path/to/multimodal_app ec2-user@<EC2_PUBLIC_IP_ADDRESS>:~/
    ```

---

### 4단계: Python 가상환경 설정

1.  프로젝트의 `backend` 디렉토리로 이동합니다.
    ```bash
    cd multimodal_app/backend
    ```
2.  가상환경을 생성하고 활성화합니다.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  `requirements.txt` 파일의 의존성을 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

---

### 5단계: Gunicorn Systemd 서비스 등록

애플리케이션을 백그라운드에서 안정적으로 실행하기 위해 Gunicorn을 Systemd 서비스로 등록합니다.

1.  **Systemd 서비스 파일 생성:**
    ```bash
    sudo nano /etc/systemd/system/multimodal_app.service
    ```
2.  열린 편집기에 아래 내용을 붙여넣습니다. (경로가 올바른지 확인)
    ```ini
    [Unit]
    Description=Gunicorn instance to serve multimodal_app
    After=network.target

    [Service]
    User=ec2-user
    Group=nginx
    WorkingDirectory=/home/ec2-user/multimodal_app/backend
    Environment="PATH=/home/ec2-user/multimodal_app/backend/venv/bin"
    ExecStart=/home/ec2-user/multimodal_app/backend/venv/bin/gunicorn --workers 3 --bind unix:multimodal_app.sock -m 007 run:app

    [Install]
    WantedBy=multi-user.target
    ```
3.  **서비스 시작 및 활성화:**
    ```bash
    sudo systemctl start multimodal_app
    sudo systemctl enable multimodal_app
    ```

---

### 6단계: Nginx 리버스 프록시 설정

외부(HTTP/80) 요청을 내부 Gunicorn 소켓으로 전달하도록 Nginx를 설정합니다.

1.  **Nginx 설정 파일 생성:**
    ```bash
    sudo nano /etc/nginx/conf.d/multimodal_app.conf
    ```
2.  열린 편집기에 아래 내용을 붙여넣습니다. `server_name`은 EC2의 퍼블릭 IP 주소로 변경합니다.
    ```nginx
    server {
        listen 80;
        server_name <EC2_PUBLIC_IP_ADDRESS>;

        location / {
            include proxy_params;
            proxy_pass http://unix:/home/ec2-user/multimodal_app/backend/multimodal_app.sock;
        }

        location /static {
            alias /home/ec2-user/multimodal_app/backend/app/static;
        }
    }
    ```
3.  **Nginx 재시작:**
    ```bash
    sudo nginx -t  # 문법 검사
    sudo systemctl restart nginx
    ```

---

### 7단계: 배포 확인 및 트러블슈팅

1.  **웹 브라우저 확인:**
    - 주소창에 `http://<EC2_PUBLIC_IP_ADDRESS>`를 입력하여 애플리케이션이 정상적으로 표시되는지 확인합니다.

2.  **오류 발생 시 로그 확인:**
    - **Gunicorn 로그:** `sudo journalctl -u multimodal_app`
    - **Nginx 에러 로그:** `tail -f /var/log/nginx/error.log`

---
이것으로 배포가 완료되었습니다. 이후 도메인 연결 및 HTTPS(SSL) 설정을 추가로 진행할 수 있습니다. 