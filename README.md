# Claude Mcp Command Server

## Poetry 명령어 사용

### 1 의존성 설치
```bash
# 가상환경 생성 및 패키지 설치
poetry install

# MCP 패키지가 PyPI에 없는 경우
poetry add git+https://github.com/modelcontextprotocol/python-sdk.git
```

### 2 가상환경 활성화
```bash
# Poetry 쉘 활성화
poetry shell

# 또는 명령어 실행
poetry run python src/mcp_command_server/mcp_server_api.py
=======
## 4. Poetry 명령어 사용

### 4.1 의존성 설치
```bash
# 가상환경 생성 및 패키지 설치
poetry install

# MCP 패키지가 PyPI에 없는 경우
poetry add git+https://github.com/modelcontextprotocol/python-sdk.git
```

### 2 가상환경 활성화
```bash
# Poetry 쉘 활성화
poetry shell

# 또는 명령어 실행 테스트
poetry run python src/mcp_command_server/mcp_server_api.py
```


## Claude desktop config json
```
{
    "mcpServers": {
		"command-executor": {
            "command": "cmd",
            "args": [
                "/c",
                "cd /d C:\\Users\\[user]\\python\\mcp_command_server && poetry run python src/mcp_command_server/mcp_server_api.py"
            ]
        }
    }
}
```
로컬의 mcp_command_server 소스 위치 정보를 확인하여 수정.