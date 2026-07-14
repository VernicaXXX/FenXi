"""
utils.py - 工具函数
提供代码统计、语言识别等公共功能
"""
import os
from typing import Tuple


# 语言识别映射
LANGUAGE_MAP = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.hpp': 'C++ Header',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.json': 'JSON',
    '.xml': 'XML',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sql': 'SQL',
    '.sh': 'Shell',
    '.bat': 'Batch',
    '.md': 'Markdown',
    '.txt': 'Text',
}

# 跳过的目录
SKIP_DIRS = {
    '__pycache__', '.git', '.svn', '.hg', 'node_modules',
    'venv', '.venv', 'env', '.env', 'dist', 'build', '.idea', '.vscode'
}


def get_language(file_path: str) -> str:
    """根据文件扩展名识别语言"""
    ext = os.path.splitext(file_path)[1].lower()
    return LANGUAGE_MAP.get(ext, 'Unknown')


def count_lines(file_path: str) -> Tuple[int, int, int]:
    """
    统计文件行数
    返回: (代码行数, 注释行数, 空行数)
    """
    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return (0, 0, 0)
    
    in_multiline_comment = False
    
    for line in lines:
        stripped = line.strip()
        
        # 空行
        if not stripped:
            blank_lines += 1
            continue
        
        # Python 多行注释
        if ext == '.py':
            if in_multiline_comment:
                comment_lines += 1
                if '"""' in stripped or "'''" in stripped:
                    in_multiline_comment = False
                continue
            
            if stripped.startswith('"""') or stripped.startswith("'''"):
                comment_lines += 1
                if stripped.count('"""') == 1 and stripped.count("'''") == 0:
                    in_multiline_comment = True
                continue
        
        # 单行注释
        if ext == '.py' and stripped.startswith('#'):
            comment_lines += 1
            continue
        if ext in ('.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs', '.swift', '.kt', '.scala', '.cs', '.php'):
            if stripped.startswith('//'):
                comment_lines += 1
                continue
        
        code_lines += 1
    
    return (code_lines, comment_lines, blank_lines)


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / 1024 / 1024:.1f} MB"


def should_skip_dir(dir_name: str) -> bool:
    """判断是否跳过该目录"""
    return dir_name in SKIP_DIRS or dir_name.startswith('.')
