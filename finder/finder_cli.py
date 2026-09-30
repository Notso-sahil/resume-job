import sys
import time
import argparse
import os
from pathlib import Path

# Ensure UTF-8 output encoding across Windows consoles — without this, Rich's
# unicode glyphs crash with UnicodeEncodeError on Windows' legacy console codepage.
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
from rich.table import Table

from finder.state_tracker import StateTracker
from finder.browser_client import BrowserClient
from finder.job_scraper import JobScraper
from finder.stipend_parser import extract_stipend, is_above_threshold
from finder.resume_integrator import ResumeIntegrator
from finder.form_filler import FormFiller

console = Console()

class FinderCLI:
    def __init__(self):
        self.tracker = StateTracker()
        self.browser = BrowserClient()
        self.scraper = JobScraper(self.browser)
        
        self.resume_builder_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.integrator = ResumeIntegrator(self.resume_builder_dir, self.tracker)
        self.filler = FormFiller(self.browser, self.tracker)

    def run_cycle(self):
        console.print("[bold cyan]Starting Job-Finder Cycle...[/bold cyan]")
        
        if not self.browser.health_check():
            console.print("[bold red]BrowseAI MCP Server is not reachable![/bold red]")
            return

        daily_count = self.tracker.get_daily_count()
        max_daily = 30
        if daily_count >= max_daily:
            console.print(f"[bold yellow]Daily limit reached ({daily_count}/{max_daily}). Stopping.[/bold yellow]")
            return

        tabs = self.browser.get_open_tabs()
        console.print(f"Found {len(tabs)} open tabs.")
        
        for tab in tabs:
            if daily_count >= max_daily:
                break
                
            tab_id = tab.get("tabId")
            url = tab.get("url", "")
            
            platform = self.scraper.detect_platform(url)
            if not platform:
                continue
                
            if not self.scraper.is_detail_page(tab_id, url, platform):
                continue
                
            console.print(f"\n[cyan]Processing Tab {tab_id}: {url}[/cyan]")
            
            details = self.scraper.scrape_detail_page(tab_id, platform)
            if not details:
                console.print("  [yellow]Failed to extract details.[/yellow]")
                continue
                
            company = details.get("company_name")
            role_title = details.get("role_title")
            
            if not company or not role_title:
                console.print("  [yellow]Missing required job details.[/yellow]")
                continue
                
            job_id = self.tracker.generate_job_id(company, role_title, url)
            if self.tracker.is_duplicate(job_id):
                console.print(f"  [yellow]Duplicate job: {company} - {role_title}[/yellow]")
                continue
                
            stipend_raw = details.get("stipend_raw", "")
            stipend_min = extract_stipend(stipend_raw)
            if not is_above_threshold(stipend_min, 20000):
                console.print(f"  [red]Stipend {stipend_min} below threshold (20000). Skipping.[/red]")
                continue
                
            tier, tier_score = self.scraper.classify_tier(role_title)
            
            job_data = {
                "job_id": job_id,
                "company": company,
                "role_title": role_title,
                "url": url,
                "platform": platform,
                "tier": tier,
                "tier_score": tier_score,
                "stipend_min": stipend_min,
                "stipend_raw": stipend_raw,
                "jd_text": details.get("jd_text", "")
            }
            
            self.tracker.add_job(job_data)
            console.print(f"  [green]Added {company} - {role_title} to tracker.[/green]")
            
            console.print("  [cyan]Generating tailored resume...[/cyan]")
            try:
                pdf_path = self.integrator.generate_resume(job_id)
                console.print(f"  [green]Resume tailored: {pdf_path}[/green]")
            except Exception as e:
                console.print(f"  [red]Resume integration failed: {e}[/red]")
                continue
                
            console.print("  [cyan]Filling application form...[/cyan]")
            success = self.filler.fill_application(job_id, tab_id)
            if success:
                console.print("  [bold green]Form filled! Awaiting human review.[/bold green]")
                daily_count += 1
            else:
                console.print("  [red]Form filling failed.[/red]")

def main():
    parser = argparse.ArgumentParser(description="Job-Finder Agent")
    parser.add_argument("--run", action="store_true", help="Run a single parsing cycle")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in the background")
    parser.add_argument("--status", action="store_true", help="Print current db stats")
    
    args = parser.parse_args()
    
    cli = FinderCLI()
    
    if args.status:
        jobs = cli.tracker.get_all()
        table = Table(title="Recent Applications")
        table.add_column("Company", style="cyan")
        table.add_column("Role", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Tier", justify="right")
        
        for job in jobs[:10]:
            table.add_row(job["company"], job["role_title"], job["status"], str(job["tier"]))
            
        console.print(table)
        
    elif args.daemon:
        console.print("[bold green]Starting daemon mode (polling every 60s)...[/bold green]")
        while True:
            try:
                cli.run_cycle()
                time.sleep(60)
            except KeyboardInterrupt:
                console.print("[bold red]Daemon stopped by user.[/bold red]")
                break
            except Exception as e:
                console.print(f"[bold red]Error in cycle: {e}[/bold red]")
                time.sleep(60)
                
    elif args.run:
        cli.run_cycle()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
