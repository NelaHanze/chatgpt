import os
import sys
import constants
import markdown

from langchain_community.vectorstores  import starrocks
from langchain_community.vectorstores.starrocks import StarRocksSettings
from langchain_community.vectorstores  import chroma
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from langchain.chains import VectorDBQA
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.indexes import VectorstoreIndexCreator
from langchain_openai import ChatOpenAI, OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
#from langchain_core.prompts import ChatPromptTemplate

template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Use three sentences maximum and keep the answer as concise as possible. 
Always say "thanks for asking!" at the end of the answer. 
{context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

os.environ["OPENAI_API_KEY"] = "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"
openai = ChatOpenAI(model_name="gpt-3.5-turbo")
openai = ChatOpenAI(model_name="gpt-4")

query = sys.argv[1]

loader = TextLoader('data.txt')
#markdown_path = "C:/Users/hanze/Downloads/chatGPT chatbot-20231106T075121Z-001/chatGPT chatbot/tutorial-1/backend.md"
#loader = UnstructuredMarkdownLoader(markdown_path, mode="elements")
#loader = DirectoryLoader("./tutorial-1", glob="**/*.txt",loader_cls=UnstructuredMarkdownLoader, show_progress=True, use_multithreading=True) #naloaduje vsetky subory s priponou .txt
#loader = DirectoryLoader("./tutorial-1", glob="**/*.md",loader_cls=UnstructuredMarkdownLoader, show_progress=True, use_multithreading=True)
#data = loader.load()
#data[0]
#len(data)
index = VectorstoreIndexCreator().from_loaders([loader])

print(index.query(query))

#print(index.query(query, llm=ChatOpenAI()))
