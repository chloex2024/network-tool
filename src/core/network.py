"""网络操作相关功能"""
import socket
import platform
import subprocess
from typing import Tuple, List, Optional
from ..config.settings import PING_COUNT, SOCKET_TIMEOUT

class NetworkOperations:
    @staticmethod
    def ping(host: str) -> Tuple[bool, str]:
        """执行ping操作"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, str(PING_COUNT), host]
            
            process = subprocess.Popen(command, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            output, error = process.communicate()
            
            if error:
                return False, error.decode('gbk', 'ignore')
            return True, output.decode('gbk' if platform.system().lower() == 'windows' 
                                    else 'utf-8')
        except Exception as e:
            return False, str(e)

    @staticmethod
    def resolve_dns(domain: str) -> Tuple[bool, dict]:
        """DNS解析"""
        try:
            result = socket.gethostbyname_ex(domain)
            return True, {
                "hostname": result[0],
                "aliases": result[1],
                "addresses": result[2]
            }
        except Exception as e:
            return False, {"error": str(e)}

    @staticmethod
    def scan_port(host: str, port: int, protocol: str) -> Tuple[bool, str]:
        """端口扫描"""
        try:
            if protocol == "TCP":
                return NetworkOperations._scan_tcp_port(host, port)
            else:
                return NetworkOperations._scan_udp_port(host, port)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _scan_tcp_port(host: str, port: int) -> Tuple[bool, str]:
        """TCP端口扫描"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(SOCKET_TIMEOUT)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                return True, f"TCP 端口 {port} 状态: 开放"
            return False, f"TCP 端口 {port} 状态: 关闭"
        finally:
            sock.close()

    @staticmethod
    def _scan_udp_port(host: str, port: int) -> Tuple[bool, str]:
        """UDP端口扫描"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(SOCKET_TIMEOUT)
        try:
            sock.sendto(b"", (host, port))
            data, addr = sock.recvfrom(1024)
            return True, f"UDP 端口 {port} 状态: 开放 (收到响应)"
        except socket.timeout:
            return False, f"UDP 端口 {port} 状态: 可能开放 (无响应)"
        except Exception as e:
            return False, f"UDP 端口 {port} 状态: 可能关闭 ({str(e)})"
        finally:
            sock.close() 