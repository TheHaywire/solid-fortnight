from agents.planner import PlannerAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.debugger import DebuggerAgent
from agents.documenter import DocumenterAgent
from agents.modal_switcher import ModalSwitcherAgent
from agents.critic import CriticAgent
from agents.researcher import ResearchAgent
from agents.deployment import DeploymentAgent
from gemini_api import GeminiAPI
import json
import os

def web_search_func(query):
    # Placeholder: In production, connect to a real web search API
    # For now, just return the query as a string
    return f"[Web search results for: {query}]"

MEMORY_FILE = "persistent_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

class Context:
    def __init__(self, user_request):
        self.user_request = user_request
        self.research = None
        self.plan = []
        self.subtask_results = []
        self.final_docs = []
        self.status = "in_progress"
        self.current_subtask = None
        self.logs = []
        self.memory = load_memory()

class MetaAgent:
    def __init__(self, name, gemini=None):
        self.name = name
        self.gemini = gemini or GeminiAPI()
    def reflect(self, context, subtask, failures):
        prompt = (
            "You are a world-class meta-reasoning agent. "
            "Given the following subtask, repeated failures, and context, suggest a new approach, alternative plan, or escalation.\n"
            f"Subtask: {subtask}\nFailures: {failures}\nContext: {context.user_request}"
        )
        return self.gemini.call(prompt, modality='text')

# Recursive subtask execution
def execute_subtask(subtask, context, agents, depth=0):
    indent = '  ' * depth
    print(f"{indent}[Modal Switcher] For subtask: {subtask}")
    modality = agents['modal_switcher'].run(subtask)
    print(f"{indent}Modality: {modality}")

    # Research for subtask if needed
    if modality not in ["code", "text"]:
        print(f"{indent}[Researching for subtask: {subtask}]")
        subtask_research = agents['research_agent'].run(subtask)
        print(subtask_research)
        subtask_input = f"{subtask}\n\nRelevant research findings:\n{subtask_research}"
    else:
        subtask_input = subtask

    # Coding
    print(f"{indent}[Coder] Coding for: {subtask}")
    code = agents['coder'].run(subtask_input)
    print(f"{indent}Generated code:\n{code}")

    # Testing and Debugging Loop
    max_attempts = 3
    failures = []
    for attempt in range(max_attempts):
        print(f"{indent}[Tester] Running tests...")
        test_results = agents['tester'].run(code)
        print(f"{indent}Test results: {test_results}")
        if test_results.get('passed'):
            break
        print(f"{indent}[Debugger] Debugging...")
        code = agents['debugger'].run(code, test_results)
        failures.append(test_results.get('details', ''))
    else:
        print(f"{indent}[MetaAgent] Reflecting after repeated failures...")
        meta_reflection = agents['meta_agent'].reflect(context, subtask, failures)
        print(f"{indent}MetaAgent suggestion: {meta_reflection}")
        # Try to break down the subtask recursively if suggested
        if 'break down' in meta_reflection.lower() or 'subtask' in meta_reflection.lower():
            print(f"{indent}[Planner] Recursively breaking down subtask...")
            sub_subtasks = agents['planner'].run(f"{subtask}\n\nMetaAgent suggestion: {meta_reflection}")
            for sub_subtask in sub_subtasks:
                execute_subtask(sub_subtask, context, agents, depth=depth+1)
            return
        else:
            print(f"{indent}[ERROR] Unable to resolve test failures after multiple attempts.")
            context.status = "failed"
            context.logs.append({'subtask': subtask, 'failures': failures, 'meta_reflection': meta_reflection})
            return

    # Critic Review
    print(f"{indent}[Critic] Reviewing code...")
    review = agents['critic'].run(code, subtask)
    print(f"{indent}Critic review: {review}")
    if review.get('issues') and review.get('issues') != '':
        print(f"{indent}[Coder] Improving code based on critic feedback...")
        code = agents['coder'].run(f"{subtask}\n\nCritic feedback:\n{review}")

    # Documentation
    print(f"{indent}[Documenter] Generating documentation...")
    docs = agents['documenter'].run(code)
    print(f"{indent}{docs}")
    context.subtask_results.append({
        'subtask': subtask,
        'code': code,
        'test_results': test_results,
        'review': review,
        'docs': docs
    })
    context.final_docs.append(docs)
    # Save to persistent memory
    context.memory[subtask] = {
        'code': code,
        'test_results': test_results,
        'review': review,
        'docs': docs
    }
    save_memory(context.memory)

    # (Stub) Continuous monitoring/self-improvement hook
    # e.g., schedule re-testing, re-research, or optimization
    # print(f"{indent}[Monitor] Scheduling continuous improvement for: {subtask}")


def main():
    user_request = input("Enter your coding request: ")
    context = Context(user_request)

    gemini = GeminiAPI()
    research_agent = ResearchAgent("Researcher", web_search_func, gemini)
    planner = PlannerAgent("Planner", gemini)
    modal_switcher = ModalSwitcherAgent("ModalSwitcher", gemini)
    coder = CoderAgent("Coder", gemini)
    tester = TesterAgent("Tester", gemini)
    debugger = DebuggerAgent("Debugger", gemini)
    documenter = DocumenterAgent("Documenter", gemini)
    critic = CriticAgent("Critic", gemini)
    deployment = DeploymentAgent("Deployment")
    meta_agent = MetaAgent("Meta", gemini)

    agents = {
        'research_agent': research_agent,
        'planner': planner,
        'modal_switcher': modal_switcher,
        'coder': coder,
        'tester': tester,
        'debugger': debugger,
        'documenter': documenter,
        'critic': critic,
        'deployment': deployment,
        'meta_agent': meta_agent
    }

    # Step 1: Research
    print("\n[Researching]")
    context.research = research_agent.run(user_request)
    print(context.research)

    # Step 2: Planning
    print("\n[Planning]")
    plan_input = f"{user_request}\n\nRelevant research findings:\n{context.research}"
    context.plan = planner.run(plan_input)
    print("Plan:", context.plan)

    # User-in-the-loop checkpoint: Approve or edit plan
    print("\n[User Checkpoint] Review the plan above.")
    user_action = input("Type 'approve' to continue, 'edit' to modify the plan, or 'replan' to start over: ").strip().lower()
    if user_action == 'edit':
        new_plan = input("Enter your edited plan as a JSON array or comma-separated list: ")
        try:
            context.plan = json.loads(new_plan)
        except Exception:
            context.plan = [item.strip() for item in new_plan.split(',') if item.strip()]
    elif user_action == 'replan':
        print("Re-running planner...")
        context.plan = planner.run(plan_input)
        print("New Plan:", context.plan)

    # Step 3: Execute each subtask (with recursion/meta-reasoning)
    for subtask in context.plan:
        execute_subtask(subtask, context, agents)
        if context.status == "failed":
            print("[FATAL] Stopping due to unresolved failures.")
            break

    # User-in-the-loop checkpoint: Approve or edit before deployment (stub)
    print("\n[User Checkpoint] Review all results before deployment.")
    user_action = input("Type 'approve' to deploy, 'edit' to modify code/docs, or 'abort' to stop: ").strip().lower()
    if user_action == 'edit':
        print("Manual editing not implemented yet. Please edit files directly if needed.")
    elif user_action == 'abort':
        print("Aborting deployment.")
        return

    context.status = "complete"
    print("\n[All subtasks complete. Final documentation and results:]")
    for result in context.subtask_results:
        print(f"\nSubtask: {result['subtask']}")
        print("Code:\n", result['code'])
        print("Test Results:", result['test_results'])
        print("Critic Review:", result['review'])
        print("Documentation:\n", result['docs'])

if __name__ == "__main__":
    main()
