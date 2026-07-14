"""
cli.py - 命令行入口
直接运行此文件进行交互式分析
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_analyzer import ProjectAnalyzer
from file_parser import FileParser
from reporter import Reporter


def print_banner():
    print("=" * 60)
    print("Code Analyzer - 本地代码分析器")
    print("=" * 60)
    print("支持：项目分析 / 单文件解析 / JSON 导出")
    print()


def print_help():
    print("可用命令：")
    print("  project <路径>    - 分析整个项目")
    print("  file <文件路径>   - 解析单个文件")
    print("  tree <路径>       - 显示目录树")
    print("  help              - 显示帮助")
    print("  exit              - 退出")
    print()


def interactive_mode():
    print_banner()
    print_help()
    
    while True:
        try:
            cmd = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出")
            break
        
        if not cmd:
            continue
        
        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        path = parts[1] if len(parts) > 1 else None
        
        if action == "project":
            if not path:
                print("用法: project <路径>")
                continue
            if not os.path.exists(path):
                print(f"路径不存在: {path}")
                continue
            
            print(f"\n正在分析项目: {path}\n")
            analyzer = ProjectAnalyzer(path)
            result = analyzer.analyze()
            Reporter.print_project_report(result)
            
            # 询问是否导出
            export = input("\n是否导出 JSON? (y/N): ").strip().lower()
            if export == 'y':
                output = os.path.join(path, "project_analysis.json")
                Reporter.export_json(result, output)
                print(f"已导出: {output}")
            print()
        
        elif action == "file":
            if not path:
                print("用法: file <文件路径>")
                continue
            if not os.path.exists(path):
                print(f"文件不存在: {path}")
                continue
            
            print(f"\n正在解析文件: {path}\n")
            parser = FileParser(path)
            result = parser.parse()
            Reporter.print_file_report(result)
            print()
        
        elif action == "tree":
            if not path:
                print("用法: tree <路径>")
                continue
            if not os.path.exists(path):
                print(f"路径不存在: {path}")
                continue
            
            analyzer = ProjectAnalyzer(path)
            tree = analyzer.get_tree()
            print(f"\n{tree}\n")
        
        elif action == "help":
            print_help()
        
        elif action == "exit":
            print("退出")
            break
        
        else:
            print(f"未知命令: {action}")
            print("输入 'help' 查看帮助")


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        
        if cmd == "project" and len(sys.argv) > 2:
            path = sys.argv[2]
            if os.path.exists(path):
                analyzer = ProjectAnalyzer(path)
                result = analyzer.analyze()
                Reporter.print_project_report(result)
            else:
                print(f"路径不存在: {path}")
        
        elif cmd == "file" and len(sys.argv) > 2:
            path = sys.argv[2]
            if os.path.exists(path):
                parser = FileParser(path)
                result = parser.parse()
                Reporter.print_file_report(result)
            else:
                print(f"文件不存在: {path}")
        
        elif cmd == "tree" and len(sys.argv) > 2:
            path = sys.argv[2]
            if os.path.exists(path):
                analyzer = ProjectAnalyzer(path)
                print(analyzer.get_tree())
            else:
                print(f"路径不存在: {path}")
        
        else:
            print("用法:")
            print("  python cli.py project <路径>")
            print("  python cli.py file <文件路径>")
            print("  python cli.py tree <路径>")
    
    else:
        interactive_mode()


if __name__ == "__main__":
    main()