import json
from pathlib import Path

def main():
    data_dir = Path(__file__).parent
    json_file = data_dir / "embedded_data.json"
    txt_file = data_dir / "link_data.txt"

    if not json_file.exists():
        print(f"JSON 파일을 찾을 수 없습니다: {json_file}")
        return
    if not txt_file.exists():
        print(f"텍스트 파일을 찾을 수 없습니다: {txt_file}")
        return

    # JSON 데이터 로드
    with open(json_file, "r", encoding="utf-8") as f:
        embedded_data = json.load(f)

    # 텍스트 파일 라인 로드 (빈 줄 제외)
    with open(txt_file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    json_length = len(embedded_data)
    links_length = len(links)

    print(f"JSON 프로필 개수: {json_length}")
    print(f"텍스트 링크 개수: {links_length}")

    if json_length != links_length:
        print("주의: JSON 데이터 개수와 링크 개수가 일치하지 않습니다!")
        print("순서대로 매핑을 진행하며, 더 적은 쪽의 개수에 맞춥니다.")

    # 순서대로 source_url 추가
    updated_count = 0
    for (title, profile_data), link in zip(embedded_data.items(), links):
        profile_data["source_url"] = link
        updated_count += 1

    # 업데이트된 데이터를 다시 JSON으로 저장
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(embedded_data, f, ensure_ascii=False, indent=2)

    print(f"\n총 {updated_count}개의 프로필에 source_url을 추가하여 저장했습니다.")

if __name__ == "__main__":
    main()
