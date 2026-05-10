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

    print("데이터베이스 삽입/업데이트 시작...")
    db = SessionLocal()
    
    inserted_count = 0
    updated_count = 0
    
    try:
        for title, info in data.items():
            raw_text = info.get("raw_text", "")
            embedding = info.get("embedded_data")
            source_url = info.get("source_url")
            
            existing = db.query(CrawledProfile).filter(
                CrawledProfile.title == title
            ).first()

            if existing:
                # Update
                if embedding and len(embedding) > 0:
                    existing.embedded_data = embedding
                if source_url:
                    existing.source_url = source_url
                if raw_text:
                    existing.raw_text = raw_text
                updated_count += 1
            else:
                # Insert
                new_profile = CrawledProfile(
                    source="json-import",
                    external_key=title,
                    source_url=source_url,
                    title=title,
                    raw_text=raw_text,
                    embedded_data=embedding if (embedding and len(embedding) > 0) else None
                )
                db.add(new_profile)
                inserted_count += 1
                
        db.commit()
        print(f"\n작업 완료! 새로 추가됨: {inserted_count}개, 업데이트됨: {updated_count}개")
            
    except Exception as e:
        db.rollback()
        print(f"작업 중 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
