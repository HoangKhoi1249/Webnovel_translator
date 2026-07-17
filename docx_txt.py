import argparse
from pathlib import Path

from docx import Document  # type: ignore


def paragraph_to_markdown(paragraph) -> str:
    if paragraph.style.name.startswith("Heading"):
        try:
            level = int(paragraph.style.name.split()[-1])
        except Exception:
            level = 1

        prefix = "#" * level + " "
    else:
        prefix = ""

    parts = []

    for run in paragraph.runs:
        text = run.text

        if not text:
            continue

        if run.bold and run.italic:
            text = f"***{text}***"
        elif run.bold:
            text = f"**{text}**"
        elif run.italic:
            text = f"*{text}*"

        parts.append(text)

    return prefix + "".join(parts)


def convert_file(input_file: Path, output_file: Path):
    print(f"[START] {input_file}")

    document = Document(str(input_file))

    total = len(document.paragraphs)

    with output_file.open("w", encoding="utf-8", newline="\n") as fout:
        for index, paragraph in enumerate(document.paragraphs, 1):
            fout.write(paragraph_to_markdown(paragraph))
            fout.write("\n")

            if index % 500 == 0 or index == total:
                print(f"  {index}/{total} paragraphs\r", end="")

    print()
    print(f"[DONE] {output_file}\n")


def batch_convert(input_folder: Path, output_folder: Path):
    docx_files = sorted(input_folder.glob("*.docx"))

    if not docx_files:
        print("Không tìm thấy file docx")
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    total = len(docx_files)

    print(f"Batch start: {total} files\n")

    for index, docx_file in enumerate(docx_files, 1):
        print(f"=== File {index}/{total} ===")

        output_file = output_folder / (docx_file.stem + ".txt")
        convert_file(docx_file, output_file)

    print("Batch completed")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        choices=["single", "batch"],
        help="single = xử lý 1 file, batch = xử lý cả thư mục",
    )

    parser.add_argument(
        "input",
        help="file docx hoặc folder",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="file hoặc folder output",
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    if args.mode == "single":
        output_path = Path(args.output or input_path.with_suffix(".txt"))
        convert_file(input_path, output_path)

    else:
        output_folder = Path(args.output or "output_txt")
        batch_convert(input_path, output_folder)


if __name__ == "__main__":
    main()