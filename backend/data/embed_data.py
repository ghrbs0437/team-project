import json
import os
import time
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai 패키지가 설치되어 있지 않습니다.")
    print("가상환경(.venv)에서 다음 명령어를 실행해주세요: pip install google-generativeai python-dotenv")
    exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def main():
    # .env 파일 로드 (python-dotenv가 설치되어 있는 경우)
    env_path = Path(__file__).parent.parent / ".env"
    if load_dotenv and env_path.exists():
        load_dotenv(env_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("환경 변수 또는 .env 파일에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
        print(".env 파일에 GEMINI_API_KEY=당신의_api_키 를 추가해주세요.")
        exit(1)

    genai.configure(api_key=api_key)

    data_dir = Path(__file__).parent
    input_file = data_dir / "result_data_cleaned.json"
    output_file = data_dir / "embedded_data.json"

    if not input_file.exists():
        print(f"입력 파일을 찾을 수 없습니다: {input_file}")
        return

    print("데이터 로딩 중...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    embedded_data = {}
    total = len(data)
    print(f"총 {total}개의 프로필을 임베딩합니다.")

    for idx, (name_key, text_list) in enumerate(data.items(), 1):
        print(f"[{idx}/{total}] 임베딩 진행 중: {name_key}")
        
        # 리스트 형태의 텍스트를 하나의 문자열로 결합
        if isinstance(text_list, list):
            combined_text = "\n".join(text_list)
        else:
            combined_text = str(text_list)
            
        try:
            # Gemini Embedding API 호출
            result = genai.embed_content(
                model="gemini-embedding-001",
                content=combined_text,
                task_type="retrieval_document",
            )
            embedding = result['embedding']
        except Exception as e:
            print(f"  -> Error: {name_key} 임베딩 실패 - {e}")
            embedding = []

        # 기존 데이터 구조를 유지하면서 embedded_data 필드 추가
        embedded_data[name_key] = {
            "raw_text": combined_text,
            "embedded_data": embedding
        }
        
        # API Rate limit을 고려한 딜레이 (필요시 조절)
        time.sleep(5)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(embedded_data, f, ensure_ascii=False, indent=2)

    print(f"\n성공적으로 임베딩이 완료되었습니다. 결과가 저장된 경로: {output_file}")


if __name__ == "__main__":
    main()
