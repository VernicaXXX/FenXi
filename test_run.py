"""
测试脚本 - 分析指定文件或项目
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_parser import FileParser
from project_analyzer import ProjectAnalyzer
from reporter import Reporter

# 测试：解析单个文件
print("=" * 60)
print("测试：解析 main.py")
print("=" * 60)

file_path = r"E:\test_guiji - LH\main.py"
parser = FileParser(file_path)
result = parser.parse()
Reporter.print_file_report(result)

# 测试：分析项目
print("\n")
print("=" * 60)
print("测试：分析 test_guiji 项目")
print("=" * 60)

project_path = r"E:\test_guiji - LH"
analyzer = ProjectAnalyzer(project_path)
project_result = analyzer.analyze()
Reporter.print_project_report(project_result)