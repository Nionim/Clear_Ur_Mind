from __future__ import annotations
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent / "."
OUTPUT_FILE = Path(__file__).resolve().parent / "tekila.txt"
IGNORE_DIRS = {"node_modules", ".git", "__pycache__", "dist", "build"}
IGNORE_FILES = {}
EXTENSIONS = {".svelte", ".scss", ".js", ".html", ".ts"}

ABOUT_PROJECT = """
My megacool project
"""

MY_COOL_POMPT = """
Rewrote this sh1111111111111
"""

ANSWER_STYLE = """
Nah
"""

USER_PROMPT = ABOUT_PROJECT + MY_COOL_POMPT + ANSWER_STYLE


def collect_files(source_dir: Path, extensions: set[str]) -> list[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(f"Cannot found: {source_dir}")

    result = []

    def walk(current_dir: Path) -> None:
        for item in current_dir.iterdir():
            if item.is_file() and item.name in IGNORE_FILES:
                continue
            if item.is_dir():
                if item.name in IGNORE_DIRS:
                    continue
                walk(item)
                continue
            if item.suffix in extensions:
                result.append(item)

    walk(source_dir)
    return sorted(result)


def write_combined_file(file_paths: list[Path], output_path: Path, prompt: str) -> None:
    with open(output_path, "w", encoding="utf-8") as out_f:
        for file_path in file_paths:
            rel_path = file_path.relative_to(SOURCE_DIR)
            out_f.write(f"{rel_path}:\n")
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            out_f.write(content)
            out_f.write("\n\n")
        if prompt:
            out_f.write(prompt + "\n")


def main() -> None:
    print(f"Searching files with {EXTENSIONS} extensions in {SOURCE_DIR}...")
    files = collect_files(SOURCE_DIR, EXTENSIONS)

    if not files:
        print("No files")
        return

    print(f"File count {len(files)}")
    write_combined_file(files, OUTPUT_FILE, USER_PROMPT)
    print(f"Final file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
