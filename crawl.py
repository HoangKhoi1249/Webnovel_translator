import argparse
import os
import json
import sys
from bs4 import BeautifulSoup, Tag
import requests

def shuhaige_chapter_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.select_one("h1.headline")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Content
    content_div = soup.select_one("div.content")

    if not isinstance(content_div, Tag):
        return ""

    lines = [
        text
        for p in content_div.select("p")
        if (text := p.get_text(strip=True))  # tránh gọi 2 lần
        and "书海阁小说网" not in text        # lọc quảng cáo
    ]

    content = "\n".join(lines)

    return f"{title}\n\n{content}"

def main():
    parser = argparse.ArgumentParser(description="Crawl chapter content from various sources")

    parser.add_argument (
        "--input",
        nargs="?",
        help="Input file containing chapter URLs (one per line)"
        )
    
    parser.add_argument (
        "--input-dir",
        nargs="?",
        help="Input directory containing .txt files with chapter URLs (one per line)"
        )
    
    parser.add_argument (
        "--batch", 
        action="store_true",
        help="Batch mode: crawl each .txt file in the input directory separately"
        )
    
    parser.add_argument (
        "-o", "--output",
        help="Output file path", 
        default="output.txt"
        )
    
    parser.add_argument (
        "--output-dir",
        nargs="?",
        help="Output directory for batch mode (each .txt file will be saved as a separate .txt file with the same name)",
        default="output_crawled"
        )
    parser.add_argument (
        "--source",
        choices=["shuhaige"],
        default="shuhaige",
        help="Source's website"
    )

    args = parser.parse_args()

    if args.batch:
        if not args.input_dir:
            args.print_help()
            return 1
        else:
            file_paths = [os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir) if f.endswith(".txt")]
    else:
        with open(args.input, "r", encoding="utf-8") as fin:
            data = fin.read()
        if args.source == "shuhaige":
            data = shuhaige_chapter_content(data)
        elif args.source is None:
            sys.exit("You must specify the source website using --source")
        else:
            sys.exit(f"Unsupported source: {args.source}")

        with open(args.output, "w", encoding="utf-8") as fout:
            fout.write(data)

if __name__ == "__main__":
    main()
    