import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import ast
import logging
from tqdm import tqdm


class CodeAnalyzer:
    """Analyzes code files and explains their functionality."""
    
    def __init__(self, file_path: str):
        """Initialize the analyzer with a file path."""
        self.file_path = Path(file_path)
        self.content = ""
        self.language = self._detect_language()
        
    def _detect_language(self) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React/JSX',
            '.tsx': 'React/TSX',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.xml': 'XML',
        }
        
        ext = self.file_path.suffix.lower()
        return extension_map.get(ext, 'Unknown')
    
    def read_file(self) -> str:
        """Read the file content."""
        try:
            if self.file_path.stat().st_size > 50_000_000:  # 50 MB limit
                return "File too large (must bot exceed 50 MB)"
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:   
                self.content = f.read()
            return self.content 
        except Exception as e:
            print(f"Error reading file {self.file_path}: {e}")
            return ""      
    
    def extract_summary(self) -> str:
        """Extract a summary of the file's purpose."""
        self.lines = self.content.splitlines()[:20]
        
        # Look for docstrings or comments at the top
        summary_lines = []
        in_docstring = False
        
        for line in self.lines:
            stripped = line.strip()
            
            # Python docstrings
            if self.language == 'Python':
                if '"""' in stripped or "'''" in stripped:
                    in_docstring = not in_docstring
                if in_docstring or stripped.startswith('#'):
                    if stripped and not stripped.startswith('"""') and not stripped.startswith("'''"):
                        summary_lines.append(stripped.lstrip('#').strip())
            
            # JavaScript/TypeScript comments
            elif self.language in ['JavaScript', 'TypeScript', 'React/JSX', 'React/TSX', 'Java', 'C++', 'C', 'C#']:
                if stripped.startswith('//'):
                    summary_lines.append(stripped.lstrip('//').strip())
                elif stripped.startswith('/*'):
                    summary_lines.append(stripped.lstrip('/*').strip())
        
        return ' '.join(summary_lines[:3]) if summary_lines else "Code file"
    
    def extract_functions_classes(self) -> List[Dict]:
        """Extract functions and classes from the code."""
        items = []
        lines = self.content.split('\n')
        
        if self.language == 'Python':
            for i, line in enumerate(lines):
                if re.match(r'^\s*def\s+\w+\s*\(', line):
                    func_name = line.split('(')[0].replace('def ', '').strip()
                    docstring = self._get_docstring(lines, i)
                    items.append({
                        'type': 'Function',
                        'name': func_name,
                        'line': i + 1,
                        'description': docstring
                    })
                elif line.lstrip().startswith('class '):
                    class_name = line.split('(')[0].split(':')[0].replace('class ', '').strip()
                    docstring = self._get_docstring(lines, i)
                    items.append({
                        'type': 'Class',
                        'name': class_name,
                        'line': i + 1,
                        'description': docstring
                    })
        
        elif self.language in ['JavaScript', 'TypeScript', 'React/JSX', 'React/TSX']:
            for i, line in enumerate(lines):
                if re.search(r'function\s+\w+\s*\(', line):
                    match = re.search(r'function\s+(\w+)', line)
                    if match:
                        func_name = match.group(1)
                        items.append({
                            'type': 'Function',
                            'name': func_name,
                            'line': i + 1,
                            'description': self._get_comment_above(lines, i)
                        })
                elif re.search(r'class\s+\w+', line):
                    match = re.search(r'class\s+(\w+)', line)
                    if match:
                        class_name = match.group(1)
                        items.append({
                            'type': 'Class',
                            'name': class_name,
                            'line': i + 1,
                            'description': self._get_comment_above(lines, i)
                        })
                elif re.search(r'const\s+\w+\s*=\s*\(.*\)\s*=>', line):
                    match = re.search(r'const\s+(\w+)', line)
                    if match:
                        func_name = match.group(1)
                        items.append({
                            'type': 'Arrow Function',
                            'name': func_name,
                            'line': i + 1,
                            'description': self._get_comment_above(lines, i)
                        })
        
        elif self.language == 'Java':
            for i, line in enumerate(lines):
                if re.search(r'public\s+(static\s+)?(\w+\s+)?(\w+)\s*\(', line):
                    match = re.search(r'(\w+)\s*\(', line)
                    if match:
                        func_name = match.group(1)
                        items.append({
                            'type': 'Method',
                            'name': func_name,
                            'line': i + 1,
                            'description': self._get_comment_above(lines, i)
                        })
        
        return items[:15]  # Return top 15
    
    def _get_docstring(self, lines: List[str], start_idx: int) -> str:
        """Extract docstring from Python code."""
        if start_idx + 1 < len(lines):
            next_line = lines[start_idx + 1].strip()
            if next_line.startswith('"""') or next_line.startswith("'''"):
                quote = '"""' if next_line.startswith('"""') else "'''"
                docstring = next_line.replace(quote, '').strip()
                return docstring[:100]
        return ""
    
    def _get_comment_above(self, lines: List[str], start_idx: int) -> str:
        """Extract comment above a line."""
        if start_idx > 0:
            prev_line = lines[start_idx - 1].strip()
            if prev_line.startswith('//'):
                return prev_line.lstrip('//').strip()[:100]
        return ""
    
    def get_analysis(self) -> Dict[str, object]:
        """Get complete analysis of the file."""
        self.read_file()
        
        return {
            'file': self.file_path.name,
            'language': self.language,
            'summary': self.extract_summary(),
            'size': len(self.content.split('\n')),
            'items': self.extract_functions_classes(),
            'preview': '\n'.join(self.content.split('\n')[:30])
        }


class ReadmeGenerator:
    """Bot that generates README files for coding projects."""
    
    def __init__(self, project_path: str):
        """Initialize the bot with a project path."""
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        self.file_structure = {}
        self.project_type = None
        self.description = ""
        self.code_files = []
        
    def get_all_code_files(self) -> List[Path]:
        """Get all code files in the project."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',
            '.cpp', '.c', '.cs', '.rb', '.php', '.h', '.hpp', '.json',
            '.yaml', '.yml', '.toml', '.xml', '.html', '.css'
        }
        
        code_files = []
        ignored_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.env'}
        
        for root, dirs, files in os.walk(self.project_path):
            # Remove ignored directories from walk
            dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith('.')]
            
            for file in files:
                if Path(file).suffix in code_extensions:
                    full_path = Path(root) / file
                    code_files.append(full_path)
        
        return sorted(code_files)
        
    def scan_project(self) -> Dict:
        """Scan the project directory and extract information."""
        logging.info(f"🔍 Scanning project: {self.project_name}")
        
        # Detect project type
        self.project_type = self._detect_project_type()
        logging.info(f"📦 Project type detected: {self.project_type}")
        
        # Get project structure
        self.file_structure = self._get_directory_structure()
        self.code_files = self.get_all_code_files()

        # Extract information
        info = {
            "name": self.project_name,
            "type": self.project_type,
            "structure": self.file_structure,
            "files": self._get_important_files(),
            "dependencies": self._extract_dependencies(),
            "description": self._extract_description()
        }
        
        return info
    
    def _detect_project_type(self) -> str:
        """Detect the project type based on key files."""
        indicators = {
            "Python": ["setup.py", "requirements.txt", "pyproject.toml", "Pipfile", "*.py"],
            "Node.js": ["package.json", "npm-shrinkwrap.json", "yarn.lock"],
            "Go": ["go.mod", "go.sum"],
            "Rust": ["Cargo.toml", "Cargo.lock"],
            "Java": ["pom.xml", "build.gradle", "*.jar"],
            "C#/.NET": ["*.csproj", "*.sln"],
            "Ruby": ["Gemfile", "Rakefile"],
            ".NET": ["*.csproj", ".sln"]
        }
        
        for lang, files in indicators.items():
            for file_pattern in files:
                if "*" in file_pattern:
                    # Check for wildcard patterns
                    extension = file_pattern.replace("*", "")
                    if any(f.endswith(extension) for f in os.listdir(self.project_path)):
                        return lang
                elif (self.project_path / file_pattern).exists():
                    return lang
        
        # Check for common project files
        repo_files = os.listdir(self.project_path)
        if any("test" in f.lower() for f in repo_files):
            return "Generic Project"
        
        return "Unknown"
    
    def _get_directory_structure(self, path: Optional[Path] = None, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> str:
        """Generate a tree representation of directory structure."""
        if path is None:
            path = self.project_path
        
        if current_depth >= max_depth:
            return ""
        
        structure = ""
        try:
            items = sorted(os.listdir(path))
            # Filter out common ignored directories
            ignored = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.env', 'dist', 'build'}
            items = [item for item in items if item not in ignored and not item.startswith('.')]
            
            for i, item in enumerate(items[:20]):  # Limit to 20 items per directory
                item_path = path / item
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                structure += f"{prefix}{current_prefix}{item}\n"
                
                if os.path.isdir(item_path) and current_depth < max_depth - 1:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    structure += self._get_directory_structure(item_path, next_prefix, max_depth, current_depth + 1)
        except PermissionError:
            pass
        
        return structure
    
    def _get_important_files(self) -> List[str]:
        """Find important configuration and documentation files."""
        important_patterns = [
            "README*", "LICENSE*", "CONTRIBUTING*", "setup.py", "package.json",
            "requirements.txt", "Dockerfile", "docker-compose.yml", ".github",
            "pyproject.toml", "Gemfile", "go.mod", "Cargo.toml", "pom.xml"
        ]
        
        found_files = []
        for pattern in important_patterns:
            for root, dirs, files in os.walk(self.project_path):
                # Skip hidden and ignored directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for file in files:
                    if self._match_pattern(file, pattern):
                        rel_path = os.path.relpath(os.path.join(root, file), self.project_path)
                        if rel_path not in found_files:
                            found_files.append(rel_path)
        
        return found_files[:10]  # Return top 10
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern (supports * wildcards)."""
        pattern = pattern.replace("*", ".*")
        return bool(re.match(f"^{pattern}$", filename, re.IGNORECASE))
    
    def _extract_dependencies(self) -> List[str]:
        """Extract project dependencies."""
        dependencies = []
        
        # Check for requirements.txt (Python)
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    dependencies.extend(deps[:5])  # First 5 dependencies
            except Exception:
                pass
        
        # Check for package.json (Node.js)
        pkg_file = self.project_path / "package.json"
        if pkg_file.exists():
            try:
                import json
                with open(pkg_file, 'r') as f:
                    data = json.load(f)
                    if 'dependencies' in data:
                        dependencies.extend(list(data['dependencies'].keys())[:5])
            except Exception:
                pass
        
        return dependencies
    
    def _extract_description(self) -> str:
        """Extract description from README or setup files."""
        description = ""
        
        # Try to read existing README
        for readme in ["README.md", "README.rst", "README.txt", "README"]:
            readme_path = self.project_path / readme
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Extract first meaningful paragraph
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        for line in lines:
                            if line and not line.startswith('#'):
                                description = line[:150]
                                break
                    if description:
                        break
                except Exception:
                    pass
        
        return description
    
    def generate_readme(self) -> str:
        """Generate README content."""
        print("📝 Generating README...")
        
        info = self.scan_project()
        
        # Build README content
        readme_content = f"""# {info['name']}

## Overview
{info['description'] if info['description'] else f"A {info['type']} project."}

## Project Type

{info['type']}

## 📁 Project Structure

```
{self.project_name}/
{self._get_directory_structure()}
```

## 🛠️ Technologies & Dependencies

"""
        
        if info['dependencies']:
            readme_content += "### Key Dependencies\n"
            for dep in info['dependencies'][:5]:
                readme_content += f"- {dep}\n"
        
        readme_content += f"""
## 🚀 Getting Started

### Prerequisites
- Ensure you have the necessary tools installed for {info['type']} development

### Installation

"""
        
        if info['type'] == "Python":
            readme_content += f"""```bash
git clone <repository-url>
cd {self.project_name}
pip install -r requirements.txt
```
"""
        elif info['type'] == "Node.js":
            readme_content += """```bash
git clone <repository-url>
cd {project_name}
npm install
```
"""
        else:
            readme_content += f"""```bash
git clone <repository-url>
cd {self.project_name}
# Follow the build instructions for {info['type']}
```
"""
        
        readme_content += """
### Running the Project

Provide instructions on how to run your project here.

```bash
# Example command
```

## 📚 Important Files

"""
        
        for file in info['files'][:8]:
            readme_content += f"- `{file}`\n"
        
        readme_content += """
## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For questions or suggestions, please open an issue on the repository.

---

*README generated by Bot*
"""
        
        return readme_content
    
    def save_readme(self, filename: str = "README.md") -> None:
        """Save the generated README to a file."""
        content = self.generate_readme()
        output_path = self.project_path / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ README saved to: {output_path}")
    
    def generate_file_readmes(self, output_dir: str = "FILE_DOCS") -> None:
        """Generate individual README files for each code file with explanations."""
        print(f"\n🔄 Analyzing {len(self.code_files)} code files...")
        
        # Create output directory
        output_path = self.project_path / output_dir
        output_path.mkdir(exist_ok=True)
        
        # Analyze each code file
        for i, code_file in enumerate(self.code_files, 1):
            try:
                analyzer = CodeAnalyzer(str(code_file))
                analysis = analyzer.get_analysis()
                
                # Generate readme for this file
                file_readme = self._create_file_readme(code_file, analysis)
                
                # Save with sanitized filename
                relative_path = code_file.relative_to(self.project_path)
                safe_name = str(relative_path).replace('/', '_').replace('\\', '_')
                output_file = output_path / f"{safe_name}.md"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(file_readme)
                
                print(f"  [{i}/{len(self.code_files)}] ✅ {relative_path} → {safe_name}.md")
            
            except Exception as e:
                print(f"  [{i}/{len(self.code_files)}] ❌ Error processing {code_file}: {e}")
        
        print(f"\n✅ Generated {len(self.code_files)} file documentation in '{output_dir}/' folder")
    
    def _create_file_readme(self, file_path: Path, analysis: Dict) -> str:
        """Create a detailed README for a single code file."""
        relative_path = file_path.relative_to(self.project_path)
        
        readme = f"""# {analysis['file']} - Code Documentation

## 📄 File Information

- **Location:** `{relative_path}`
- **Language:** {analysis['language']}
- **Lines of Code:** {analysis['size']}
- **Purpose:** {analysis['summary'] if analysis['summary'] else 'Code file'}

---

## 📋 Overview

This file is a {analysis['language']} module that contains various functionality. Below is a detailed breakdown of all the functions and classes defined in this file.

---

## 🔧 Components

### Functions & Classes

"""
        
        if analysis['items']:
            for item in analysis['items']:
                readme += f"\n#### `{item['name']}` ({item['type']})\n"
                readme += f"- **Line:** {item['line']}\n"
                if item['description']:
                    readme += f"- **Description:** {item['description']}\n"
                readme += "\n"
        else:
            readme += "No functions or classes found.\n\n"
        
        # Add code preview
        readme += f"""
---

## 📝 Code Preview (First 30 lines)

```{analysis['language'].lower()}
{analysis['preview']}
```

---

## 💡 Key Concepts

- **Language:** {analysis['language']}
- **File Type:** {"Configuration" if analysis['language'] in ['JSON', 'YAML', 'TOML', 'XML'] else "Source Code"}
- **Complexity:** {"High" if analysis['size'] > 500 else "Medium" if analysis['size'] > 100 else "Low"}

---

## 🔗 Dependencies

Check the imports and dependencies at the top of this file to understand what external libraries are used.

---

## 📚 Related Files

Other files in this project may depend on or be related to this file. Check other documentation files to understand the complete picture.

---

*Documentation generated automatically by README Bot*
"""
        
        return readme


def main():
    """Main function to run the bot."""
    print("🤖 README Generator Bot")
    print("=" * 50)
    
    # Get project path from user
    project_path = input("Enter the path to your project (or press Enter for current directory): ").strip()
    if not project_path:
        project_path = "."
    
    # Validate path
    if not os.path.isdir(project_path):
        print(f"❌ Error: '{project_path}' is not a valid directory.")
        return
    
    # Generate README
    try:
        generator = ReadmeGenerator(project_path)
        
        # Get all code files
        generator.code_files = generator.get_all_code_files()
        
        print(f"\n📁 Found {len(generator.code_files)} code files")
        
        # Show menu
        print("\n" + "=" * 50)
        print("What would you like to do?")
        print("1. Generate main project README")
        print("2. Generate individual file documentation")
        print("3. Generate both")
        print("=" * 50)
        
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice in ['1', '3']:
            # Generate main README
            readme_content = generator.generate_readme()
            print("\nPreview of main README:\n")
            print(readme_content[:500] + "...\n")
            
            save = input("Save main README? (y/n): ").strip().lower()
            if save == 'y':
                generator.save_readme()
        
        if choice in ['2', '3']:
            # Generate file documentation
            gen_docs = input("\nGenerate individual file documentation? (y/n): ").strip().lower()
            if gen_docs == 'y':
                custom_dir = input("Enter output directory name (default: FILE_DOCS): ").strip()
                output_dir = custom_dir if custom_dir else "FILE_DOCS"
                generator.generate_file_readmes(output_dir)
        
        print("\n✅ Done!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
