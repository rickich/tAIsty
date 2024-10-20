# AX FastAPI Boilerplate
## Features
- FastAPI 기반의 RESTful API
- 채팅 기능 구현
- 데이터베이스 통합 (SQLAlchemy 사용)
- 외부 서비스 연동 (LLM, 벡터 데이터베이스 등)
- Docker 컨테이너화
- Logging 

## Technical Stack
- Python 3.12
- FastAPI 0.113.0
- SQLAlchemy 2.0.34
- Pydantic 2.9.0
- Uvicorn 0.30.6
- Dependency Injector 4.42.0b1
- OpenAI 1.44.0
- Anthropic 0.34.2
- Pinecone 5.1.0
- Poetry (의존성 관리)
- Docker (컨테이너화)

## Quick Start
### Install dependency
```shell
> poetry shell
> poetry install
```
### Environment Variables (.env)
You need to create a `.env` file in the root directory of the project and fill in the environment variables.\
Refer to the config file to add the necessary environment variables.
```shell
> cp .env.example .env
```
### Run server
```shell
> python3 main.py --env local|dev|prod --debug
```
### Docker
```shell
> docker-compose up --build
```

## Project Structure

```
.
├── Dockerfile
├── README.md
├── app
│   ├── chat
│   │   ├── application
│   │   ├── domain
│   │   ├── infrastructure
│   │   └── interface
│   ├── dependency.py
│   └── server.py
├── core
│   ├── config.py
│   ├── db
│   ├── exceptions
│   ├── fastapi
│   └── helpers
├── docker-compose.yml
├── libs
│   ├── connection
│   ├── repository
│   ├── service
│   └── sse
├── main.py
├── poetry.lock
├── pyproject.toml
├── test.db
└── tests
```

- `app/`: 애플리케이션의 주요 로직이 포함된 디렉토리
  - `chat/`: 채팅 관련 기능 구현
    - `application/`: 애플리케이션 서비스
    - `domain/`: 도메인 모델 및 비즈니스 로직
    - `infrastructure/`: 데이터베이스 및 외부 서비스 통합
    - `interface/`: API 엔드포인트 및 요청/응답 모델
- `core/`: 핵심 기능 및 설정
  - `config.py`: 애플리케이션 설정
  - `db/`: 데이터베이스 관련 유틸리티
  - `exceptions/`: 사용자 정의 예외 클래스
  - `fastapi/`: FastAPI 관련 미들웨어 및 의존성
- `libs/`: 공통 라이브러리 및 유틸리티
  - `connection/`: 외부 서비스 연결 (예: LLM, 벡터 데이터베이스)
  - `repository/`: 저장소 인터페이스 및 구현
  - `service/`: 공통 서비스 구현
  - `sse/`: Server-Sent Events 관련 기능
- `main.py`: 애플리케이션 진입점
- `Dockerfile` & `docker-compose.yml`: 도커 설정 파일
- `pyproject.toml` & `poetry.lock`: 의존성 관리 파일

![ax-boilerplate](https://github.com/user-attachments/assets/a84650f2-045f-4edf-ad9b-647a3331f04f)

![Hexagonal](https://github.com/user-attachments/assets/3ef7020b-3a03-4d85-8302-420e8bbffdb0)
