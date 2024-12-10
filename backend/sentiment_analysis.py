from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self, azure_key, azure_endpoint):
        self.azure_client = TextAnalyticsClient(
            endpoint=azure_endpoint,
            credential=AzureKeyCredential(azure_key)
        )
        self.hf_analyzer = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )

    def analyze_sentiment(self, text):
        # Azure 감정 분석
        azure_response = self.azure_client.analyze_sentiment(documents=[text])[0]
        azure_sentiment = azure_response.sentiment
        azure_score_map = {'positive': 1, 'neutral': 0, 'negative': -1}
        azure_score = azure_score_map.get(azure_sentiment, 0)

        # Hugging Face 감정 분석
        hf_result = self.hf_analyzer(text)[0]
        hf_label = hf_result['label']
        if '1' in hf_label or '2' in hf_label:
            hf_sentiment = 'negative'
            hf_score = -1
        elif '3' in hf_label:
            hf_sentiment = 'neutral'
            hf_score = 0
        else:
            hf_sentiment = 'positive'
            hf_score = 1

        # 앙상블 결과 계산 (6:4 비율)
        final_score = (azure_score * 0.6) + (hf_score * 0.4)
        if final_score > 0.2:
            final_sentiment = 'positive'
        elif final_score < -0.2:
            final_sentiment = 'negative'
        else:
            final_sentiment = 'neutral'

        # 상세한 결과 반환
        return {
            'final_sentiment': final_sentiment,
            'azure': {
                'sentiment': azure_sentiment,
                'confidence_scores': azure_response.confidence_scores,
                'key_phrases': self.extract_key_phrases(text)
            },
            'huggingface': {
                'sentiment': hf_sentiment,
                'label': hf_label,
                'score': hf_result['score']
            }
        }

    def extract_key_phrases(self, text):
        # Azure 키워드 추출
        key_phrase_response = self.azure_client.extract_key_phrases(documents=[text])[0]
        if not key_phrase_response.is_error:
            return key_phrase_response.key_phrases
        else:
            return []
        
    # sentiment_analysis.py에 추가
    def analyze_word_importance(self, text):
        words = text.split()
        word_importance = []
        
        # 기본 전체 문장 분석
        base_result = self.analyze_sentiment(text)
        base_positive = base_result['azure']['confidence_scores'].positive
        base_negative = base_result['azure']['confidence_scores'].negative
        base_score = base_positive - base_negative
        
        max_impact = 0  # 최대 영향도 추적을 위한 변수
        raw_impacts = []  # 정규화 전 영향도 저장
        
        # 각 단어별 영향도 계산
        for word in words:
            temp_text = ' '.join(w for w in words if w != word)
            
            if temp_text.strip():
                temp_result = self.analyze_sentiment(temp_text)
                temp_positive = temp_result['azure']['confidence_scores'].positive
                temp_negative = temp_result['azure']['confidence_scores'].negative
                temp_score = temp_positive - temp_negative
                
                impact = base_score - temp_score
                raw_impacts.append({'word': word, 'impact': impact})
                max_impact = max(max_impact, abs(impact))
            else:
                raw_impacts.append({'word': word, 'impact': 0})
        
        # 영향도 정규화 (-1 ~ 1 범위로)
        if max_impact > 0:
            for impact_data in raw_impacts:
                normalized_impact = impact_data['impact'] / max_impact
                word_importance.append({
                    'word': impact_data['word'],
                    'normalized_impact': normalized_impact
                })
        else:
            word_importance = [{'word': w, 'normalized_impact': 0} for w in words]
        
        return word_importance