import argparse
import os
import json
import sys
from bs4 import BeautifulSoup, Tag
import utilities as utils
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

    parser.add_argument (
        "--structure",
        action="store_true",
        help="Create a structure of folders"
    )
    args = parser.parse_args()

    if args.batch and args.input_dir:
        if not args.input_dir:
            args.print_help()
            return 1
        
        else:    
            file_paths = [os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir) if f.endswith(".html")]
            #print(file_paths)
            print(f"Found {len(file_paths)} .html files in {args.input_dir}")
            file_path_id = "00000"

            amount = len(file_paths)//100 + 1
            if args.structure:
                for i in range(1, amount + 1):
                    folder_name = utils.add_with_padding("000", str(i))
                    os.makedirs(os.path.join(args.output_dir, folder_name), exist_ok=True)

            for i, file_path in enumerate(file_paths, start=1):
                

                file_path_id = utils.add_with_padding(file_path_id, "1")
                with open(file_path, "r", encoding="utf-8") as fin:
                    data = fin.read()
                if args.source == "shuhaige":
                    data = shuhaige_chapter_content(data)

                elif args.source == None:
                    sys.exit("You must specify the source website using --source")
                
                else:
                    sys.exit(f"Unsupported source: {args.source}")

                os.makedirs(args.output_dir, exist_ok=True)
                output_subdir = os.path.join(args.output_dir, utils.add_with_padding("000", str((i-1)//100 + 1))) if args.structure else args.output_dir
                
                output_file_path = utils.normalize_path(os.path.join(output_subdir, os.path.basename(file_path_id + ".txt")))
                
                with open(output_file_path, "w", encoding="utf-8") as fout:
                    fout.write(data)
                print(f"Crawled content from {file_path} and saved to {output_file_path}")

    elif args.batch and not args.input_dir:
        sys.exit("Batch mode requires --input-dir")

    elif args.input:
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
    