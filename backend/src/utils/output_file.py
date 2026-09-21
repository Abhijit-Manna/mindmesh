from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def save_output(filename: str, output) -> Path:
    file_path = OUTPUT_DIR / filename

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(output))

    print(f"Saved output to: {file_path}")

    return file_path