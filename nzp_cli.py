import sys
import os
import argparse
import requests
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from prompt_toolkit import prompt

def ollama_call(model: str, prompt: str) -> str:
    """
    Make an API call to Ollama and return the response.
    """
    try:
        response = requests.post('http://localhost:11434/api/generate', 
                               json={
                                   'model': model,
                                   'prompt': prompt,
                                   'stream': False
                               })
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: Unable to connect to Ollama (Status: {response.status_code})"
    except Exception as e:
        return f"Error: {str(e)}"

def ollama_ask_question(model: str, context: str, section: str) -> str:
    """
    Use Model A to ask the next NZP question for the given section.
    """
    section_questions = {
        "Objective": "What specific outcomes and deliverables will this project achieve?",
        "Purpose": "Why is this project important and what problem does it solve?",
        "Plan-of-Action": "What are the detailed steps to complete this project?",
        "Progress-so-far": "What work has already been completed on this project?",
        "Glossary": "What key terms and concepts are important for understanding this project?"
    }
    
    # Use predefined questions to ensure relevance
    question = section_questions.get(section, f"Describe the {section} for this project.")
    return question

def ollama_generate_answer(model: str, question: str, project: str, section: str) -> str:
    """
    Use Model B to generate an answer to the question.
    """
    section_requirements = {
        "Objective": "Answer in 150+ words as a single paragraph describing what this project aims to achieve.",
        "Purpose": "Answer in 100+ words explaining why this project is important and its intended impact.",
        "Plan-of-Action": "Provide detailed actionable steps explaining how this project will be completed.",
        "Progress-so-far": "Describe current status and progress on this project (minimum 10 words).",
        "Glossary": "List and define key terms and concepts relevant to this project."
    }
    
    requirement = section_requirements.get(section, "Provide a comprehensive answer.")
    
    answer_prompt = f"""You are working on a project about: {project}

Question: {question}

Requirements: {requirement}

Write a direct answer without repeating the project title. Start with "This project will..." or "The main objectives are..." and focus on the actual outcomes and deliverables:"""
    
    return ollama_call(model, answer_prompt)

console = Console()

SECTIONS = [
    ("Objective", 150),
    ("Purpose", 100),
    ("Plan-of-Action", 0),
    ("Progress-so-far", 10),
    ("Glossary", 0),
]


def edit_answer_cli(initial: str) -> str:
    console.print(Panel("Edit your answer below. Press [bold]Ctrl+D[/bold] when finished editing to save and continue.", title="Editor", style="yellow"))
    
    from prompt_toolkit.application import Application
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.layout.containers import HSplit
    from prompt_toolkit.layout.layout import Layout
    from prompt_toolkit.widgets import TextArea
    from prompt_toolkit.key_binding import KeyBindings
    
    # Create text area with initial content
    text_area = TextArea(
        text=initial,
        multiline=True,
        wrap_lines=True,
    )
    
    # Create key bindings
    bindings = KeyBindings()
    
    @bindings.add('c-d')
    def _(event):
        "Save and exit when Ctrl+D is pressed."
        event.app.exit(result=text_area.text)
    
    @bindings.add('c-c')
    def _(event):
        "Cancel editing when Ctrl+C is pressed."
        event.app.exit(result=initial)
    
    # Create layout
    root_container = HSplit([
        text_area,
    ])
    
    layout = Layout(root_container)
    
    # Create application
    app = Application(
        layout=layout,
        key_bindings=bindings,
        full_screen=False,
    )
    
    try:
        result = app.run()
        console.print("[green]✓ Saved![/green]")
        return result if result is not None else initial
    except KeyboardInterrupt:
        console.print("\n[red]Edit cancelled. Using original answer.[/red]")
        return initial

def validate(section: str, answer: str, min_words: int) -> bool:
    words = len(answer.split())
    if min_words > 0 and words < min_words:
        console.print(f"[red]Answer for {section} must be at least {min_words} words. Currently: {words} words.[/red]")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="NZP CLI Automation Tool")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--type", default="General", help="Project type/profile")
    parser.add_argument("--interviewer-model", default="llama3.1:8b-instruct-q4_K_M", help="Model for asking questions")
    parser.add_argument("--responder-model", default="llama3.2:3b-instruct-q4_K_M", help="Model for generating answers")
    args = parser.parse_args()

    project_name = args.project
    profile = args.type
    interviewer_model = args.interviewer_model
    responder_model = args.responder_model
    answers = {}
    context = ""

    for section, min_words in SECTIONS:
        while True:
            question = ollama_ask_question(interviewer_model, context, section)
            console.print(Panel(question, title=f"[bold cyan]Model A: {interviewer_model} ({section})[/bold cyan]"))
            answer = ollama_generate_answer(responder_model, question, project_name, section)
            console.print(Panel(answer, title=f"[bold green]Model B: {responder_model} ({section})[/bold green]"))
            action = Prompt.ask("[a]ccept / [e]dit / [r]etry / [q]uit", choices=["a", "e", "r", "q"], default="a")
            if action == "a":
                if validate(section, answer, min_words):
                    answers[section] = answer
                    context += f"\n{section}: {answer}\n"
                    break
            elif action == "e":
                edited = edit_answer_cli(answer)
                if validate(section, edited, min_words):
                    answers[section] = edited
                    context += f"\n{section}: {edited}\n"
                    break
            elif action == "r":
                continue  # regenerate answer
            elif action == "q":
                console.print("[yellow]Quitting...[/yellow]")
                sys.exit(0)

    # Compile output
    output = f"# {project_name}\n\n"
    for section, _ in SECTIONS:
        output += f"## {section}\n{answers.get(section, '')}\n\n"
    out_file = f"{project_name.replace(' ', '_').lower()}.md"
    with open(out_file, "w") as f:
        f.write(output)
    console.print(Panel(f"Project skeleton saved to [bold]{out_file}[/bold]", title="Done", style="green"))

if __name__ == "__main__":
    main()
