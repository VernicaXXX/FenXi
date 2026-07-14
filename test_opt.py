import sys
sys.path.insert(0, '.')
from project_analyzer import ProjectAnalyzer
from reporter import Reporter
a = ProjectAnalyzer('.')
r = a.analyze()
Reporter.print_project_report(r)
# 测试导出
Reporter.export_json(r)