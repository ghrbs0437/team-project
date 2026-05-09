# SOMAtching Demo API Specification

## 1. Overview

본 문서는 SOMAtching 1차 데모 기준 API 명세입니다. 현재 백엔드는 크롤링 결과 JSON을 import해 `crawled_profiles` 테이블에 저장하고, 프론트엔드는 저장된 크롤링 프로필을 조회하는 흐름을 기준으로 합니다.

1. `GET /health`: 서버 상태 확인
2. `POST /crawled-profiles/import-json`: 크롤링 결과 JSON import 및 `crawled_profiles` 저장
3. `GET /crawled-profiles`: 저장된 크롤링 프로필 목록 조회
4. `GET /crawled-profiles/{profile_id}`: 저장된 크롤링 프로필 상세 조회
5. `POST /crawled-profiles/convert-to-users`: 크롤링 프로필을 `users` 데이터로 변환

### Base URL

```text
http://localhost:8000
```

### Common Headers

| Header | Required | Type | Description |
| --- | --- | --- | --- |
| `Content-Type` | Request body가 있는 API에서 Yes | String | `application/json` |

### Validation Error Response

FastAPI validation error는 `422 Unprocessable Entity`로 응답합니다.

```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "Input should be greater than or equal to 1",
      "type": "greater_than_equal"
    }
  ]
}
```

## 2. Data Models

### CrawledProfileRead

`crawled_profiles` 테이블에 저장되는 크롤링 결과 모델입니다.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | Number | Yes | 크롤링 프로필 고유 ID |
| `source` | String | Yes | 데이터 출처. 예: `notion`, `json-import` |
| `external_key` | String \| null | No | 외부 데이터 고유 키 |
| `source_url` | String \| null | No | 원본 페이지 URL |
| `title` | String | Yes | 프로필 제목 또는 대표 타이틀 |
| `raw_text` | String | Yes | 원문 또는 정제 전 텍스트 |
| `parsed_json` | Object \| null | No | 구조화 데이터. 태그는 `parsed_json.tags` 기준 |
| `created_at` | String | Yes | 생성일시, ISO 8601 |

### CrawledProfileListResponse

| Field | Type | Description |
| --- | --- | --- |
| `crawled_profiles` | Array\<CrawledProfileRead> | 크롤링 프로필 목록 |
| `page` | Number | 현재 페이지 |
| `size` | Number | 페이지 크기 |
| `total` | Number | 전체 개수 |
| `has_next` | Boolean | 다음 페이지 존재 여부 |

## 3. Health API

### `GET /health`

백엔드 서버가 정상적으로 실행 중인지 확인합니다.

#### Success Response

```json
{
  "status": "ok"
}
```

## 4. Crawled Profile APIs

## 4.1 크롤링 결과 JSON Import

### Endpoint

```http
POST /crawled-profiles/import-json
```

### 기능 설명

이미 준비된 크롤링 결과 JSON 데이터를 받아 `crawled_profiles` 테이블에 저장합니다. `source_url`을 우선 기준으로 중복을 건너뛰고, 없으면 `source + external_key` 기준으로 중복을 확인합니다.

### Request Body

배열 payload를 사용할 수 있습니다.

| Field | Required | Type | Description |
| --- | --- | --- | --- |
| `[].title` | No | String | 프로필 제목 또는 대표 타이틀 |
| `[].name` | No | String | 연수생 이름. `title`이 없으면 제목 대체값으로 사용 |
| `[].tags` | No | Array\<String> | 태그 목록. 저장 시 `parsed_json.tags`에 반영 |
| `[].raw_text` | Yes | String | 원문 또는 정제 전 텍스트 |
| `[].source` | No | String | 데이터 출처. 기본값 `json-import` |
| `[].source_url` | No | String | 원본 페이지 URL |
| `[].external_key` | No | String | 외부 데이터 고유 키 |
| `[].parsed_json` | No | Object | 추가 구조화 데이터 |

```json
[
  {
    "name": "김민준",
    "title": "프론트엔드 개발자",
    "source": "notion",
    "source_url": "https://notion.so/example/kim-minjun",
    "raw_text": "김민준 연수생은 React와 TypeScript 기반 프론트엔드 개발 경험이 있습니다.",
    "tags": ["frontend", "react", "typescript"]
  }
]
```

기존 크롤링 JSON 형태인 객체 payload도 사용할 수 있습니다.

```json
{
  "profile A | Notion": ["first profile text", "second profile text"]
}
```

### Success Response

#### `200 OK`

```json
{
  "imported_count": 1,
  "skipped_count": 0
}
```

## 4.2 크롤링 프로필 목록 조회

### Endpoint

```http
GET /crawled-profiles
```

### Query Parameters

| Field | Required | Type | Description |
| --- | --- | --- | --- |
| `page` | No | Number | 페이지 번호, 1부터 시작. 기본값 `1` |
| `size` | No | Number | 페이지 크기. 기본값 `20`, 최대 `100` |
| `q` | No | String | 검색어 |

### Success Response

#### `200 OK`

```json
{
  "crawled_profiles": [
    {
      "id": 1,
      "source": "notion",
      "external_key": "https://notion.so/example/kim-minjun",
      "source_url": "https://notion.so/example/kim-minjun",
      "title": "프론트엔드 개발자",
      "raw_text": "김민준 연수생은 React와 TypeScript 기반 프론트엔드 개발 경험이 있습니다.",
      "parsed_json": {
        "name": "김민준",
        "tags": ["frontend", "react", "typescript"]
      },
      "created_at": "2026-05-07T11:00:00Z"
    }
  ],
  "page": 1,
  "size": 20,
  "total": 1,
  "has_next": false
}
```

## 4.3 크롤링 프로필 상세 조회

### Endpoint

```http
GET /crawled-profiles/{profile_id}
```

### Path Parameters

| Field | Required | Type | Description |
| --- | --- | --- | --- |
| `profile_id` | Yes | Number | 조회할 크롤링 프로필 ID |

### Success Response

#### `200 OK`

```json
{
  "id": 1,
  "source": "notion",
  "external_key": "https://notion.so/example/kim-minjun",
  "source_url": "https://notion.so/example/kim-minjun",
  "title": "프론트엔드 개발자",
  "raw_text": "김민준 연수생은 React와 TypeScript 기반 프론트엔드 개발 경험이 있습니다.",
  "parsed_json": {
    "name": "김민준",
    "tags": ["frontend", "react", "typescript"]
  },
  "created_at": "2026-05-07T11:00:00Z"
}
```

### Error Response

| Status | Case |
| --- | --- |
| `404 Not Found` | 존재하지 않는 `profile_id` |
| `422 Unprocessable Entity` | `profile_id` 형식 오류 |

## 4.4 크롤링 프로필 Users 변환

### Endpoint

```http
POST /crawled-profiles/convert-to-users
```

### 기능 설명

저장된 `crawled_profiles` 데이터를 서비스 조회용 `users` 데이터로 변환합니다. 이미 변환된 데이터는 중복 생성하지 않고 건너뜁니다.

### Success Response

#### `200 OK`

```json
{
  "converted_count": 2,
  "skipped_count": 0
}
```

## 5. Frontend Demo Mapping

### 크롤링 결과 Import

| UI Element | API |
| --- | --- |
| 데모 데이터 적재 | `POST /crawled-profiles/import-json` |
| 적재 완료 후 목록 갱신 | `GET /crawled-profiles` |

### 크롤링 프로필 목록 화면

| UI Element | API Field |
| --- | --- |
| 고유 ID | `crawled_profiles[].id` |
| 이름 | `crawled_profiles[].title` |
| 태그 배지 | `crawled_profiles[].parsed_json.tags` |
| 상세 버튼 | `GET /crawled-profiles/{profile_id}` |

### 크롤링 프로필 상세 화면

| UI Element | API Field |
| --- | --- |
| 이름 | `title` |
| 출처 | `source` |
| 태그 배지 | `parsed_json.tags` |
| 원본 링크 | `source_url` |
| 원문 | `raw_text` |

## 6. Implementation Notes

- Base URL은 `http://localhost:8000`을 기준으로 합니다.
- 프론트 개발 서버는 Vite 기본 포트인 `http://localhost:5173`을 기준으로 합니다.
- API 응답 필드는 현재 백엔드 규칙에 맞춰 `snake_case`를 사용합니다.
- 1차 데모의 현재 흐름은 `크롤링 결과 import -> crawled_profiles 저장 -> crawled_profiles 조회`입니다.
- 목록 화면은 빠른 탐색을 위해 `id`, `title`, `parsed_json.tags`를 사용하고, 상세 화면에서 나머지 정보를 표시합니다.

## 7. Future Work

향후 개발 예정 기능은 본문 API 명세와 섞지 않고 이 섹션에서 별도로 관리합니다.

### 태그 기반 추천

변환된 `users.tags`를 기준으로 비슷한 연수생을 추천하는 API를 추가할 예정입니다. 필요 시 `raw_text`를 보조 정보로 사용해 추천 이유나 요약을 생성할 수 있습니다.

#### Proposed Endpoint

```http
GET /recommendations
```
