# healthy-newsletter

RAG system to that generates a healthy meal newsletter based on a user's health data.

### Instructions
1. Create and activate virtual environment
    - Run `python3 -m venv env` 
    - Run `source env/bin/activate`
2. Install dependencies
    - Run `pip install -r requirements.txt`
3. Navigate into /text to find necessary scripts
    - Run `./generate_text.py ./data/data_file.txt` to generate newsletters without RAG
    - Run `./generate_text_rag.py ./data/data_file.txt` to generate newsletters with RAG