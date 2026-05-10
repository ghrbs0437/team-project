# Local Setup

이 문서는 로컬 개발 환경을 맞추는 방법을 정리합니다.

## 0. Prerequisites

### Docker Compose로 실행할 경우

* Git
* Docker Desktop 또는 Docker Engine
* Docker Compose v2

### 로컬 프로세스로 직접 실행할 경우 추가 필요

* Python 3.12
* Node.js
* pnpm

Docker Compose v2는 일반적으로 아래 명령어로 확인할 수 있습니다.

```bash
docker compose version
```

## 1. Clone

```bash
git clone https://github.com/soma17th-ai35/team-project.git
cd team-project
```

fork를 사용한다면 fork 저장소를 clone한 뒤 원본 저장소를 `upstream`으로 추가합니다.

```bash
git remote add upstream https://github.com/soma17th-ai35/team-project
git fetch upstream
```

## 2. Docker Compose로 전체 실행

루트에 `.env.example`을 복사해 `.env`를 만듭니다.

```bash
cp .env.example .env
```

Windows cmd를 사용하는 경우 아래 명령어를 사용합니다.

```cmd
copy .env.example .env
```

Docker Engine이 실행 중이어야 합니다.

* Windows: Docker Desktop 실행
* Linux: Docker daemon 실행

```bash
docker compose up --build
```

백그라운드 실행이 필요하면 아래 명령어를 사용합니다.

```bash
docker compose up --build -d
```

실행 후 아래 주소로 접속합니다.

* Frontend: [http://localhost:5173](http://localhost:5173)
* Backend API: [http://localhost:8000](http://localhost:8000)
* Backend Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* Backend health check: [http://localhost:8000/health](http://localhost:8000/health)
* Database: `localhost:5432`

Compose로 실행하는 backend 컨테이너는 시작 시 `app.core.init_db`를 실행해 기본 DB 테이블을 준비합니다.

## 3. DB만 Docker로 실행하고 앱은 로컬 프로세스로 실행

이 방식은 Docker를 아예 쓰지 않는 실행 방법이 아니라, PostgreSQL만 컨테이너로 표준화하고 Backend/Frontend는 호스트에서 직접 실행하는 개발 모드입니다. 앱 코드를 자주 수정하면서 가상환경, IDE 디버거, Vite HMR 같은 로컬 개발 도구를 쓰고 싶을 때 사용합니다.

처음 실행 확인이 목적이면 2번의 전체 Docker Compose 실행이 더 단순합니다. Backend까지 Docker로 실행하려면 `docker compose up --build` 또는 `docker compose up --build backend`를 사용합니다.

DB 컨테이너만 먼저 실행합니다.

```bash
docker compose up -d db
```

### Backend

아래 명령어는 Windows cmd 기준입니다.

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
init-db.bat
dev.bat
```

PowerShell을 사용하는 경우 가상환경 활성화 명령어는 아래와 같습니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

### Frontend

프론트엔드는 별도 터미널에서 실행합니다.

```bash
cd frontend
pnpm install
pnpm run dev
```

백엔드는 기본적으로 아래 DB 주소를 사용합니다.

```text
DATABASE_URL=postgresql+psycopg://soma:soma@localhost:5432/soma17ai35
```

다른 DB를 쓰는 경우 터미널 환경변수로 `DATABASE_URL`을 지정합니다.

## 4. Stop

```bash
docker compose down
```

DB 볼륨까지 삭제해야 하는 경우에만 아래 명령을 사용합니다.

```bash
docker compose down -v
```

## 5. Troubleshooting

### Docker daemon is not running

아래와 같은 오류가 나면 Docker Desktop이 실행 중인지 확인합니다.

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

Docker Desktop을 실행한 뒤 다시 시도합니다.

```bash
docker compose up --build
```

### Port already in use

`8000`, `5173`, `5432` 포트가 이미 사용 중이면 루트 `.env`에서 host port를 바꿉니다.

```dotenv
BACKEND_PORT=18000
FRONTEND_PORT=15173
DB_PORT=15432
VITE_API_BASE_URL=http://localhost:18000
```

DB host port를 바꾼 뒤 백엔드를 Docker 밖에서 직접 실행한다면 `DATABASE_URL`의 port도 같은 값으로 맞춥니다.

예시:

```text
DATABASE_URL=postgresql+psycopg://soma:soma@localhost:15432/soma17ai35
```

변경 후 다시 실행합니다.

```bash
docker compose up --build
```

### Compose configuration check

Compose 설정만 확인하고 싶으면 아래 명령어를 실행합니다.

```bash
docker compose config
```
