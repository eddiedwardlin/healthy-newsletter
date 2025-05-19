#!/bin/bash

export BASE_MODEL="llama3.2"
export SYSTEM_PROMPT="./settings/system.txt"
export TEMPERATURE=0.3
export OUTPUT_DIR="./rag_responses"
export DOC_DIR="./scraper/recipes"
export EMBEDDING_MODEL="nomic-embed-text"

print_only=false

help_message() {
    echo "Usage: ./generate_text_rag.sh [options] <data_path>"
    echo ""
    echo "Options:"
    echo "  -p       Print to console (do not save response to file)"
    echo " --help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./generate_text_rag.sh data.txt"
    echo "  ./generate_text_rag.sh -p data.txt"
}

for arg in "$@"; do
    if [[ "$arg" == "--help" ]]; then
        help_message
        exit 0
    fi
done

while getopts p flag
do
    case "$flag" in
        p) print_only=true ;;
    esac
done

shift $((OPTIND - 1))
data=$1

if [ -z "$data" ]; then
    echo "No data file provided"
    echo "Usage: ./generate_text_rag.sh [options] <data_path>"
    exit 1
fi

CMD="python3 generate_text_rag.py --base_model=$BASE_MODEL --system_prompt=$SYSTEM_PROMPT --temperature=$TEMPERATURE --doc_dir=$DOC_DIR --embedding_model=$EMBEDDING_MODEL --data_file=$data"

if [ "$print_only" = false ]; then
    CMD+=" --output_dir=$OUTPUT_DIR"
else
    CMD+=" --print_only"
fi

eval $CMD