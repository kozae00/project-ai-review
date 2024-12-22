# AI 리뷰 시스템

## 📖 프로젝트 소개
이 프로젝트는 리뷰 데이터를 분석하여 **감정 상태를 파악**하고, 결과를 **시각화**하여 보여주는 웹 기반 시스템입니다.  
**Azure Text Analytics**와 **BERT 모델**을 활용하여 텍스트의 감정을 분석하고, 사용자에게 요약된 정보를 바탕으로 솔루션 결과를 제공합니다.

---

## 💻 시스템 요구사항
- Python 3.9 이상
- Flask 프레임워크
- **Azure Text Analytics API 키** 필요
- **OpenAI API 키** 필요

---

## 가상환경 생성
```bash
python -m venv myvenv

# 가상환경 활성화
# Windows
myvenv\Scripts\activate
# macOS/Linux
source myvenv/bin/activate
```
## 필요한 패키지 설치
```bash
cd ./backend
pip install -r requirements.txt
```

# 🏃 실행 방법
## 1️⃣ 서버 실행
```bash
cd frontend
python app.py
```
## 2️⃣ 웹 브라우저에서 접속
- 주소: http://127.0.0.1:5000

# 🌟 주요 기능
## ✍️ 리뷰 입력 페이지
- 리뷰 텍스트 입력 시, 자동으로 감정 분석 수행.
## 📊 분석 결과 페이지
- 전체 리뷰의 감정 분포 시각화
- 평균 평점 표시
- 리뷰 요약 및 개선사항 제시
## 🛠️ 관리자 페이지
- 상세 분석 결과 조회
- 리뷰별 감정 분석 데이터 확인
- 키워드 분석 결과 표시
- 단어별 감정 영향도 시각화

# 🔑 관리자 접속 방법
1. /admin/login 페이지 접속
2. 기본 비밀번호: admin123

# 🗂️ 프로젝트 구조
```plaintext
project_root/
├── backend/
│   ├── requirements.txt
│   ├── sentiment_analysis.py
│   └── summarization.py
├── data/
│   └── dummy_data.json
├── frontend/
│   ├── static/
│   │   └── styles.css
│   ├── templates/
│   │   ├── admin_detail.html
│   │   ├── admin_login.html
│   │   ├── admin.html
│   │   ├── input.html
│   │   └── output.html
│   └── app.py
├── .env
├── .gitignore
└── README.md
```

# 🛠️ 문제 해결 가이드

## 1️⃣ 모델 로딩 오류
```bash
pip install --no-cache-dir transformers
```
## 2️⃣ CUDA 관련 오류
- 현재 CPU 모드로 설정됨.
- GPU 사용 시 CUDA 설정 필요.

# ⚠️ 주의사항
- **API 키**는 공개되지 않도록 주의하세요!
- 실제 운영 환경에서는 보안 설정 강화 필수.
- 대량 리뷰 처리 시 **API 사용량**을 고려해야 합니다.