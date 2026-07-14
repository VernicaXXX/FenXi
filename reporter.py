"""
reporter.py - 报告生成器
生成终端报告和 JSON 导出
"""
import json
import os
from typing import Optional
from datetime import datetime

from project_analyzer import ProjectAnalysisResult
from file_parser import FileAnalysisResult
from utils import format_size


class Reporter:
    """报告生成器"""
    
    @staticmethod
    def print_project_report(result: ProjectAnalysisResult):
        """打印项目分析报告"""
        print("=" * 60)
        print("[项目分析报告]")
        print("=" * 60)
        print(f"路径: {result.root_path}")
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("[总体统计]")
        print("-" * 40)
        print(f"  文件数: {result.total_files}")
        print(f"  目录数: {result.total_dirs}")
        print(f"  总大小: {format_size(result.total_size_bytes)}")
        print(f"  代码行数: {result.total_code_lines}")
        print(f"  注释行数: {result.total_comment_lines}")
        print(f"  空行数: {result.total_blank_lines}")
        print()
        
        # 语言分布
        if result.language_stats:
            print("[语言分布]")
            print("-" * 40)
            sorted_langs = sorted(result.language_stats.items(), key=lambda x: x[1], reverse=True)
            for lang, count in sorted_langs[:10]:
                lines = result.language_lines.get(lang, 0)
                print(f"  {lang}: {count} 文件, {lines} 行代码")
            print()
        
        # 最大文件
        if result.largest_files:
            print("[代码行数 Top 10]")
            print("-" * 40)
            for i, f in enumerate(result.largest_files, 1):
                rel_path = f.path.replace(result.root_path, "").lstrip(os.sep)
                print(f"  {i}. {f.name} ({f.code_lines} 行) [{f.language}]")
            print()
        
        # 最近修改
        if result.recently_modified:
            print("[最近修改]")
            print("-" * 40)
            for f in result.recently_modified[:5]:
                print(f"  {f.modified_time}  {f.name}")
            print()
        
        print("=" * 60)
    
    @staticmethod
    def print_file_report(result: FileAnalysisResult):
        """打印文件分析报告"""
        print("=" * 60)
        print("[文件分析报告]")
        print("=" * 60)
        print(f"文件: {result.file_name}")
        print(f"路径: {result.file_path}")
        print(f"语言: {result.language}")
        print()
        
        print("[基本信息]")
        print("-" * 40)
        print(f"  文件大小: {format_size(result.size_bytes)}")
        print(f"  总行数: {result.total_lines}")
        print(f"  代码行数: {result.code_lines}")
        print(f"  注释行数: {result.comment_lines}")
        print(f"  空行数: {result.blank_lines}")
        print()
        
        # 导入语句
        if result.imports:
            print(f"[导入语句] ({len(result.imports)} 个)")
            print("-" * 40)
            for imp in result.imports[:10]:
                print(f"  {imp}")
            if len(result.imports) > 10:
                print(f"  ... 还有 {len(result.imports) - 10} 个")
            print()
        
        # 类
        if result.classes:
            print(f"[类定义] ({len(result.classes)} 个)")
            print("-" * 40)
            for cls in result.classes:
                methods_str = f" -> {', '.join(cls.methods[:3])}" if cls.methods else ""
                more = f" (+{len(cls.methods) - 3})" if len(cls.methods) > 3 else ""
                print(f"  {cls.name} (行 {cls.line_number}){methods_str}{more}")
            print()
        
        # 函数
        if result.functions:
            print(f"[函数定义] ({len(result.functions)} 个)")
            print("-" * 40)
            for func in result.functions[:15]:
                params_str = f"({', '.join(func.params)})" if func.params else "()"
                print(f"  {func.name}{params_str} (行 {func.line_number})")
            if len(result.functions) > 15:
                print(f"  ... 还有 {len(result.functions) - 15} 个")
            print()
        
        print("=" * 60)
    
    @staticmethod
    def export_json(data, output_path: str) -> str:
        """导出为 JSON 文件"""
        def dataclass_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: v for k, v in vars(obj).items()}
            elif isinstance(obj, list):
                return [dataclass_to_dict(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: dataclass_to_dict(v) for k, v in obj.items()}
            return obj
        
        result = dataclass_to_dict(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return output_path
