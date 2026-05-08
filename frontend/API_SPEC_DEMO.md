# SOMAtching Demo API Specification

## 1. Overview

본 문서는 SOMAtching 1차 데모 기준 API 명세입니다. 현재 백엔드는 크롤링 결과 JSON을 import해 `crawled_profiles` 테이블에 저장하고, 프론트엔드는 저장된 크롤링 프로필을 조회하는 흐름을 기준으로 합니다.

1. `GET /health`: 서버 상태 확인
2. `POST /crawled-profiles/import-json`: 크롤링 결과 JSON import 및 `crawled_profiles` 저장
3. `GET /crawled-profiles`: 저장된 크롤링 프로필 목록 조회
4. `GET /crawled-profiles/{profile_id}`: 저장된 크롤링 프로필 상세 조회

### Demo Scope

| 기능 |
| --- |
| 서버 상태 확인 |
| 크롤링 결과 JSON import |
| `crawled_profiles` 저장 |
| 크롤링 프로필 목록 조회 |
| 크롤링 프로필 상세 조회 |

### Base URL

```text
http://localhost:8000
```

### Naming Convention

현재 백엔드는 JSON 필드와 path parameter에 `snake_case`를 사용합니다. 프론트엔드는 응답을 그대로 사용하거나, 화면 계층에서만 camelCase로 변환합니다.

### Common Headers

| Header | Required | Type | Description |
| --- | --- | --- | --- |
| `Content-Type` | Request body가 있는 API에서 Yes | String | `application/json` |

### Common Error Response

에러 응답은 아래 형식을 권장합니다. 현재 백엔드 구현이 다를 경우 1차 데모에서는 백엔드 응답 형식을 우선 따릅니다.

```json
{
  "status": 400,
  "code": "invalid_request",
  "message": "요청 값이 올바르지 않습니다.",
  "detail": [
    {
      "field": "profile_id",
      "reason": "profile_id는 숫자여야 합니다."
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `status` | Number | HTTP 상태 코드 |
| `code` | String | 에러 코드 |
| `message` | String | 에러 메시지 |
| `detail` | Array | 필드 단위 상세 오류. 없으면 빈 배열 |

## 2. Data Models

### Crawled Profile

`crawled_profiles` 테이블에 저장되는 크롤링 결과 모델입니다. 1차 데모에서는 이 데이터를 목록/상세 화면에서 조회합니다.

| Field | Type | Description |
| --- | --- | --- |
| `profile_id` | Number | 크롤링 프로필 고유 ID |
| `name` | String | 연수생 이름 |
| `title` | String | 프로필 제목 또는 대표 타이틀 |
| `source` | String | 데이터 출처. 예: `notion` |
| `source_url` | String | 원본 노션 페이지 URL |
| `raw_text` | String | 노션 페이지에서 추출한 원문 또는 정제 전 텍스트 |
| `tags` | Array\<String> | 크롤링 또는 후처리로 추출한 태그 목록 |
| `created_at` | String | 생성일시, ISO 8601 |
| `updated_at` | String | 수정일시, ISO 8601 |

## 3. Health API

## 3.1 서버 상태 확인

### Endpoint

```http
GET /health
```

### 기능 설명

백엔드 서버가 정상적으로 실행 중인지 확인합니다.

### Request Parameters

#### Path Parameters

없음

#### Query Parameters

없음

#### Body Parameters

없음

### Success Response

#### `200 OK`

```json
{
  "status": "ok"
}
```

### Error Response

| Status | Code | Message | Case |
| --- | --- | --- | --- |
| `500 Internal Server Error` | `internal_server_error` | 서버 내부 오류가 발생했습니다. | 서버 상태 확인 실패 |

## 4. Crawled Profile APIs

## 4.1 크롤링 결과 JSON Import

### Endpoint

```http
POST /crawled-profiles/import-json
```

### 기능 설명

이미 준비된 크롤링 결과 JSON 데이터를 받아 `crawled_profiles` 테이블에 저장합니다. 현재 데모 데이터 적재용 API입니다.

### Request Parameters

#### Path Parameters

없음

#### Query Parameters

없음

#### Body Parameters

| Field | Required | Type | Description |
| --- | --- | --- | --- |
| `profiles` | Yes | Array\<Object> | import할 크롤링 프로필 목록 |
| `profiles[].name` | Yes | String | 연수생 이름 |
| `profiles[].title` | No | String | 프로필 제목 또는 대표 타이틀 |
| `profiles[].source` | No | String | 데이터 출처. 예: `notion` |
| `profiles[].source_url` | No | String | 원본 노션 페이지 URL |
| `profiles[].raw_text` | Yes | String | 노션 페이지 원문 또는 정제 전 텍스트 |
| `profiles[].tags` | No | Array\<String> | 태그 목록 |

```json
{
  "profiles": [
    {
      "name": "김민준",
      "title": "프론트엔드 개발자",
      "source": "notion",
      "source_url": "https://notion.so/example/kim-minjun",
      "raw_text": "김민준 연수생은 React와 TypeScript 기반 프론트엔드 개발 경험이 있습니다.",
      "tags": ["frontend", "react", "typescript"]
    },
    {
      "name": "이서윤",
      "title": "백엔드 개발자",
      "source": "notion",
      "source_url": "https://notion.so/example/lee-seoyun",
      "raw_text": "이서윤 연수생은 Node.js와 AWS 기반 백엔드 개발에 관심이 있습니다.",
      "tags": ["backend", "nodejs", "aws"]
    }
  ]
}
```

### Success Response

#### `201 Created`

```json
{
  "imported_count": 2,
  "skipped_count": 0
}
```

### Error Response

| Status | Code | Message | Case |
| --- | --- | --- | --- |
| `400 Bad Request` | `invalid_request` | 요청 값이 올바르지 않습니다. | `profiles` 누락, 빈 배열, `raw_text` 누락 |
| `400 Bad Request` | `invalid_json` | JSON 형식이 올바르지 않습니다. | 파싱할 수 없는 JSON |
| `500 Internal Server Error` | `internal_server_error` | 서버 내부 오류가 발생했습니다. | import 처리 중 서버 오류 |

## 4.2 크롤링 프로필 목록 조회

### Endpoint

```http
GET /crawled-profiles
```

### 기능 설명

`crawled_profiles` 테이블에 저장된 크롤링 프로필 목록을 조회합니다. 1차 데모의 목록 화면에서 사용합니다.

### Request Parameters

#### Path Parameters

없음

#### Query Parameters

| Field | Required | Type | Description |
| --- | --- | --- | --- |
| `page` | No | Number | 페이지 번호, 1부터 시작. 기본값 `1` |
| `size` | No | Number | 페이지 크기. 기본값 `20`, 최대 `100` |
| `q` | No | String | 이름, 제목, 태그, 원문 텍스트 검색어 |
| `tag` | No | String | 단일 태그 필터 |
| `tags` | No | String | 쉼표로 구분한 태그 필터. 예: `react,typescript` |

#### Body Parameters

없음

### Success Response

#### `200 OK`

```json
{
  "crawled_profiles": [
    {
      "profile_id": 1,
      "name": "김민준",
      "tags": ["frontend", "react", "typescript"]
    },
    {
      "profile_id": 2,
      "name": "이서윤",
      "tags": ["backend", "nodejs", "aws"]
    }
  ],
  "page": 1,
  "size": 20,
  "total": 2,
  "has_next": false
}
```

### Error Response

| Status | Code | Message | Case |
| --- | --- | --- | --- |
| `400 Bad Request` | `invalid_request` | 요청 값이 올바르지 않습니다. | `page`, `size`, `tags` 값 오류 |
| `500 Internal Server Error` | `internal_server_error` | 서버 내부 오류가 발생했습니다. | 서버 오류 |

## 4.3 크롤링 프로필 상세 조회

### Endpoint

```http
GET /crawled-profiles/{profile_id}
```

### 기능 설명

`crawled_profiles` 테이블에 저장된 크롤링 프로필 하나의 상세 정보를 조회합니다.

### Request Parameters

#### Path Parameters

| Field | Required | Type | Description |
| --- | --- | --- | --- |
| `profile_id` | Yes | Number | 조회할 크롤링 프로필 ID |

#### Query Parameters

없음

#### Body Parameters

없음

### Success Response

#### `200 OK`

```json
{
  "profile_id": 1,
  "name": "김민준",
  "title": "프론트엔드 개발자",
  "source": "notion",
  "source_url": "https://notion.so/example/kim-minjun",
  "raw_text": "김민준 연수생은 React와 TypeScript 기반 프론트엔드 개발 경험이 있습니다.",
  "tags": ["frontend", "react", "typescript"],
  "created_at": "2026-05-07T11:00:00Z",
  "updated_at": "2026-05-07T11:00:00Z"
}
```

### Error Response

| Status | Code | Message | Case |
| --- | --- | --- | --- |
| `400 Bad Request` | `invalid_request` | 요청 값이 올바르지 않습니다. | `profile_id` 형식 오류 |
| `404 Not Found` | `crawled_profile_not_found` | 크롤링 프로필을 찾을 수 없습니다. | 존재하지 않는 `profile_id` |
| `500 Internal Server Error` | `internal_server_error` | 서버 내부 오류가 발생했습니다. | 서버 오류 |

## 5. Frontend Demo Mapping

### 크롤링 결과 Import

| UI Element | API |
| --- | --- |
| 데모 데이터 적재 | `POST /crawled-profiles/import-json` |
| 적재 완료 후 목록 갱신 | `GET /crawled-profiles` |

### 크롤링 프로필 목록 화면

| UI Element | API Field |
| --- | --- |
| 이름 | `crawled_profiles[].name` |
| 태그 배지 | `crawled_profiles[].tags` |
| 상세 버튼 | `GET /crawled-profiles/{profile_id}` |

### 크롤링 프로필 상세 화면

| UI Element | API Field |
| --- | --- |
| 이름 | `name` |
| 제목 | `title` |
| 출처 | `source` |
| 태그 배지 | `tags` |
| 원본 링크 | `source_url` |
| 원문 | `raw_text` |

## 6. Implementation Notes

- Base URL은 `http://localhost:8000`을 기준으로 합니다.
- API 응답 필드는 현재 백엔드 규칙에 맞춰 `snake_case`를 사용합니다.
- 1차 데모의 현재 흐름은 `크롤링 결과 import -> crawled_profiles 저장 -> crawled_profiles 조회`입니다.
- `GET /crawled-profiles`, `GET /crawled-profiles/{profile_id}`는 현재 저장된 `crawled_profiles` 데이터를 조회하는 API입니다.
- `POST /crawled-profiles/import-json`은 `crawled_profiles` 테이블에 데이터를 저장합니다.
- 목록 화면은 빠른 탐색을 위해 `profile_id`, `name`, `tags`만 사용하고, 상세 화면에서 나머지 정보를 표시합니다.

## 7. Future Work

향후 개발 예정 기능은 본문 API 명세와 섞지 않고 이 섹션에서 별도로 관리합니다.

### Users 변환

`crawled_profiles`의 `name`, `title`, `source`, `source_url`, `raw_text`, `tags`를 기반으로 서비스 조회용 `users` 데이터를 생성하는 기능을 추가할 예정입니다.

#### Proposed Endpoint

```http
POST /users/from-crawled-profiles
```

### 태그 기반 추천

변환된 `users.tags`를 기준으로 비슷한 연수생을 추천하는 API를 추가할 예정입니다. 필요 시 `raw_text`를 보조 정보로 사용해 추천 이유나 요약을 생성할 수 있습니다.

#### Proposed Endpoint

```http
GET /recommendations
```
