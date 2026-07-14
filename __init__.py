"""
code_analyzer - 本地代码分析器

功能：
- 分析整个项目目录
- 解析单个代码文件
- 生成报告（终端 + JSON）

使用示例：
    from code_analyzer import ProjectAnalyzer, FileParser, Reporter
    
    # 分析项目
    analyzer = ProjectAnalyzer("E:/my_project")
    result = analyzer.analyze()
    Reporter.print_project_report(result)
    
    # 解析文件
    parser = FileParser("E:/my_project/main.py")
    info = parser.parse()
    Reporter.print_file_report(info)
"""

from .utils import (
    get_language,
    count_lines,
    format_size,
    should_skip_dir,
    LANGUAGE_MAP,
    SKIP_DIRS,
)

from .file_parser import (
    FileParser,
    FileAnalysisResult,
    FunctionInfo,
    ClassInfo,
)

from .project_analyzer import (
    ProjectAnalyzer,
    ProjectAnalysisResult,
    FileInfo,
)

from .reporter import Reporter

__version__ = "1.0.0"
__all__ = [
    # 主要接口
    "ProjectAnalyzer",
    "FileParser",
    "Reporter",
    # 结果类
    "ProjectAnalysisResult",
    "FileAnalysisResult",
    "FileInfo",
    "FunctionInfo",
    "ClassInfo",
    # 工具函数
    "get_language",
    "count_lines",
    "format_size",
    "should_skip_dir",
]
