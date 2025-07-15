import sys
import os
import re
import subprocess
from typing import List, Dict, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gemini_api import GeminiAPI

def extract_code_blocks(text: str) -> List[Dict[str, Any]]:
    code_blocks = []
    pattern = r'```(?P<lang>\w+)?(?: filename=(?P<filename>[^\n]+))?\n(?P<code>[\s\S]*?)```'
    for match in re.finditer(pattern, text):
        lang = match.group('lang') or 'text'
        code = match.group('code').strip()
        filename = match.group('filename') or None
        code_blocks.append({'language': lang, 'code': code, 'filename': filename})
    return code_blocks

def extract_plan(text: str) -> List[str]:
    plan = []
    plan_section = re.search(r'(plan|steps|how it works)[:\n\r]+([\s\S]+?)(\n\n|---|$)', text, re.IGNORECASE)
    if plan_section:
        lines = plan_section.group(2).splitlines()
        for line in lines:
            line = line.strip('-* 0123456789.\t')
            if line:
                plan.append(line)
    return plan

def run_orchestration(user_prompt: str) -> Dict[str, Any]:
    logs = []
    gemini = GeminiAPI()
    logs.append("Calling Gemini LLM...")
    llm_output = gemini.call(user_prompt, modality='text')
    logs.append("LLM response received.")
    plan = extract_plan(llm_output)
    code_blocks = extract_code_blocks(llm_output)
    files_created = []
    test_results = {}
    # If no code blocks, chain a follow-up prompt
    if not code_blocks:
        logs.append("No code blocks found. Sending follow-up prompt to generate code files.")
        followup_prompt = (
            "Based on the plan you just gave, now generate the full code for the project. "
            "For each file, use a separate markdown code block with the filename, like this: "
            "```python filename=app.py\n# code here\n```\n. Only output code blocks, no extra explanation."
        )
        llm_output2 = gemini.call(followup_prompt, modality='text')
        logs.append("Follow-up LLM response received.")
        code_blocks = extract_code_blocks(llm_output2)
        llm_output = llm_output + "\n\n---\n\n" + llm_output2
    # Create files
    output_dir = os.path.join(os.path.dirname(__file__), '../agent_output')
    os.makedirs(output_dir, exist_ok=True)
    for block in code_blocks:
        filename = block['filename'] or f"untitled_{block['language']}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(block['code'])
        files_created.append({'filename': filename, 'language': block['language'], 'code': block['code']})
        logs.append(f"Created file: {filename}")
    # Run tests if any test file is present
    test_file = next((f for f in files_created if 'test' in f['filename']), None)
    if test_file:
        logs.append(f"Running tests in {test_file['filename']}...")
        try:
            proc = subprocess.run([
                sys.executable, os.path.join(output_dir, test_file['filename'])
            ], capture_output=True, text=True, timeout=20)
            test_results = {
                'status': 'success' if proc.returncode == 0 else 'error',
                'stdout': proc.stdout,
                'stderr': proc.stderr,
                'returncode': proc.returncode,
                'test_file': test_file['filename']
            }
            logs.append(f"Test run complete. Return code: {proc.returncode}")
        except Exception as e:
            test_results = {'status': 'error', 'stderr': str(e), 'test_file': test_file['filename']}
            logs.append(f"Test run failed: {e}")
    else:
        logs.append("No unittest found in generated files.")
    logs.append("Orchestration complete.")
    return {
        'plan': plan,
        'files_created': files_created,
        'test_results': test_results,
        'logs': logs,
        'llm_output': llm_output
    } 