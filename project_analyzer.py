"""
project_analyzer.py - 项目分析器
扫描整个项目目录，统计文件、代码量、语言分布等
"""
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from utils import get_language, count_lines, format_size, should_skip_dir
from file_parser import FileParser, FileAnalysisResult


@dataclass
class FileInfo:
    """文件简要信息"""
    path: str
    name: str
    language: str
    size_bytes: int
    code_lines: int
    modified_time: str


@dataclass
class ProjectAnalysisResult:
    """项目分析结果"""
    root_path: str
    total_files: int
    total_dirs: int
    total_size_bytes: int
    total_code_lines: int
    total_comment_lines: int
    total_blank_lines: int
    language_stats: Dict[str, int]  # 语言 -> 文件数
    language_lines: Dict[str, int]  # 语言 -> 代码行数
    files: List[FileInfo] = field(default_factory=list)
    largest_files: List[FileInfo] = field(default_factory=list)
    recently_modified: List[FileInfo] = field(default_factory=list)


class ProjectAnalyzer:
    """项目分析器"""
    
    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)
    
    def analyze(self, max_depth: int = 10) -> ProjectAnalysisResult:
        """分析项目"""
        total_files = 0
        total_dirs = 0
        total_size = 0
        total_code = 0
        total_comment = 0
        total_blank = 0
        language_stats = defaultdict(int)
        language_lines = defaultdict(int)
        files = []
        
        for root, dirs, filenames in os.walk(self.root_path):
            # 过滤要跳过的目录
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]
            
            depth = root[len(self.root_path):].count(os.sep)
            if depth > max_depth:
                continue
            
            total_dirs += len(dirs)
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                # 跳过二进制文件等
                if not self._is_text_file(file_path):
                    continue
                
                total_files += 1
                
                # 获取文件信息
                try:
                    size_bytes = os.path.getsize(file_path)
                    total_size += size_bytes
                    
                    mod_time = os.path.getmtime(file_path)
                    from datetime import datetime
                    mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
                    
                    language = get_language(file_path)
                    language_stats[language] += 1
                    
                    code_lines, comment_lines, blank_lines = count_lines(file_path)
                    total_code += code_lines
                    total_comment += comment_lines
                    total_blank += blank_lines
                    language_lines[language] += code_lines
                    
                    file_info = FileInfo(
                        path=file_path,
                        name=filename,
                        language=language,
                        size_bytes=size_bytes,
                        code_lines=code_lines,
                        modified_time=mod_time_str
                    )
                    files.append(file_info)
                    
                except Exception as e:
                    continue
        
        # 排序：最大的文件
        largest_files = sorted(files, key=lambda f: f.code_lines, reverse=True)[:10]
        
        # 排序：最近修改
        recently_modified = sorted(files, key=lambda f: f.modified_time, reverse=True)[:10]
        
        return ProjectAnalysisResult(
            root_path=self.root_path,
            total_files=total_files,
            total_dirs=total_dirs,
            total_size_bytes=total_size,
            total_code_lines=total_code,
            total_comment_lines=total_comment,
            total_blank_lines=total_blank,
            language_stats=dict(language_stats),
            language_lines=dict(language_lines),
            files=files,
            largest_files=largest_files,
            recently_modified=recently_modified
        )
    
    def _is_text_file(self, file_path: str) -> bool:
        """判断是否为文本文件"""
        # 跳过常见二进制文件
        binary_ext = {
            '.pyc', '.pyo', '.exe', '.dll', '.so', '.dylib',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.tar', '.gz', '.rar', '.7z',
            '.mp3', '.mp4', '.avi', '.mov', '.wav',
            '.db', '.sqlite', '.sqlite3',
        }
        ext = os.path.splitext(file_path)[1].lower()
        return ext not in binary_ext
    
    def get_tree(self, max_depth: int = 3, max_files: int = 50) -> str:
        """生成目录树"""
        result = []
        
        def walk(path: str, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            
            try:
                items = sorted(os.listdir(path))
            except:
                return
            
            dirs = [i for i in items if os.path.isdir(os.path.join(path, i)) and not should_skip_dir(i)]
            files = [i for i in items if os.path.isfile(os.path.join(path, i))]
            
            # 限制文件数量
            if len(files) > max_files:
                files = files[:max_files]
                files.append(f"... ({len(items) - max_files} more)")
            
            for i, d in enumerate(dirs):
                is_last = (i == len(dirs) - 1) and not files
                result.append(f"{prefix}{'└── ' if is_last else '├── '}{d}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                walk(os.path.join(path, d), new_prefix, depth + 1)
            
            for i, f in enumerate(files):
                is_last = i == len(files) - 1
                result.append(f"{prefix}{'└── ' if is_last else '├── '}{f}")
        
        result.append(os.path.basename(self.root_path) + "/")
        walk(self.root_path)
        
        return "\n".join(result)