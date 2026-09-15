"""
AntiGravity Resume Engine — CLI Entrypoint

Usage:
    python main.py                          # Interactive job selection, PDF default
    python main.py --job naive              # Non-interactive generation for Naive
    python main.py --job naive --format docx # Generate docx for Naive
    python main.py --job pindrop --format latex # Generate LaTeX for Pindrop
    python main.py --jd path/to/jd.txt      # Custom JD text file
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.prompt import Prompt

from src.config import is_secondary_mode, OUTPUT_DIR
from src.agents.graph import create_resume_graph
from src.schemas.models import OutputFormat
from src.extractors.profile_extractor import (
    load_or_extract_profile,
    find_candidate_resumes,
    CACHE_PATH,
)
from src.loaders.job_loader import load_job_config, list_available_jobs, JOBS_DIR

console = Console(legacy_windows=False)


def parse_cli_args():
    parser = argparse.ArgumentParser(description="AntiGravity Resume Engine")
    parser.add_argument(
        "--format",
        choices=["pdf", "docx", "latex"],
        default=None,
        help="Resume output format (default: pdf)",
    )
    parser.add_argument(
        "--job",
        type=str,
        default=None,
        help="Company name or slug of pre-configured job in jobs/ (e.g. sample_job, pindrop)",
    )
    parser.add_argument(
        "--jd",
        type=str,
        default=None,
        help="Path to a text file containing the target Job Description",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Path to candidate resume PDF (to override auto-detection)",
    )
    return parser.parse_args()


def main():
    args = parse_cli_args()

    console.rule("[bold green]AntiGravity Autonomous Resume Engine[/bold green]")

    # --- Step 1: Candidate Profile Detection ---
    console.print("\n[bold]Step 1 of 3:[/bold] Candidate Profile")
    candidate_profile = None

    if CACHE_PATH.exists():
        candidate_profile = load_or_extract_profile(None)
        if candidate_profile:
            console.print(
                f"[green]✓ Loaded from cache:[/green] [bold]{candidate_profile.full_name}[/bold] "
                f"({candidate_profile.email})"
            )
            if candidate_profile.education:
                edu = candidate_profile.education[0]
                console.print(f"  [dim]{edu.degree} | {edu.institution}[/dim]")

    if not candidate_profile:
        if args.resume:
            resume_path = Path(args.resume)
            if resume_path.is_file():
                console.print(f"[cyan]Extracting profile from {resume_path}...[/cyan]")
                candidate_profile = load_or_extract_profile(resume_path)
            else:
                console.print(f"[red]Error: Specified resume PDF not found at {resume_path}[/red]")
                sys.exit(1)

        if not candidate_profile:
            found_pdfs = find_candidate_resumes()
            if len(found_pdfs) == 1:
                pdf_target = found_pdfs[0]
                console.print(f"[green]✓ Found candidate resume:[/green] {pdf_target.name}")
                with console.status("[bold green]Extracting candidate profile...[/bold green]"):
                    candidate_profile = load_or_extract_profile(pdf_target)
            elif len(found_pdfs) > 1:
                console.print("[yellow]Multiple resume PDFs found in workspace:[/yellow]")
                for idx, pdf in enumerate(found_pdfs, start=1):
                    console.print(f"  [{idx}] {pdf.name}")
                choice = Prompt.ask(
                    "Select resume to extract",
                    choices=[str(i) for i in range(1, len(found_pdfs) + 1)],
                    default="1",
                )
                selected_pdf = found_pdfs[int(choice) - 1]
                with console.status("[bold green]Extracting candidate profile...[/bold green]"):
                    candidate_profile = load_or_extract_profile(selected_pdf)
            else:
                project_root = Path(__file__).resolve().parent
                console.print("\n[bold red]✗ No candidate profile or resume PDF found.[/bold red]")
                console.print("  [yellow]To fix this:[/yellow]")
                console.print(f"  Copy your resume PDF into this directory:")
                console.print(f"    [bold cyan]{project_root}[/bold cyan]")
                console.print(f"  Then re-run: [bold green]python main.py[/bold green]\n")
                sys.exit(1)

        if candidate_profile:
            console.print(
                f"[green]✓ Profile extracted & cached:[/green] [bold]{candidate_profile.full_name}[/bold] "
                f"({candidate_profile.email})"
            )

    # --- Step 2: Target Job Configuration ---
    console.print("\n[bold]Step 2 of 3:[/bold] Target Job")
    job_config = None
    raw_jd = ""

    if args.job:
        try:
            job_config = load_job_config(args.job)
            jd_obj = job_config["jd_analysis"]
            console.print(
                f"[green]✓ Loaded Job Config:[/green] [bold]{jd_obj.company_name}[/bold] — {jd_obj.role_title}"
            )
        except Exception as e:
            console.print(f"[red]Error loading job config '{args.job}': {e}[/red]")
            sys.exit(1)

    elif args.jd:
        jd_file = Path(args.jd)
        if jd_file.exists():
            with open(jd_file, "r", encoding="utf-8") as f:
                raw_jd = f.read()
            console.print(f"[green]✓ Loaded JD from:[/green] {jd_file}")
        else:
            console.print(f"[red]Error: JD file not found at {jd_file}[/red]")
            sys.exit(1)

    else:
        available_jobs = list_available_jobs()
        if available_jobs:
            console.print("  Available pre-configured jobs:")
            menu_choices = []
            for idx, j in enumerate(available_jobs, start=1):
                key = str(idx)
                menu_choices.append(key)
                console.print(f"    [{key}] [bold]{j['company_name']}[/bold] ({j['role_title']})")
            manual_key = str(len(available_jobs) + 1)
            menu_choices.append(manual_key)
            console.print(f"    [{manual_key}] Enter custom Job Description manually")

            choice = Prompt.ask("\nSelect target job", choices=menu_choices, default="1")
            if choice == manual_key:
                raw_jd = ""
            else:
                selected_job = available_jobs[int(choice) - 1]
                job_config = load_job_config(selected_job["path"])
                jd_obj = job_config["jd_analysis"]
                console.print(
                    f"[green]✓ Selected:[/green] [bold]{jd_obj.company_name}[/bold] — {jd_obj.role_title}"
                )

        if not job_config and not raw_jd:
            console.print(
                "[yellow]Paste your Job Description below. Press Enter twice when done (or Enter on empty line to use sample JD):[/yellow]"
            )
            lines = []
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            raw_jd = "\n".join(lines).strip()

            if not raw_jd:
                sample_path = Path("sample_jd.txt")
                if sample_path.exists():
                    with open(sample_path, "r", encoding="utf-8") as f:
                        raw_jd = f.read()
                else:
                    raw_jd = (
                        "Role: Senior AI Engineer / Agentic Backend Architect\n"
                        "Requirements: 3+ years experience with Python, FastAPI, LangGraph, and LangChain.\n"
                        "Hands-on production experience designing agentic cyclic workflows, RAG pipelines, and vector databases (Qdrant, Pinecone).\n"
                        "Strong background in distributed systems, Kafka, Redis, PostgreSQL, Docker, and Kubernetes.\n"
                        "Proven track record optimizing p99 latency, high-throughput concurrency, and system reliability."
                    )
                console.print("[cyan]✓ Using default target Job Description (AI Platform / Agentic Systems)[/cyan]")

    # --- Step 3: Output Format ---
    console.print("\n[bold]Step 3 of 3:[/bold] Output Format")
    selected_fmt = "pdf"
    if args.format:
        selected_fmt = args.format.lower()
        console.print(f"[green]✓ Format specified via CLI:[/green] [bold]{selected_fmt.upper()}[/bold]")
    else:
        console.print("[green]✓ Format:[/green] [bold]PDF (default)[/bold]")

    output_format = OutputFormat(format=selected_fmt)

    # --- Run Pipeline ---
    console.print()
    console.rule("[bold cyan]Executing Agentic Synthesis Pipeline[/bold cyan]")
    with console.status("[bold green]Synthesizing single-format tailored portfolio...[/bold green]"):
        graph = create_resume_graph()
        initial_state = {
            "raw_jd": raw_jd or (job_config["jd_analysis"].model_dump_json() if job_config else ""),
            "output_format": output_format,
            "candidate_profile": candidate_profile,
            "job_config": job_config,
            "job_config_path": job_config.get("job_config_path") if job_config else None,
            "iteration_count": 0,
            "critique_history": [],
        }
        final_state = graph.invoke(initial_state)

    # --- Report Outputs ---
    console.rule("[bold green]Pipeline Execution Complete[/bold green]")
    eval_res = final_state.get("evaluation_result")
    if eval_res:
        console.print(
            f"[bold]Audit Results:[/bold] ATS Coverage: [cyan]{eval_res.ats_coverage_score}%[/cyan] | "
            f"Plausibility: [cyan]{eval_res.metric_plausibility_score}/10[/cyan] | "
            f"Stack Cohesion: [cyan]{eval_res.stack_cohesion_score}/10[/cyan] | "
            f"Gate Passed: [green]{eval_res.passed_all_gates}[/green]"
        )

    console.print("\n[bold]Generated Artifacts (Clean Single-Format Output):[/bold]")
    if CACHE_PATH.exists():
        console.print(f"  [green]✓ Candidate Profile:[/green] {CACHE_PATH}")
    if final_state.get("final_docx_path"):
        console.print(f"  [green]✓ Resume (.docx):[/green]    {final_state['final_docx_path']}")
    if final_state.get("final_pdf_path"):
        console.print(f"  [green]✓ Resume (.pdf):[/green]     {final_state['final_pdf_path']}")
    if final_state.get("final_latex_path"):
        console.print(f"  [green]✓ Resume (.tex):[/green]     {final_state['final_latex_path']}")
    if final_state.get("final_dossier"):
        console.print(f"  [green]✓ Interview Dossier:[/green] {final_state['final_dossier']}")
    if final_state.get("archived_pdf_path"):
        console.print(f"  [dim cyan]✓ Archived prior PDF:[/dim cyan]       {final_state['archived_pdf_path']}")
    if final_state.get("archived_dossier_path"):
        console.print(f"  [dim cyan]✓ Archived prior Dossier:[/dim cyan]   {final_state['archived_dossier_path']}")
    console.print(f"  [green]✓ Structured JSON:[/green]   {OUTPUT_DIR / 'portfolio_data.json'}")
    console.print("\n[bold green]Ready for technical interview defense and ATS submission![/bold green]\n")


if __name__ == "__main__":
    main()
