import argparse
import os
import chapter_process as cp
import utilities as util


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
        "-n","--n_json_content",
        help="name the variable to extract from json (e.g., chapter_+name, author name, etc.)"
    )
    parser.add_argument (
        "--ext_output",
        required=False,
        help="extension for output files (default: .txt)"
    )
    parser.add_argument (
        "-t", "--title",
        required=False,
        default="title",
        nargs="?",
        help="place the title in the json of the chapter at the beginning of the output file (optional)\n Example: --title 'chapter_title'"

    )
    args = parser.parse_args()

    if args.mode == "single":
        if args.output and args.input and args.n_json_content:
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(
                    util.get_json_content(
                        args.input,
                        args.n_json_content
                    )
                )
        else:
            print("Output file, input file, and name of json content are required for single mode.")
    elif args.mode == "batch":

        if args.output and args.input:

            os.makedirs(args.input, exist_ok=True)
            os.makedirs(args.output, exist_ok=True)
            
            name_v, files = cp.collect_files(args.input, extension=".json")
            if util.is_2d_list(files):
                for index_v, volume in enumerate(files):
                    for chapter in volume:
                        content = util.get_json_content(chapter, args.n_json_content)
                        save_volume = os.path.join(args.output, name_v[index_v])
                        os.makedirs(save_volume, exist_ok=True)
                        

                        if args.ext_output:
                            save_path = os.path.join(save_volume, os.path.basename(chapter).replace('.json', args.ext_output))
                        else:
                            save_path = os.path.join(save_volume, os.path.basename(chapter).replace('.json', '.txt'))
                        with open(save_path, 'w', encoding='utf-8') as f:                        
                            if args.title:
                                title_content = util.get_json_content(chapter, args.title)
                                content = f"{title_content}\n\n" + content
                            f.write(content)
                        print(f"Saved: {save_path}")
            else:                
                for chapter in files:
                    content = util.get_json_content(chapter, args.n_json_content)
                    if args.ext_output:
                        save_path = os.path.join(args.output, os.path.basename(chapter).replace('.json', args.ext_output))
                    else:
                        save_path = os.path.join(args.output, os.path.basename(chapter).replace('.json', '.txt'))
                        
                    with open(save_path, 'w', encoding='utf-8') as f:                        
                        if args.title:
                            title_content = util.get_json_content(chapter, args.title)
                            content = f"{title_content}\n\n" + content
                        f.write(content)
                    print(f"Saved: {save_path}")
            
        else:
            print("Output folder and input folder are required for batch mode.")

if __name__ == "__main__":
    main()