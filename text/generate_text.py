import os
import argparse
import ollama

def parse_args():
    parser = argparse.ArgumentParser(description='Generate text for a a healthy diet newsletter.')
    parser.add_argument('--base_model', required=True, type=str, help='Base model for text generation')
    parser.add_argument('--system_prompt', required=True, type=str, help='System prompt for customising model output')
    parser.add_argument('--temperature', required=True, type=float, help='Model temperature')
    parser.add_argument('--data_file', required=True, type=str, help='Path to the data file')
    parser.add_argument('--output_dir', type=str, help="Output directory where responses will be stored")
    parser.add_argument('--print_only', action='store_true', help="Print response to console")
    args = parser.parse_args()
    return args

def get_response(**kwargs):
    args = parse_args()

    with open(args.system_prompt, "r") as file:
        system_prompt = file.read()

    ollama.create(model="health-writer", from_=args.base_model, system=system_prompt)

    with open(args.data_file, "r") as file:
        data = file.read()

    res = ollama.generate(model="health-writer", prompt=data, options={"temperature": args.temperature})

    if args.print_only or args.output_dir is None:
        print(res['response'])
    else:
        os.makedirs(args.output_dir, exist_ok=True)

        data_base, _ = os.path.splitext(os.path.basename(args.data_file))
        output_filename = f"{data_base}_response.md"
        output_path = os.path.join(args.output_dir, output_filename)

        with open(output_path, "w") as f:
            f.write(res['response'])

    ollama.delete("health-writer")
    print("done")

def main():
    get_response()

if __name__ == "__main__":
    main()