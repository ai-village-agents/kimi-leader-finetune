#!/usr/bin/env python3
import os
import sys
import ast

def lint_file(filepath):
    errors = []
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Rule 1: Single trailing newline
    if not content.endswith("\n"):
        errors.append("File does not end with a newline.")
    elif content.endswith("\n\n"):
        errors.append("File ends with multiple blank lines/newlines.")
        
    # Rule 2: No TODO comments
    for i, line in enumerate(content.splitlines(), 1):
        if "todo" in line.lower():
            errors.append(f"Line {i}: Found 'TODO' comment: '{line.strip()}'")
            
    # Rule 3: Public classes and functions/methods must have docstrings
    try:
        root = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        errors.append(f"Syntax error during AST parsing: {e}")
        return errors

    for node in ast.walk(root):
        if isinstance(node, ast.ClassDef):
            # Check public class
            if not node.name.startswith("_"):
                doc = ast.get_docstring(node)
                if not doc or not doc.strip():
                    errors.append(f"Class '{node.name}' is missing a docstring.")
                
                # Check public methods inside public class
                for subnode in node.body:
                    if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not subnode.name.startswith("_"):
                            subdoc = ast.get_docstring(subnode)
                            if not subdoc or not subdoc.strip():
                                errors.append(f"Method '{node.name}.{subnode.name}' is missing a docstring.")
                                
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # This handles top-level functions (not inside classes, as we traverse globally)
            # Since ast.walk traverses everything, we should check if this is top-level.
            # However, checking parent node is a bit tricky with simple ast.walk.
            # We can check if it is public and lacks a docstring. If it's a method of a private class
            # or a helper function, we can relax it if needed, but for simplicity, let's check top-level public functions.
            # To distinguish top-level functions from class methods, we can parse manually or just check all public functions.
            # Let's check all public functions. If any public function lacks a docstring, we report it.
            # To be safe, we will walk the top-level body of the module for functions.
            pass

    # Specifically check top-level functions
    for node in root.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                doc = ast.get_docstring(node)
                if not doc or not doc.strip():
                    errors.append(f"Top-level function '{node.name}' is missing a docstring.")

    return errors

def main():
    target_dir = "/home/computeruse/kimi-leader-finetune/ai_village_toolkit"
    all_passed = True
    print(f"[*] Starting Toolkit Linter on: {target_dir}")
    print("=" * 60)
    
    for root_dir, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                filepath = os.path.join(root_dir, file)
                rel_path = os.path.relpath(filepath, start="/home/computeruse/kimi-leader-finetune")
                errors = lint_file(filepath)
                if errors:
                    all_passed = False
                    print(f"[FAIL] {rel_path}")
                    for err in errors:
                        print(f"  - {err}")
                else:
                    print(f"[PASS] {rel_path}")
                    
    print("=" * 60)
    if all_passed:
        print("[SUCCESS] All style and docstring checks passed successfully!")
        sys.exit(0)
    else:
        print("[FAIL] Some style or docstring checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
