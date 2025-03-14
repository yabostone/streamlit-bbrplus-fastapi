import subprocess
import os
from typing import Tuple, Optional

class PathConverter:
    @staticmethod
    def to_wsl_path(windows_path: str) -> str:
        """将Windows路径转换为WSL路径"""
        if not windows_path:
            return ""
        
        # 移除驱动器号并替换反斜杠
        path = windows_path.replace("\\", "/")
        if ":" in path:
            drive, path = path.split(":", 1)
            return f"/mnt/{drive.lower()}{path}"
        return path

    @staticmethod
    def to_windows_path(wsl_path: str) -> str:
        """将WSL路径转换为Windows路径"""
        if not wsl_path.startswith("/mnt/"):
            return wsl_path
        
        # 提取驱动器号和路径
        parts = wsl_path[5:].split("/", 1)
        if len(parts) < 2:
            return wsl_path
        
        drive, path = parts
        return f"{drive.upper()}:/{path}"

class WSLExecutor:
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.path_converter = PathConverter()

    def execute_ansible(self, command: str) -> Tuple[bool, str]:
        """
        在WSL中执行Ansible命令
        
        Args:
            command: Ansible命令字符串
        
        Returns:
            Tuple[bool, str]: (是否成功, 输出结果)
        """
        try:
            # 转换命令中的路径
            wsl_command = self._convert_paths_in_command(command)
            
            # 构建完整的WSL命令
            full_command = f'wsl bash -c "{wsl_command}"'
            
            # 执行命令
            self.process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            
            # 等待命令执行完成
            stdout, stderr = self.process.communicate(timeout=self.timeout)
            
            # 检查执行结果
            if self.process.returncode != 0:
                return False, stderr or stdout
            
            return True, stdout
            
        except subprocess.TimeoutExpired:
            self._kill_process()
            return False, "命令执行超时"
        except Exception as e:
            self._kill_process()
            return False, f"执行出错: {str(e)}"

    def _convert_paths_in_command(self, command: str) -> str:
        """转换命令中的Windows路径为WSL路径"""
        parts = command.split()
        converted_parts = []
        
        for part in parts:
            if os.path.sep in part or ":" in part:
                # 可能是路径，尝试转换
                converted_part = self.path_converter.to_wsl_path(part)
                converted_parts.append(converted_part)
            else:
                converted_parts.append(part)
        
        return " ".join(converted_parts)

    def _kill_process(self):
        """终止当前进程"""
        if self.process:
            try:
                self.process.kill()
            except:
                pass

    def close(self):
        """清理资源"""
        self._kill_process()