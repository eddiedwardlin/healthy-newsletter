import os
import argparse
import ollama
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def parse_args():
    parser = argparse.ArgumentParser(description='Generate text for a a healthy diet newsletter.')
    parser.add_argument('--base_model', required=True, type=str, help='Base model for text generation')
    parser.add_argument('--system_prompt', required=True, type=str, help='System prompt for customising model output')
    parser.add_argument('--temperature', required=True, type=float, help='Model temperature')
    parser.add_argument('--data_file', required=True, type=str, help='Path to the data file')
    parser.add_argument('--output_dir', type=str, help="Output directory where responses will be stored")
    parser.add_argument('--doc_dir', type=str, help="Directory that contains RAG documents")
    parser.add_argument('--embedding_model', required=True, type=str, help='Embedding model for embedding generation')
    parser.add_argument('--print_only', action='store_true', help="Print response to console")
    args = parser.parse_args()
    return args

def load_docs(dir):
    loader = DirectoryLoader(path=dir, glob="*.txt", loader_cls=TextLoader)
    docs = loader.load()
    return docs

def split_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
    chunks = text_splitter.split_documents(docs)
    return chunks

def create_vector_db(chunks, embedding_model):
    ollama.pull(embedding_model)
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model=embedding_model)
    )
    return vector_db

def create_retriever(vector_db, llm):
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. You will be given a type of food and some data. Your task is to generate five different subsets of the given a data to retrieve relevant recipes fitting the food type and data from a vector database. By generating multiple datasets on the given data, your goal is to help the user overcome some of the limitations of the distance-based similarity search. Provide these alternative datasets separated by newlines.
        Original food type and data: {question}""",
    )

    retriever = MultiQueryRetriever.from_llm(
        retriever=vector_db.as_retriever(),
        llm=llm,
        prompt=QUERY_PROMPT
    )

    return retriever

def create_chain(retriever, llm):
    template = """{context}
    data: {data}
    """
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "data": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

def main():
    args = parse_args()

    # Load recipes
    docs = load_docs(args.doc_dir)
    print("done loading...")

    # Break recipes into chunks
    chunks = split_docs(docs)
    print("done splitting...")
    
    # Load chunks into vector db
    vector_db = create_vector_db(chunks, args.embedding_model)
    print("done setting up vector database...")

    # Set up retriever for finding relevant chunks
    base_llm = ChatOllama(model=args.base_model)
    retriever = create_retriever(vector_db, base_llm)

    # Generate newsletter
    with open(args.system_prompt, "r") as file:
        system_prompt = file.read()

    ollama.create(model="health-writer", from_=args.base_model, system=system_prompt)
    llm = ChatOllama(model="health-writer", temperature=args.temperature)
    chain = create_chain(retriever, llm)

    with open(args.data_file, "r") as file:
        data = file.read()

    res = chain.invoke(data)
    
    if args.print_only or args.output_dir is None:
        print(res)
    else:
        os.makedirs(args.output_dir, exist_ok=True)

        data_base, _ = os.path.splitext(os.path.basename(args.data_file))
        output_filename = f"{data_base}_rag_response.md"
        output_path = os.path.join(args.output_dir, output_filename)

        with open(output_path, "w") as f:
            f.write(res)

    ollama.delete("health-writer")
    print("done")

if __name__ == "__main__":
    main()