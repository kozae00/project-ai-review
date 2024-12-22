from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import sys
import numpy as np
from dotenv import load_dotenv

# 현재 파일의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# backend 모듈 경로 추가
backend_dir = os.path.abspath(os.path.join(current_dir, '../backend'))
sys.path.append(backend_dir)

from sentiment_analysis import SentimentAnalyzer
from summarization import Summarizer

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션을 사용하기 위한 시크릿 키 설정

# .env 파일 로드
load_dotenv()

# API 키 설정
AZURE_KEY = os.getenv('AZURE_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# SentimentAnalyzer 및 Summarizer 초기화
sentiment_analyzer = SentimentAnalyzer(AZURE_KEY, AZURE_ENDPOINT)
summarizer = Summarizer(OPENAI_API_KEY)

# 데이터 로드
data_file_path = os.path.abspath(os.path.join(current_dir, '../data/dummy_data.json'))

def load_data():
    with open(data_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(data_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

@app.template_filter('abs')
def abs_filter(number):
    return abs(number)

@app.route('/', methods=['GET', 'POST'])
def input_data():
    if request.method == 'POST':
        new_text = request.form['text']
        sentiment_result = sentiment_analyzer.analyze_sentiment(new_text)
        final_sentiment = sentiment_result['final_sentiment']
        data = load_data()
        new_entry = {
            "id": len(data) + 1,
            "text": new_text,
            "sentiment": final_sentiment
        }
        data.append(new_entry)
        save_data(data)
        return redirect(url_for('output_data'))
    return render_template('input.html')

@app.route('/output')
def output_data():
    data = load_data()
    total_reviews = len(data)
    positive_count = sum(1 for entry in data if entry['sentiment'] == 'positive')
    neutral_count = sum(1 for entry in data if entry['sentiment'] == 'neutral')
    negative_count = sum(1 for entry in data if entry['sentiment'] == 'negative')

    # 평점 계산
    score_map = {'positive': 5, 'neutral': 3, 'negative': 1}
    scores = [score_map.get(entry['sentiment'], 3) for entry in data]
    average_score = round(sum(scores) / len(scores) * 2) / 2  # 0.5 단위로 반올림

    # 요약 및 해결책 생성
    summary = summarizer.summarize([entry['text'] for entry in data])
    solution = summarizer.get_negative_feedback_solution(data)

    return render_template(
        'output.html',
        total_reviews=total_reviews,
        positive_count=positive_count,
        neutral_count=neutral_count,
        negative_count=negative_count,
        average_score=average_score,
        summary=summary,
        solution=solution
    )

@app.route('/admin')
def admin_page():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    data = load_data()
    detailed_results = []
    for entry in data:
        text = entry['text']
        sentiment_result = sentiment_analyzer.analyze_sentiment(text)
        detailed_results.append({
            'id': entry['id'],
            'text': text,
            'final_sentiment': sentiment_result['final_sentiment'],
            'azure_sentiment': sentiment_result['azure']['sentiment'],
            'azure_confidence_scores': sentiment_result['azure']['confidence_scores'],
            'azure_key_phrases': sentiment_result['azure']['key_phrases'],
            'hf_sentiment': sentiment_result['huggingface']['sentiment'],
            'hf_label': sentiment_result['huggingface']['label'],
            'hf_score': sentiment_result['huggingface']['score']
        })
    
    return render_template('admin.html', detailed_results=detailed_results)

@app.route('/admin/detail/<int:review_id>')
def admin_detail(review_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    data = load_data()
    review = next((r for r in data if r['id'] == review_id), None)
    if not review:
        return redirect(url_for('admin_page'))
    
    text = review['text']
    sentiment_result = sentiment_analyzer.analyze_sentiment(text)
    word_importance = sentiment_analyzer.analyze_word_importance(text)
    
    result = {
        'id': review_id,
        'text': text,
        'word_importance': word_importance,
        'final_sentiment': sentiment_result['final_sentiment'],
        'azure_sentiment': sentiment_result['azure']['sentiment'],
        'azure_confidence_scores': sentiment_result['azure']['confidence_scores'],
        'azure_key_phrases': sentiment_result['azure']['key_phrases'],
        'hf_sentiment': sentiment_result['huggingface']['sentiment'],
        'hf_label': sentiment_result['huggingface']['label'],
        'hf_score': sentiment_result['huggingface']['score']
    }
    
    return render_template('admin_detail.html', result=result)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':  # 간단한 패스워드 인증
            session['is_admin'] = True
            return redirect(url_for('admin_page'))
    return render_template('admin_login.html')

if __name__ == '__main__':
    app.run(debug=True)