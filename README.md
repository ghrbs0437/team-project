# team-project

소마 17기 AI 35조 팀 프로젝트입니다. FastAPI 백엔드, React/Vite 프론트엔드, PostgreSQL DB를 Docker Compose로 함께 실행할 수 있습니다.

## 빠른 시작

처음 프로젝트를 확인하는 경우에는 Docker Compose로 전체 서비스를 실행하는 방법이 가장 단순합니다.

### 필요 프로그램

- Git
- Docker Desktop 또는 Docker Engine
- Docker Compose v2

Docker Compose 설치 여부는 아래 명령어로 확인합니다.

```bash
docker compose version
```

### 실행

루트 디렉터리에서 환경변수 예시 파일을 복사한 뒤 서비스를 실행합니다. Docker Engine이 실행 중이어야 합니다.

```bash
cp .env.example .env
docker compose up --build
```

Windows cmd에서는 아래 명령어로 `.env`를 복사합니다.

```cmd
copy .env.example .env
```

백그라운드에서 실행하려면 `-d` 옵션을 붙입니다.

```bash
docker compose up --build -d
```

실행 후 아래 주소로 접속합니다.

- Frontend: <http://localhost:5173>
- Backend API: <http://localhost:8000>
- Backend Swagger UI: <http://localhost:8000/docs>
- Backend health check: <http://localhost:8000/health>
- PostgreSQL: `localhost:5432`

종료할 때는 아래 명령어를 사용합니다.

```bash
docker compose down
```

DB 볼륨까지 삭제해야 할 때만 아래 명령어를 사용합니다.

```bash
docker compose down -v
```

## 개발 모드

앱 코드를 자주 수정한다면 DB만 Docker로 실행하고 Backend/Frontend는 로컬 프로세스로 실행할 수 있습니다. 이 방식은 IDE 디버거, Python 가상환경, Vite HMR을 쓰기 위한 개발 모드입니다.

```bash
docker compose up -d db
```

Backend와 Frontend를 각각 로컬에서 실행하는 자세한 순서는 [`docs/LOCAL_SETUP.md`](docs/LOCAL_SETUP.md)를 참고하세요.

## 환경변수

- `.env.example`: 커밋되는 로컬 실행 예시 파일
- `.env`: 개인 PC에서만 사용하는 실제 로컬 환경변수 파일

`.env`와 `.env.*`는 git에 커밋하지 않습니다. CI/CD나 배포 환경에서는 민감한 값은 GitHub Secrets, 비민감 설정값은 GitHub Variables로 관리합니다.

## 프로젝트 구조

- `backend/`: FastAPI 백엔드 애플리케이션, PostgreSQL 연동, 사용자/크롤링 프로필 API
- `frontend/`: React, Vite 기반 프론트엔드 애플리케이션
- `docs/`: 로컬 실행 방법, 개발 문서, API/DB 설계 문서
- `data/`: 샘플 데이터와 공통 데이터 포맷 문서
- `infra/`: Docker, Nginx, AWS 등 인프라 관련 설정

## 관련 문서

- [로컬 실행 가이드](docs/LOCAL_SETUP.md)
- [백엔드 README](backend/README.md)
- [프론트엔드 README](frontend/README.md)
- [DB 스키마 문서](docs/backend-db.md)
