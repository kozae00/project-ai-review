import openai

class Summarizer:
    def __init__(self, api_key):
        openai.api_key = api_key

    def summarize(self, texts):
        combined_text = "\n".join(texts)
        prompt = (
            "다음 리뷰들을 종합하여 전체적인 평가를 1~2줄로 작성해 주세요. "
            "긍정적인 측면과 부정적인 측면을 균형 있게 포함해 주세요:\n" + combined_text
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5,
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary

    def get_negative_feedback_solution(self, texts):
        # 부정적인 리뷰만 필터링
        negative_texts = [entry['text'] for entry in texts if entry.get('sentiment') == 'negative']
        if not negative_texts:
            return "부정적인 리뷰가 없습니다."

        combined_text = "\n".join(negative_texts)
        prompt = (
            "다음 부정적인 리뷰들을 종합하여 고객들의 주요 불만 사항을 한 문장으로 요약하고, "
            "그에 대한 전반적인 해결책을 두 문장 이내로 제시해 주세요. 불필요한 내용은 생략하고 핵심만 전달해 주세요:\n" + combined_text
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 문제 해결을 돕는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,  # 토큰 수 증가
            temperature=0.3,
        )
        solution = response['choices'][0]['message']['content'].strip()
        return solution
