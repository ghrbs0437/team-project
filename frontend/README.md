# Frontend

SOMatching 프론트엔드 프로젝트입니다.  
React, Vite 기반으로 실행됩니다.

## 실행 전 준비

아래 프로그램이 설치되어 있어야 합니다.

- Node.js
- npm 또는 pnpm

설치 여부는 터미널에서 확인할 수 있습니다.

```bash
node -v
npm -v
```

pnpm을 사용할 경우 아래 명령어도 확인합니다.

```bash
pnpm -v
```

pnpm이 설치되어 있지 않다면 아래 명령어로 설치할 수 있습니다.

```bash
npm install -g pnpm
```

## 실행 방법

프로젝트 루트에서 프론트엔드 폴더로 이동합니다.

```bash
cd frontend
```

의존성 패키지를 설치합니다.

```bash
pnpm install
```

백엔드는 FastAPI 기본 포트인 `8000`, 프론트엔드는 Vite 기본 포트인 `5173`을 기준으로 실행합니다.
프론트에서 호출할 백엔드 주소를 바꾸려면 `frontend/.env`에 아래 값을 설정합니다.

```bash
VITE_API_BASE_URL=http://localhost:8000
```

설치가 끝나면 개발 서버를 실행합니다.

```bash
pnpm run dev
```

터미널에 아래와 비슷한 주소가 표시되면 브라우저에서 접속합니다.

```text
http://localhost:5173
```

## Docker Compose로 실행하는 방법

프로젝트 루트에서 아래 명령어를 실행하면 프론트엔드, 백엔드, DB를 함께 실행할 수 있습니다.

```bash
docker compose up --build
```

프론트엔드 컨테이너는 기본적으로 `http://localhost:5173`에 노출됩니다. 프론트엔드에서 호출하는 백엔드 주소는 루트 `.env`의 `VITE_API_BASE_URL` 값으로 조정합니다.

## npm으로 실행하는 방법

pnpm 대신 npm을 사용하고 싶다면 아래 순서로 실행할 수 있습니다.

```bash
cd frontend
npm install
npm run dev
```

## 빌드 방법

배포용 파일을 만들 때는 아래 명령어를 실행합니다.

```bash
pnpm run build
```

빌드가 성공하면 `dist` 폴더가 생성됩니다.

## 자주 발생하는 문제

### 포트가 이미 사용 중인 경우

`5173` 포트가 이미 사용 중이면 Vite가 자동으로 다른 포트를 안내할 수 있습니다.  
터미널에 표시된 주소로 접속하면 됩니다.

### 패키지 설치 오류가 나는 경우

기존 설치 파일을 지운 뒤 다시 설치합니다.

```bash
rm -rf node_modules
pnpm install
```

### 실행 명령어를 찾을 수 없다는 오류가 나는 경우

현재 위치가 `frontend` 폴더인지 확인합니다.

```bash
pwd
```

경로 끝이 `frontend`가 아니라면 아래 명령어로 이동한 뒤 다시 실행합니다.

```bash
cd frontend
pnpm run dev
```
