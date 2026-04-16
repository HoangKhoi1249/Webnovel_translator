import argparse
import json
import os
from bs4 import BeautifulSoup
import chapter_process as cp

def get_json_content(path: str, name_json: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        content = html_to_text(data.get(name_json))
        if content is None:
            raise ValueError(f"Variable '{name_json}' not found in the JSON file.")
        return content

def html_to_text(HtmlContent: str) -> str:
    Soup = BeautifulSoup(HtmlContent, "html.parser")

    # Get text, each <p> tag on a new line
    Text = Soup.get_text(separator="\n")

    # Remove extra blank lines
    Lines = [Line.strip() for Line in Text.splitlines() if Line.strip()]

    return "\n".join(Lines)

def main():
    parser = argparse.ArgumentParser(description="Crawl chapter content from various sources")
    parser.add_argument (
        "--mode",
        choices=["single", "batch"],
        help="single = process 1 file, batch = process all files in a folder"
    )
    parser.add_argument (
        "--input",
        help="input file or folder if batch mode"
    )

    parser.add_argument (
        "-o", "--output",
        help="output file or folder if batch mode"
    )
    
    parser.add_argument (
        "-n","--name_json",
        help="name the variable to extract from json (e.g., chapter name, author name, etc.)"
    )

    args = parser.parse_args()

    if args.mode == "single":
        if args.output:
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(
                    get_json_content(
                        args.input,
                        args.name_json
                    )
                )
    elif args.mode == "batch":

        if args.output and args.input:
            os.makedirs(args.output, exist_ok=True)
            _, files = cp.collect_files(args.input, extension=".json")
            print("Output folder is not implemented yet.")
            
        else:
            print("Output folder and input folder are required for batch mode.")

if __name__ == "__main__":
    main()