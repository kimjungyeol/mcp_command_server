#!/usr/bin/env python3
# """
# MCP Server - API 연결 및 통신 담당 (수정된 버전)
# Claude와의 통신을 위한 MCP 프로토콜 구현
# """

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
    )
except ImportError as e:
    logger.error(f"MCP 패키지를 찾을 수 없습니다: {e}")
    print("MCP 패키지 설치가 필요합니다:")
    print("poetry add git+https://github.com/modelcontextprotocol/python-sdk.git")
    sys.exit(1)

from command_executor import CommandExecutor


class MCPCommandServer:
    # """MCP 명령어 실행 서버"""
    
    def __init__(self):
        self.server = Server("command-executor")
        self.executor = CommandExecutor()
        self.setup_handlers()
        logger.info("MCP 서버 초기화 완료")
    
    def setup_handlers(self):
        # """MCP 핸들러 설정"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            # """사용 가능한 도구 목록 반환"""
            logger.info("도구 목록 요청됨")
            return [
                Tool(
                    name="execute_command",
                    description="Windows CMD 명령어를 실행합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "실행할 CMD 명령어"
                            },
                            "working_directory": {
                                "type": "string",
                                "description": "명령어를 실행할 작업 디렉토리 (선택사항)",
                                "default": None
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "명령어 실행 제한 시간(초), 기본값 30초",
                                "default": 30
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="list_directory",
                    description="지정된 디렉토리의 파일과 폴더 목록을 표시합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "목록을 표시할 디렉토리 경로",
                                "default": "."
                            }
                        }
                    }
                ),
                Tool(
                    name="get_current_directory",
                    description="현재 작업 디렉토리를 반환합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            # """도구 호출 처리"""
            logger.info(f"도구 호출: {name}, 인수: {arguments}")
            
            try:
                if name == "execute_command":
                    command = arguments.get("command")
                    working_directory = arguments.get("working_directory")
                    timeout = arguments.get("timeout", 30)
                    
                    if not command:
                        return [TextContent(
                            type="text", 
                            text="오류: 실행할 명령어를 입력해주세요."
                        )]
                    
                    result = await self.executor.execute_command(
                        command, working_directory, timeout
                    )
                    return [TextContent(type="text", text=result)]
                
                elif name == "list_directory":
                    path = arguments.get("path", ".")
                    result = await self.executor.list_directory(path)
                    return [TextContent(type="text", text=result)]
                
                elif name == "get_current_directory":
                    result = await self.executor.get_current_directory()
                    return [TextContent(type="text", text=result)]
                
                else:
                    error_msg = f"오류: 알 수 없는 도구 '{name}'"
                    logger.error(error_msg)
                    return [TextContent(type="text", text=error_msg)]
                    
            except Exception as e:
                error_msg = f"오류가 발생했습니다: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return [TextContent(type="text", text=error_msg)]
    
    async def run(self):
        # """서버 실행"""
        try:
            logger.info("MCP 서버 시작 중...")
            
            # stdio 서버 시작
            async with stdio_server() as (read_stream, write_stream):
                logger.info("stdio 서버 연결됨")
                await self.server.run(
                    read_stream, 
                    write_stream, 
                    self.server.create_initialization_options()
                )
                
        except KeyboardInterrupt:
            logger.info("사용자에 의해 서버가 중단되었습니다")
        except Exception as e:
            logger.error(f"서버 실행 중 오류 발생: {e}", exc_info=True)
            raise


def test_server_sync():
    # """서버 테스트 함수 (Claude 없이 테스트용)"""
    print("MCP 서버 테스트 모드")
    print("Ctrl+C로 종료하세요")
    
    try:
        executor = CommandExecutor()

        async def test_commands():
            print("\n=== 테스트 시작 ===")
            result = await executor.get_current_directory()
            print(f"현재 디렉토리: {result}")
            result = await executor.list_directory(".")
            print(f"\n디렉토리 목록:\n{result}")
            result = await executor.execute_command("echo Hello MCP!")
            print(f"\n명령어 실행 결과:\n{result}")
            print("\n=== 테스트 완료 ===")

        try:
            loop = asyncio.get_running_loop()
            # 이미 실행 중인 루프가 있으면, 직접 태스크로 실행
            task = loop.create_task(test_commands())
            loop.run_until_complete(task)
        except RuntimeError:
            # 실행 중인 루프가 없으면, 새로 실행
            asyncio.run(test_commands())
        
    except Exception as e:
        print(f"테스트 중 오류: {e}")


async def main():
    # """메인 함수"""
    # 명령행 인수 확인
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        await test_server_async()
        return
    
    # 정상 MCP 서버 실행
    server = MCPCommandServer()
    await server.run()

async def test_server_async():
    # 비동기 테스트 함수
    print("MCP 서버 테스트 모드")
    print("Ctrl+C로 종료하세요")
    try:
        executor = CommandExecutor()
        print("\n=== 테스트 시작 ===")
        result = await executor.get_current_directory()
        print(f"현재 디렉토리: {result}")
        result = await executor.list_directory(".")
        print(f"\n디렉토리 목록:\n{result}")
        result = await executor.execute_command("echo Hello MCP!")
        print(f"\n명령어 실행 결과:\n{result}")
        print("\n=== 테스트 완료 ===")
    except Exception as e:
        print(f"테스트 중 오류: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("서버가 정상적으로 종료되었습니다")
    except Exception as e:
        logger.error(f"서버 시작 실패: {e}", exc_info=True)
        sys.exit(1)