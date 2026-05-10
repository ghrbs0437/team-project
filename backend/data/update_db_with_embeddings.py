import json
from pathlib import Path
import sys

# 백엔드 루트 디렉토리를 Python Path에 추가하여 app 모듈을 임포트할 수 있게 합니다.
backend_root = Path(__file__).parent.parent
sys.path.append(str(backend_root))

from app.core.database import SessionLocal, create_database_tables
from app.crawled_profiles.models import CrawledProfile

def main():
    # 데이터베이스 테이블 및 컬럼 업데이트 (새 컬럼 자동 추가)
    print("데이터베이스 스키마 확인 중...")
    create_database_tables()
    
    data_dir = Path(__file__).parent
    input_file = data_dir / "embedded_data.json"

    if not input_file.exists():
        print(f"입력 파일을 찾을 수 없습니다: {input_file}")
        return

    print("임베딩 데이터 로딩 중...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("데이터베이스 업데이트 시작...")
    db = SessionLocal()
    
    updated_count = 0
    not_found_count = 0
    
    try:
        for title, info in data.items():
            embedding = info.get("embedded_data")
            
            # 임베딩 데이터가 정상적으로 존재하는 경우만 처리
            if not embedding or len(embedding) == 0:
                continue

            update_data = {"embedded_data": embedding}
            source_url = info.get("source_url")
            if source_url:
                update_data["source_url"] = source_url

            # DB에서 title이 일치하는 모든 레코드 업데이트
            result = db.query(CrawledProfile).filter(
                CrawledProfile.title == title
            ).update(
                update_data,
                synchronize_session=False
            )
            
            if result > 0:
                updated_count += result
            else:
                not_found_count += 1
                print(f"DB에서 찾을 수 없음 (업데이트 스킵됨): {title}")
                
        db.commit()
        print(f"\n업데이트 완료! 총 {updated_count}개의 레코드에 임베딩 데이터가 삽입되었습니다.")
        if not_found_count > 0:
            print(f"매칭되지 않은 타이틀 수: {not_found_count}개")
            
    except Exception as e:
        db.rollback()
        print(f"업데이트 중 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
