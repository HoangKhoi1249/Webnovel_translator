import argparse
import os
from pathlib import Path

"""
Split Book Utility

This script provides functionality to split large text files into smaller parts.
It supports two modes: single file splitting and batch processing of multiple files.

OPTIONS:
    input                    Input text file to split (required in single file mode)
    -o, --outdir DIR         Output directory (default: <input>_split for single file)
    -n, --lines N            Lines per split file (default: 100)
    --batch                  Process all .txt files in directory recursively
    --og-dir DIR            Origin directory to scan in batch mode (default: ./novels_txt)
    --save-dir DIR           Base save directory in batch mode (default: ./novels_txt_split)

Single File Mode:
    Split one text file into multiple parts based on line count.

    Usage:
        python split_book.py <input_file> [options]

    Examples:
        # Split a file into parts of 100 lines each (default)
        python split_book.py novel.txt

        # Split with 50 lines per file
        python split_book.py novel.txt -n 50

        # Split with custom output directory
        python split_book.py novel.txt -o ./split_parts

        # Split with both custom lines and output directory
        python split_book.py novel.txt -n 50 -o ./split_parts

Batch Mode:
    Process all .txt files in a directory recursively, preserving folder structure.

    Usage:
        python split_book.py --batch [options]

    Examples:
        # Process all .txt files in default novels_txt directory
        python split_book.py --batch

        # Process with custom source directory
        python split_book.py --batch --og-dir ./books

        # Process with custom destination directory
        python split_book.py --batch --save-dir ./processed

        # Process with both custom directories
        python split_book.py --batch --og-dir ./books --save-dir ./processed

Note: You cannot specify an input file when using --batch mode, and vice versa.
"""

OG_DIR = "./novels_txt"
SAVE_DIR = "./novels_txt_split"

os.makedirs(OG_DIR, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)

def split_file(path, output_dir=None, lines_per_file=100, h_match=None):
	"""
	Split a text file into multiple smaller files.

	Args:
		path (str or Path): Path to the input text file
		output_dir (str or Path, optional): Directory to save split files.
			If None, creates a directory named after the input file with '_split' suffix.
		lines_per_file (int): Number of lines per split file. Default is 100.
		h_match (str, optional): The heading pattern to match. If None, no heading matching is performed.
	Returns:
		int: Number of parts created

	Example:
		>>> split_file("novel.txt", lines_per_file=50)
		12  # Created 12 parts
	"""
	path = Path(path)
	if output_dir is None:
		output_dir = path.with_suffix("").as_posix() + "_split"
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	base = path.stem
	part_index = 1
	line_counter = 0
	out_file = None

	with path.open("r", encoding="utf-8") as fin:
		if h_match is not None:
			for line in fin:
				if line.lstrip().startswith(h_match):
					if out_file:
						out_file.close()
						part_index += 1
					part_name = f"{base}_part{part_index:03d}.txt"
					out_path = output_dir / part_name
					out_file = out_path.open("w", encoding="utf-8")
					
				if out_file is None:
					part_name = f"{base}_part{part_index:03d}.txt"
					out_path = output_dir / part_name
					out_file = out_path.open("w", encoding="utf-8")
				out_file.write(line) # type: ignore

					
		else:
			for line in fin:
					if line_counter % lines_per_file == 0:
						if out_file:
							out_file.close()
						part_name = f"{base}_part{part_index:03d}.txt"
						out_path = output_dir / part_name
						out_file = out_path.open("w", encoding="utf-8")
						part_index += 1
					out_file.write(line) # type: ignore
					line_counter += 1

	if out_file:
		out_file.close()

	return part_index - 1


def main():
	"""
	Main function to handle command-line arguments and execute file splitting.

	Parses command-line arguments and either processes a single file or batch processes
	all .txt files in the specified directory.

	Returns:
		int: Exit code (0 for success, 1 for error)
	"""
	parser = argparse.ArgumentParser(description="Split a text file into multiple files every N lines.")
	parser.add_argument("input", nargs="?", help="Input text file to split (omit when using --batch)")
	parser.add_argument("-o", "--outdir", help="Output directory (default: <input>_split)")
	parser.add_argument("-n", "--lines", type=int, default=100, help="Lines per split file (default: 100)")
	parser.add_argument("--batch", action="store_true", help="Process all .txt files under OG_DIR and write into SAVE_DIR preserving structure")
	parser.add_argument("--og-dir", default=OG_DIR, help="Origin directory to scan when using --batch (default: OG_DIR)")
	parser.add_argument("--save-dir", default=SAVE_DIR, help="Base save directory when using --batch (default: SAVE_DIR)")
	parser.add_argument("--heading", default=None, help="Match lines that start with a heading pattern (e.g., 'Chapter') instead of splitting by line count")

	args = parser.parse_args()
	input_path = args.input
	outdir = args.outdir
	n = args.lines
	h_match = args.heading
	if args.batch:
		og = Path(args.og_dir)
		save = Path(args.save_dir)
		if not og.exists():
			print(f"Origin directory not found: {og}")
			return 1

		total = 0
		failed = 0
		for file in og.rglob("*.txt"):
			try:
				rel_parent = file.parent.relative_to(og)
			except Exception:
				rel_parent = Path("")
			out_dir = save / rel_parent / file.stem
			try:
				parts = split_file(file, out_dir, n, h_match)
				print(f"{file} -> {out_dir} ({parts} parts)")
				total += 1
			except Exception as e:
				print(f"Failed to process {file}: {e}")
				failed += 1

		print(f"Processed {total} file(s), {failed} failed.")
		return 0

	if not input_path:
		parser.print_help()
		return 1

	if not Path(input_path).is_file():
		print(f"Input file not found: {input_path}")
		return 1

	parts = split_file(input_path, outdir, n, h_match)
	print(f"Created {parts} part(s) in: {outdir or (Path(input_path).with_suffix('').as_posix() + '_split')}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())