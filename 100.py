import os
import requests
import google.generativeai as genai
from datetime import datetime
import pytz
from git import Repo

# 1. 설정 정보
GEMINI_API_KEY = "AIzaSyC1PzzxctuWbKD54MUW_tWEQwCPaAru5bo"
WEATHER_API_KEY = "adeeeb980a9437a95a54669f42cba2261e47b2d01292a58792886d36b0c0f5f8"
WEATHER_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
REPO_PATH = os.getcwd()

def get_realtime_weather():
    """기상청 API 실시간 조회"""
    try:
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        base_date = now.strftime("%Y%m%d")
        base_time = now.strftime("%H00") if now.minute >= 40 else f"{now.hour-1:02d}00"

        params = {
            'serviceKey': WEATHER_API_KEY,
            'pageNo': '1', 'numOfRows': '1000', 'dataType': 'JSON',
            'base_date': base_date, 'base_time': base_time,
            'nx': '55', 'ny': '127'
        }
        res = requests.get(WEATHER_URL, params=params, timeout=10).json()
        items = res['response']['body']['items']['item']
        
        weather_info = []
        for i in items:
            if i['category'] == 'T1H': weather_info.append(f"기온 {i['obsrValue']}°C")
            if i['category'] == 'RN1': weather_info.append(f"강수량 {i['obsrValue']}mm")
        
        return ", ".join(weather_info) if weather_info else "맑음"
    except:
        return "날씨 정보 호출 실패"

def run_music_ai():
    """메인 실행 함수"""
    print("\n🚀 프로그램을 시작합니다. 잠시만 기다려주세요...")
    
    # Gemini 설정 (최신 모델명 적용)
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
    
    # 정보 획득
    kst = pytz.timezone('Asia/Seoul')
    time_now = datetime.now(kst)
    time_str = time_now.strftime("%Y-%m-%d %H:%M:%S")
    weather = get_realtime_weather()
    
    # AI 추천 요청
    prompt = f"""
    현재 한국 시간 {time_str}, 실시간 날씨 데이터 {weather}입니다.
    이 상황에 어울리는 노래 3곡을 추천해줘.
    형식: - [아티스트] 노래제목 : 추천 이유
    """
    
    try:
        response = model.generate_content(prompt)
        recommendation = response.text
        
        # --- 시각화 출력 (UI) ---
        print("\n" + "═"*60)
        print(" 🎵  AI 실시간 음악 큐레이션 서비스 ".center(54))
        print("═"*60)
        print(f" 🕒  분석 시간 : {time_str}")
        print(f" 🌤️  현재 날씨 : {weather}")
        print("-" * 60)
        print(f" ✨  Gemini의 오늘의 추천곡")
        print(recommendation.strip())
        print("-" * 60)
        
        # Git 기록
        log_file = "music_history.txt"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- {time_str} ---\n{recommendation}\n")
        
        try:
            repo = Repo(REPO_PATH)
            repo.git.add(log_file)
            repo.index.commit(f"Music recommend: {time_str}")
            print(" ✅  로그가 Git 레파지토리에 성공적으로 기록되었습니다.")
        except:
            print(" ⚠️  Git 기록 실패 (폴더 내 .git 존재 여부를 확인하세요)")
            
        print("═"*60 + "\n")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

# 프로그램 시작점 (이 부분이 정확해야 실행됩니다)
if __name__ == "__main__":
    run_music_ai()