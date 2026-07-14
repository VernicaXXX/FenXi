"""
project_analyzer.py - 项目分析器（性能优化版）

优化点：
1. 多线程并行处理文件（ThreadPoolExecutor）
2. frozenset 存储二进制扩展名（O(1)查找）
3. datetime 导入移到模块级别
4. heapq.nlargest 代替完整排序
"""
import os
import heapq
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils import get_language, count_lines, format_size, should_skip_dir


BINARY_EXTS = frozenset({
    '.pyc', '.pyo', '.exe', '.dll', '.so', '.dylib',
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.mp3', '.mp4', '.avi', '.mov', '.wav',
    '.db', '.sqlite', '.sqlite3', '.lock', '.git',
})


@dataclass
class FileInfo:
    path: str
    name: str
    language: str
    size_bytes: int
    code_lines: int
    modified_time: str


@dataclass
class ProjectAnalysisResult:
    root_path: str
    total_files: int
    total_dirs: int
    total_size_bytes: int
    total_code_lines: int
    total_comment_lines: int
    total_blank_lines: int
    language_stats: Dict[str, int]
    language_lines: Dict[str, int]
    files: List[FileInfo] = field(default_factory=list)
    largest_files: List[FileInfo] = field(default_factory=list)
    recently_modified: List[FileInfo] = field(default_factory=list)


class ProjectAnalyzer:
    def __init__(self, root_path: str, max_workers: int = 4):
        self.root_path = os.path.abspath(root_path)
        self.max_workers = max_workers

    def analyze(self, max_depth: int = 10) -> ProjectAnalysisResult:
        file_paths, total_dirs = [], 0
        for root, dirs, filenames in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]
            if root[len(self.root_path):].count(os.sep) > max_depth:
                continue
            total_dirs += len(dirs)
            for f in filenames:
                fp = os.path.join(root, f)
                if self._is_text_file(fp):
                    file_paths.append(fp)

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self._process_file, fp): fp for fp in file_paths}
            for f in as_completed(futures):
                r = f.result()
                if r: results.append(r)

        total_files = len(results)
        total_size = sum(r['size_bytes'] for r in results)
        total_code = sum(r['code_lines'] for r in results)
        total_comment = sum(r['comment_lines'] for r in results)
        total_blank = sum(r['blank_lines'] for r in results)

        lang_stats, lang_lines, file_infos = defaultdict(int), defaultdict(int), []
        for r in results:
            lang_stats[r['language']] += 1
            lang_lines[r['language']] += r['code_lines']
            file_infos.append(FileInfo(r['path'], r['name'], r['language'], r['size_bytes'], r['code_lines'], r['modified_time']))

        return ProjectAnalysisResult(
            self.root_path, total_files, total_dirs, total_size,
            total_code, total_comment, total_blank,
            dict(lang_stats), dict(lang_lines), file_infos,
            heapq.nlargest(10, file_infos, key=lambda f: f.code_lines),
            heapq.nlargest(10, file_infos, key=lambda f: f.modified_time)
        )

    def _process_file(self, fp: str) -> Optional[dict]:
        try:
            return {
                'path': fp, 'name': os.path.basename(fp),
                'language': get_language(fp),
                'size_bytes': os.path.getsize(fp),
                'code_lines': count_lines(fp)[0], 'comment_lines': count_lines(fp)[1], 'blank_lines': count_lines(fp)[2],
                'modified_time': datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M')
            }
        except: return None

    def _is_text_file(self, fp: str) -> bool:
        return os.path.splitext(fp)[1].lower() not in BINARY_EXTS

    def get_tree(self, max_depth: int = 3, max_files: int = 50) -> str:
        result = []
        def walk(p, prefix="", d=0):
            if d > max_depth: return
            try: items = sorted(os.listdir(p))
            except: return
            dirs = [i for i in items if os.path.isdir(os.path.join(p, i)) and not should_skip_dir(i)]
            files = [i for i in items if os.path.isfile(os.path.join(p, i))]
            if len(files) > max_files: files = files[:max_files] + [f"... ({len(items)-max_files} more)"]
            for i, d_ in enumerate(dirs):
                last = (i == len(dirs)-1) and not files
                result.append(f"{prefix}{'`-- ' if last else '|-- '}{d_}/")
                walk(os.path.join(p, d_), prefix + ("    " if last else "|   "), d+1)
            for i, f in enumerate(files):
                result.append(f"{prefix}{'`-- ' if i==len(files)-1 else '|-- '}{f}")
        result.append(os.path.basename(self.root_path) + "/")
        walk(self.root_path)
        return "\n".join(result)