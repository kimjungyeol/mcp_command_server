# Poetry를 이용한 MCP 서버 설정 가이드

## 현재 상황
- 경로: `C:\Users\kjy\myproject\python\mcp_cmd`
- 오류: `Poetry could not find a pyproject.toml file`

## 1. Poetry 프로젝트 초기화

### 방법 1: 새 프로젝트 생성
```bash
# 현재 디렉토리에서 초기화
poetry init

# 또는 완전히 새로 시작
cd C:\Users\kjy\myproject\python
poetry new mcp_cmd
cd mcp_cmd
```

### 방법 2: 기존 디렉토리에 Poetry 설정 추가
```bash
# 현재 위치에서 (C:\Users\kjy\myproject\python\mcp_cmd)
poetry init --no-interaction
```

## 2. 디렉토리 구조 설정

Poetry 프로젝트의 권장 구조:
```
mcp_cmd/
├── pyproject.toml          # Poetry 설정 파일
├── README.md              # 프로젝트 설명
├── src/                   # 소스 코드 디렉토리
│   └── mcp_command_server/
│       ├── __init__.py
│       ├── mcp_server_api.py      # MCP API 연결 파일
│       └── command_executor.py    # 실제 명령어 실행 모듈
└── tests/                 # 테스트 파일 (선택사항)
    └── test_server.py
```

## 3. 단계별 설정 방법

### 3.1 pyproject.toml 파일 생성
위에서 제공한 `pyproject.toml` 파일을 프로젝트 루트에 저장하세요.

### 3.2 소스 디렉토리 생성
```bash
mkdir src
mkdir src\mcp_command_server
```

### 3.3 __init__.py 파일 생성
```bash
# 빈 파일 생성
type nul > src\mcp_command_server\__init__.py
```

### 3.4 소스 파일 이동
기존 `server.py`와 `command_executor.py` 파일을 `src\mcp_command_server\` 폴더로 이동하세요.

## 4. Poetry 명령어 사용

### 4.1 의존성 설치
```bash
# 가상환경 생성 및 패키지 설치
poetry install

# MCP 패키지가 PyPI에 없는 경우
poetry add git+https://github.com/modelcontextprotocol/python-sdk.git
```

### 4.2 가상환경 활성화
```bash
# Poetry 쉘 활성화
poetry shell

# 또는 명령어 실행
poetry run python src/mcp_command_server/mcp_server_api.py
```

### 4.3 패키지 추가/제거
```bash
# 패키지 추가
poetry add package_name

# 개발 의존성 추가
poetry add --group dev package_name

# 패키지 제거
poetry remove package_name
```

## 5. Claude Desktop 설정 (Poetry 버전)

### 5.1 실행 경로 확인
```bash
# Poetry 환경에서 Python 경로 확인
poetry run which python
# 또는 Windows에서
poetry run where python
```

### 5.2 Claude 설정 파일 수정
`%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "command-executor": {
      "command": "poetry",
      "args": [
        "run",
        "python",
        "src/mcp_command_server/mcp_server_api.py"
      ],
      "cwd": "C:/Users/kjy/myproject/python/mcp_command_server",
      "env": {}
    }
  }
}
```

또는 직접 Python 실행:
```json
{
  "mcpServers": {
    "command-executor": {
      "command": "C:/Users/kjy/.cache/pypoetry/virtualenvs/mcp-command-server-xxxxx/Scripts/python.exe",
      "args": [
        "C:/Users/kjy/myproject/python/mcp_cmd/src/mcp_command_server/server.py"
      ],
      "env": {}
    }
  }
}
```

## 6. 빠른 시작 명령어

현재 위치에서 바로 시작하려면:

```bash
# 1. pyproject.toml 파일 생성 (위의 내용을 복사해서 저장)

# 2. 소스 디렉토리 구조 생성
mkdir src\mcp_command_server
echo. > src\mcp_command_server\__init__.py

# 3. 기존 파일들 이동
move server.py src\mcp_command_server\
move command_executor.py src\mcp_command_server\

# 4. Poetry 설치 및 실행
poetry install
poetry shell
```

## 7. 문제 해결

### MCP 패키지를 찾을 수 없는 경우:
```bash
# GitHub에서 직접 설치
poetry add git+https://github.com/modelcontextprotocol/python-sdk.git

# 또는 로컬 개발용으로 설치
poetry add mcp --allow-prereleases
```

### 가상환경 위치 확인:
```bash
poetry env info --path
```

### Poetry 캐시 정리:
```bash
poetry cache clear pypi --all
```

## 8. 추천 워크플로우

1. `poetry shell`로 가상환경 활성화
2. `poetry run python src/mcp_command_server/server.py`로 서버 테스트
3. Claude Desktop 설정 후 재시작
4. Claude에서 "현재 디렉토리 확인해줘" 테스트

이제 Poetry를 이용해서 깔끔하게 MCP 서