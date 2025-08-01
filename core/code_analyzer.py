# core/code_analyzer.py
import os
import logging
import shutil
from pathlib import Path
from datetime import datetime

class CodeAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.modifiable_files = [
            "core/agent.py",
            "core/speech_to_text.py", 
            "core/text_to_speech.py",
            "memory/user_profile.py",
            "models/local_llm.py"
        ]
    
    def analyze_code_structure(self):
        analysis = {
            "files": {},
            "total_lines": 0,
            "functions": 0,
            "classes": 0,
            "potential_issues": []
        }
        
        for file_path in self.modifiable_files:
            if Path(file_path).exists():
                file_data = self._analyze_file(file_path)
                analysis["files"][file_path] = file_data
                analysis["total_lines"] += file_data.get("lines", 0)
                analysis["functions"] += len(file_data.get("functions", []))
                analysis["classes"] += len(file_data.get("classes", []))
        
        analysis["potential_issues"] = self._detect_issues(analysis)
        return analysis
    
    def _analyze_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            return {
                "path": file_path,
                "lines": len(lines),
                "size": len(content),
                "functions": self._count_functions(content),
                "classes": self._count_classes(content),
                "comments": content.count('#')
            }
            
        except Exception as e:
            return {"path": file_path, "error": str(e)}
    
    def _count_functions(self, content):
        functions = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') and ':' in line:
                func_name = line.split('def ')[1].split('(')[0].strip()
                functions.append({"name": func_name, "line": i+1})
        return functions
    
    def _count_classes(self, content):
        classes = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('class ') and ':' in line:
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append({"name": class_name, "line": i+1})
        return classes
    
    def _detect_issues(self, analysis):
        issues = []
        
        for file_path, file_data in analysis["files"].items():
            if "error" not in file_data:
                if file_data.get("lines", 0) > 500:
                    issues.append(f"Arquivo {file_path} muito grande ({file_data['lines']} linhas)")
                
                if file_data.get("comments", 0) < 5:
                    issues.append(f"Arquivo {file_path} tem poucos comentários")
        
        return issues
    
    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        for file_path in self.modifiable_files:
            if Path(file_path).exists():
                backup_file = backup_path / file_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_file)
        
        return str(backup_path)
