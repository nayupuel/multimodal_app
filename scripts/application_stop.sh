#!/bin/bash
echo "Running ApplicationStop hook..."

# Gunicorn 서비스 중지
sudo systemctl stop multimodal_app || true

# Nginx 서비스 중지 (필요하다면)
# sudo systemctl stop nginx || true
echo "ApplicationStop hook completed."