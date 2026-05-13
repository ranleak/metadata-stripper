import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Optional

# Attempt to import rich for the interactive UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
except ImportError:
    print("This script requires the 'rich' library. Please install it with: pip install rich")
    sys.exit(1)

# External dependencies check
# This script relies on 'exiftool' being installed on the system for deep cleaning.
# It also uses 'pikepdf' for document-specific cleaning.
try:
    import pikepdf
except ImportError:
    rprint("[yellow]Warning: 'pikepdf' not found. PDF metadata stripping will be limited.[/yellow]")

console = Console()

class MetadataStripper:
    def __init__(self):
        self.supported_images = {'.jpg', '.jpeg', '.png', '.tiff', '.webp', '.heic'}
        self.supported_videos = {'.mp4', '.mov', '.mkv', '.avi'}
        self.supported_docs = {'.pdf'}
        self.stats = {"success": 0, "failed": 0, "skipped": 0}

    def check_dependencies(self) -> bool:
        """Checks if ExifTool is installed on the system."""
        return shutil.which("exiftool") is not None

    def strip_metadata(self, file_path: Path) -> bool:
        """
        Main logic for stripping metadata based on file extension.
        Uses ExifTool for most files as it is the industry standard for 'nuclear' stripping.
        """
        ext = file_path.suffix.lower()
        
        try:
            # 1. Image and Video Handling via ExifTool (The most thorough method)
            if ext in self.supported_images or ext in self.supported_videos:
                # -all= removes all metadata groups
                # -overwrite_original prevents creating ._original backup files
                import subprocess
                result = subprocess.run(
                    ["exiftool", "-all=", "-overwrite_original", str(file_path)],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0

            # 2. PDF Handling (Special case for document structure)
            elif ext in self.supported_docs:
                try:
                    with pikepdf.open(file_path, allow_overwriting_input=True) as pdf:
                        # Delete the document information dictionary
                        del pdf.Root.Info
                        # Remove XMP metadata if it exists
                        if "/Metadata" in pdf.Root:
                            del pdf.Root.Metadata
                        pdf.save(file_path)
                    return True
                except Exception as e:
                    logging.error(f"PDF Error: {e}")
                    return False
            
            return False
        except Exception as e:
            logging.error(f"Error processing {file_path.name}: {e}")
            return False

    def run(self):
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]Privacy Guard: Metadata Stripper[/bold cyan]\n"
            "[small]Nuclear-grade metadata removal for Images, Videos, and PDFs[/small]",
            border_style="blue"
        ))

        # Check for ExifTool
        if not self.check_dependencies():
            rprint("[red]Error: 'exiftool' is not installed or not in your PATH.[/red]")
            rprint("ExifTool is required for deep cleaning. Install it from: [link=https://exiftool.org/]https://exiftool.org/[/link]")
            return

        # Input gathering
        target_path = Prompt.ask("Enter the path to a [bold green]file[/bold green] or [bold green]directory[/bold green]")
        path = Path(target_path)

        if not path.exists():
            rprint("[red]Path does not exist![/red]")
            return

        # Find targets
        files_to_process = []
        if path.is_file():
            files_to_process.append(path)
        else:
            for p in path.rglob("*"):
                if p.suffix.lower() in (self.supported_images | self.supported_videos | self.supported_docs):
                    files_to_process.append(p)

        if not files_to_process:
            rprint("[yellow]No supported files found.[/yellow]")
            return

        # Confirmation
        rprint(f"\n[bold]Found {len(files_to_process)} target files.[/bold]")
        if not Confirm.ask("Proceed with stripping metadata? [red]This is irreversible.[/red]"):
            rprint("[yellow]Operation cancelled.[/yellow]")
            return

        # Processing with Progress UI
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Stripping metadata...", total=len(files_to_process))
            
            for file in files_to_process:
                progress.update(task, description=f"[cyan]Processing: [white]{file.name}")
                success = self.strip_metadata(file)
                if success:
                    self.stats["success"] += 1
                else:
                    self.stats["failed"] += 1
                progress.advance(task)

        # Final Report
        table = Table(title="Processing Summary", box=None)
        table.add_column("Status", style="bold")
        table.add_column("Count", justify="right")
        
        table.add_row("[green]Successfully Cleaned", str(self.stats["success"]))
        table.add_row("[red]Failed", str(self.stats["failed"]))
        
        console.print("\n")
        console.print(table)
        console.print(Panel(f"[bold green]Done![/bold green] Your files at '{path}' are now sanitized.", border_style="green"))

if __name__ == "__main__":
    stripper = MetadataStripper()
    stripper.run()