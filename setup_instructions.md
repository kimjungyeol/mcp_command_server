# MCP Command Server 설치 및 설정 가이드

## 1. 프로젝트 구조
```
mcp_command_server/
├── server.py              # MCP API 연결 파일
├── command_executor.py     # 실제 명령어 실행 모듈
├── requirements.txt        # 필요 패키지 목록
└── README.md              # 이 파일
```

## 2. 설치 방법

### 2.1 Python 환경 설정
```bash
# 가상환경 생성 (권장)
python -m venv mcp_env

# 가상환경 활성화
# Windows:
mcp_env\Scripts\activate
# macOS/Linux:
source mcp_env/bin/activate
```

### 2.2 필요 패키지 설치
```bash
pip install -r requirements.txt
```

### 2.3 MCP 패키지 설치 (수동)
MCP 패키지가 아직 공식 릴리스되지 않았다면:
```bash
pip install git+https://github.com/modelcontextprotocol/python-sdk.git
```

## 3. Claude에 MCP 서버 등록

### 3.1 Claude Desktop 설정 파일 수정
Windows의 경우 다음 경로에 설정 파일을 생성/수정:
```
%APPDATA%\Claude\claude_desktop_config.json
```

macOS의 경우:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 3.2 설정 파일 내용
```json
{
  "mcpServers": {
    "command-executor": {
      "command": "python",
      "args": [
        "C:/path/to/your/mcp_command_server/server.py"
      ],
      "env": {}
    }
  }
}
```

**중요**: `C:/path/to/your/mcp_command_server/server.py` 부분을 실제 server.py 파일의 전체 경로로 변경하세요.

### 3.3 Python 경로 확인
Python 경로를 확인하려면:
```bash
where python
# 또는
python -c "import sys; print(sys.executable)"
```

전체 Python 경로를 사용하는 경우:
```json
{
  "mcpServers": {
    "command-executor": {
      "command": "C:/Python311/python.exe",
      "args": [
        "C:/path/to/your/mcp_command_server/server.py"
      ],
      "env": {}
    }
  }
}
```

## 4. 사용 방법

### 4.1 Claude Desktop 재시작
설정 파일을 수정한 후 Claude Desktop을 완전히 종료하고 다시 시작하세요.

### 4.2 사용 가능한 명령어
Claude에서 다음과 같이 사용할 수 있습니다:

1. **명령어 실행**
   - "dir 명령어를 실행해줘"
   - "python --version을 확인해줘"
   - "C:\\temp 디렉토리에서 ls 명령을 실행해줘"

2. **디렉토리 목록 조회**
   - "현재 디렉토리 목록을 보여줘"
   - "C:\\Users 디렉토리 목록을 보여줘"

3. **현재 위치 확인**
   - "현재 작업 디렉토리를 알려줘"

## 5. 보안 고려사항

### 5.1 제한된 명령어
다음 명령어들은 보안상 실행이 제한됩니다:
- `format`
- `del /s`
- `rmdir /s`
- `shutdown`
- `taskkill /f`
- `reg delete`

### 5.2 추가 보안 설정
더 안전한 사용을 위해 `command_executor.py`의 `dangerous_commands` 리스트에 추가 명령어를 등록할 수 있습니다.

## 6. 문제 해결

### 6.1 서버가 시작되지 않는 경우
1. Python 경로가 올바른지 확인
2. 필요 패키지가 설치되었는지 확인
3. 파일 경로가 올바른지 확인

### 6.2 명령어가 실행되지 않는 경우
1. 명령어가 보안 제한 목록에 있는지 확인
2. 작업 디렉토리 권한 확인
3. 명령어 구문이 올바른지 확인

### 6.3 로그 확인
서버 실행 시 오류가 발생하면 콘솔에 오류 메시지가 표시됩니다.

## 7. 테스트 방법

### 7.1 직접 실행 테스트
```bash
python server.py
```

### 7.2 Claude에서 테스트
Claude Desktop에서 다음과 같이 요청:
- "명령어 실행 도구가 사용 가능한가요?"
- "현재 디렉토리를 확인해주세요"

## 8. 확장 기능

추가 기능이 필요한 경우 `command_executor.py`에 새로운 메서드를 추가하고, `server.py`의 도구 목록에 등록하면 됩니다.

예시:
- 파일 읽기/쓰기 기능
- 프로세스 모니터링
- 시스템 정보 조회
- 네트워크 상태 확인

## 9. 주의사항

- 이 도구는 시스템 명령어를 실행하므로 신중하게 사용하세요
- 중요한 시스템 파일이나 디렉토리에 대한 작업은 백업 후 수행하세요
- 알 수 없는 명령어는 실행하지 마세요