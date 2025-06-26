# """
# Command Executor - 실제 명령어 실행 담당 모듈
# Windows CMD 명령어 실행 및 파일 시스템 작업 처리
# """

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class CommandExecutor:
    # """명령어 실행 클래스"""
    
    def __init__(self):
        self.default_encoding = 'cp949'  # Windows 기본 인코딩
        
    async def execute_command(
        self, 
        command: str, 
        working_directory: Optional[str] = None,
        timeout: int = 30
    ) -> str:
        # """
        # CMD 명령어를 비동기적으로 실행
        # 
        # Args:
        #     command: 실행할 명령어
        #     working_directory: 작업 디렉토리 (선택사항)
        #     timeout: 제한 시간(초)
        #     
        # Returns:
        #     명령어 실행 결과
        # """
        try:
            # 작업 디렉토리 설정
            cwd = working_directory if working_directory else os.getcwd()
            
            # 디렉토리 존재 확인
            if working_directory and not os.path.exists(working_directory):
                return f"오류: 디렉토리 '{working_directory}'가 존재하지 않습니다."
            
            # 보안을 위한 위험한 명령어 체크
            dangerous_commands = [
                'format', 'del /s', 'rmdir /s', 'rd /s', 
                'shutdown', 'taskkill /f', 'reg delete'
            ]
            
            command_lower = command.lower()
            for dangerous in dangerous_commands:
                if dangerous in command_lower:
                    return f"보안상 위험한 명령어는 실행할 수 없습니다: {command}"
            
            # 명령어 실행
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                shell=True
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                # 출력 디코딩
                stdout_text = self._decode_output(stdout)
                stderr_text = self._decode_output(stderr)
                
                # 결과 포맷팅
                result = f"명령어: {command}\n"
                result += f"작업 디렉토리: {cwd}\n"
                result += f"종료 코드: {process.returncode}\n\n"
                
                if stdout_text:
                    result += f"출력:\n{stdout_text}\n"
                
                if stderr_text:
                    result += f"오류:\n{stderr_text}\n"
                
                if not stdout_text and not stderr_text:
                    result += "출력 없음\n"
                
                return result
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return f"명령어 실행 시간 초과 ({timeout}초): {command}"
                
        except Exception as e:
            return f"명령어 실행 중 오류 발생: {str(e)}"
    
    async def list_directory(self, path: str = ".") -> str:
        # """
        # 디렉토리 목록 표시
        # 
        # Args:
        #     path: 목록을 표시할 경로
        #     
        # Returns:
        #     디렉토리 목록
        # """
        try:
            abs_path = os.path.abspath(path)
            
            if not os.path.exists(abs_path):
                return f"오류: 경로 '{path}'가 존재하지 않습니다."
            
            if not os.path.isdir(abs_path):
                return f"오류: '{path}'는 디렉토리가 아닙니다."
            
            result = f"디렉토리 목록: {abs_path}\n"
            result += "=" * 50 + "\n"
            
            items = []
            try:
                for item in os.listdir(abs_path):
                    item_path = os.path.join(abs_path, item)
                    if os.path.isdir(item_path):
                        items.append(f"📁 {item}/")
                    else:
                        size = os.path.getsize(item_path)
                        items.append(f"📄 {item} ({self._format_size(size)})")
                
                if items:
                    result += "\n".join(sorted(items))
                else:
                    result += "(빈 디렉토리)"
                    
            except PermissionError:
                result += "권한이 없어 접근할 수 없습니다."
                
            return result
            
        except Exception as e:
            return f"디렉토리 목록 조회 중 오류 발생: {str(e)}"
    
    async def get_current_directory(self) -> str:
        # """현재 작업 디렉토리 반환"""
        try:
            current_dir = os.getcwd()
            return f"현재 작업 디렉토리: {current_dir}"
        except Exception as e:
            return f"현재 디렉토리 조회 중 오류 발생: {str(e)}"
    
    def _decode_output(self, output: bytes) -> str:
        # """바이트 출력을 문자열로 디코딩"""
        if not output:
            return ""
        
        # 여러 인코딩 시도
        encodings = [self.default_encoding, 'utf-8', 'utf-16', 'latin1']
        
        for encoding in encodings:
            try:
                return output.decode(encoding).strip()
            except UnicodeDecodeError:
                continue
        
        # 모든 인코딩 실패 시 오류 무시하고 디코딩
        return output.decode(self.default_encoding, errors='ignore').strip()
    
    def _format_size(self, size: int) -> str:
        # """파일 크기를 읽기 쉬운 형태로 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"