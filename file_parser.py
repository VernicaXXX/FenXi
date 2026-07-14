"""
file_parser.py - 单文件解析器
解析单个代码文件，提取函数、类、统计信息
"""
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from utils import count_lines, get_language


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    line_number: int
    params: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    line_number: int
    methods: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class FileAnalysisResult:
    """文件分析结果"""
    file_path: str
    file_name: str
    language: str
    size_bytes: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    total_lines: int
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


class FileParser:
    """单文件解析器"""
    
    def __init__(self, file_path: str):
        self.file_path = os.path.abspath(file_path)
        self.file_name = os.path.basename(file_path)
        self.language = get_language(file_path)
        
    def parse(self) -> FileAnalysisResult:
        """解析文件并返回结果"""
        # 基础信息
        size_bytes = os.path.getsize(self.file_path)
        code_lines, comment_lines, blank_lines = count_lines(self.file_path)
        total_lines = code_lines + comment_lines + blank_lines
        
        # 解析代码结构（目前支持 Python）
        functions, classes, imports = self._parse_structure()
        
        return FileAnalysisResult(
            file_path=self.file_path,
            file_name=self.file_name,
            language=self.language,
            size_bytes=size_bytes,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            total_lines=total_lines,
            functions=functions,
            classes=classes,
            imports=imports
        )
    
    def _parse_structure(self) -> tuple:
        """解析代码结构（函数、类、导入）"""
        functions = []
        classes = []
        imports = []
        
        ext = os.path.splitext(self.file_path)[1].lower()
        
        if ext == '.py':
            functions, classes, imports = self._parse_python()
        elif ext in ('.js', '.ts'):
            functions, classes, imports = self._parse_javascript()
        elif ext == '.java':
            functions, classes, imports = self._parse_java()
        elif ext == '.go':
            functions, classes, imports = self._parse_go()
        elif ext == '.rs':
            functions, classes, imports = self._parse_rust()
        
        return functions, classes, imports
    
    def _parse_python(self) -> tuple:
        """解析 Python 文件"""
        functions = []
        classes = []
        imports = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except:
            return functions, classes, imports
        
        current_class = None
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 导入语句
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(stripped)
                continue
            
            # 类定义
            class_match = re.match(r'^class\s+(\w+)', stripped)
            if class_match:
                class_name = class_match.group(1)
                classes.append(ClassInfo(
                    name=class_name,
                    line_number=i,
                    methods=[]
                ))
                current_class = class_name
                continue
            
            # 函数定义
            func_match = re.match(r'^def\s+(\w+)\s*\(([^)]*)\)', stripped)
            if func_match:
                func_name = func_match.group(1)
                params_str = func_match.group(2)
                params = [p.strip().split('=')[0].strip() for p in params_str.split(',') if p.strip() and p.strip() != 'self']
                
                functions.append(FunctionInfo(
                    name=func_name,
                    line_number=i,
                    params=params
                ))
                
                if current_class and classes:
                    for cls in classes:
                        if cls.name == current_class:
                            cls.methods.append(func_name)
                
                continue
        
        return functions, classes, imports
    
    def _parse_javascript(self) -> tuple:
        """解析 JavaScript/TypeScript 文件"""
        functions = []
        classes = []
        imports = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return functions, classes, imports
        
        # 导入语句
        import_pattern = r'import\s+.*?from\s+[\'"][^\'"]+[\'"]|require\s*\([\'"][^\'"]+[\'"]\)'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(0))
        
        # 函数定义
        func_patterns = [
            r'function\s+(\w+)\s*\(',  # function name()
            r'const\s+(\w+)\s*=\s*\(',  # const name = ()
            r'let\s+(\w+)\s*=\s*\(',    # let name = ()
            r'(\w+)\s*:\s*function\s*\(',  # name: function()
        ]
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                functions.append(FunctionInfo(
                    name=match.group(1),
                    line_number=content[:match.start()].count('\n') + 1
                ))
        
        # 类定义
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            classes.append(ClassInfo(
                name=match.group(1),
                line_number=content[:match.start()].count('\n') + 1
            ))
        
        return functions, classes, imports
    
    def _parse_java(self) -> tuple:
        """解析 Java 文件"""
        functions, classes, imports = [], [], []
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return functions, classes, imports
        
        # import
        for m in re.finditer(r'import\s+[\w.]+;', content):
            imports.append(m.group(0))
        
        # class
        for m in re.finditer(r'class\s+(\w+)', content):
            classes.append(ClassInfo(name=m.group(1), line_number=content[:m.start()].count('\n')+1))
        
        # method
        for m in re.finditer(r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(', content):
            functions.append(FunctionInfo(name=m.group(1), line_number=content[:m.start()].count('\n')+1))
        
        return functions, classes, imports
    
    def _parse_go(self) -> tuple:
        """解析 Go 文件"""
        functions, classes, imports = [], [], []
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return functions, classes, imports
        
        # import
        for m in re.finditer(r'import\s+[\'"][^\'"]+[\'"]|import\s*\([^)]+\)', content):
            imports.append(m.group(0))
        
        # struct (as class)
        for m in re.finditer(r'type\s+(\w+)\s+struct', content):
            classes.append(ClassInfo(name=m.group(1), line_number=content[:m.start()].count('\n')+1))
        
        # func
        for m in re.finditer(r'func\s+(?:\([^)]+\)\s*)?(\w+)\s*\(', content):
            functions.append(FunctionInfo(name=m.group(1), line_number=content[:m.start()].count('\n')+1))
        
        return functions, classes, imports
    
    def _parse_rust(self) -> tuple:
        """解析 Rust 文件"""
        functions, classes, imports = [], [], []
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return functions, classes, imports
        
        # use
        for m in re.finditer(r'use\s+[\w:]+;', content):
            imports.append(m.group(0))
        
        # struct/enum (as class)
        for m in re.finditer(r'(?:struct|enum)\s+(\w+)', content):
            classes.append(ClassInfo(name=m.group(1), line_number=content[:m.start()].count('\n')+1))
        
        # fn
        for m in re.finditer(r'fn\s+(\w+)', content):
            functions.append(FunctionInfo(name=m.group(1), line_number=content[:m.start()].count('\n')+1))
        
        return functions, classes, imports
