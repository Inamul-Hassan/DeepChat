from langchain_community.document_loaders import WebBaseLoader, RecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate, MessagesPlaceholder, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.messages import AIMessage, HumanMessage, ChatMessage

from bs4 import BeautifulSoup as Soup
from dotenv import load_dotenv


load_dotenv()

# import os
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# print(GOOGLE_API_KEY)


def multi_loader(url, method):
    match method:
        case "WebBaseLoader":
            loader = WebBaseLoader(url)
            document = loader.aload()
            return document, len(document)
        case "RecursiveUrlLoader":
            loader = RecursiveUrlLoader(
                url=url, max_depth=2, extractor=lambda x: Soup(x, "html.parser").text)
            document = loader.load()
            length = len(document)
            return document, length
        case _:
            return "Invalid method"


def get_data_from_url(url):
    loader = WebBaseLoader(url)
    document = loader.load()
    return document


def split_document(document):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, chunk_overlap=200)
    return splitter.split_documents(documents=document)


def vector_store_document(document):
    print(len(document))
    vector_store = Chroma.from_documents(
        document, GoogleGenerativeAIEmbeddings(model='models/embedding-001'))
    return vector_store


def get_context_retriever_chain(vector_store: Chroma):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")

    retriever = vector_store.as_retriever()
    # TODO implement history with google gen ai package

    # prompt = ChatPromptTemplate.from_messages([
    #     ("user", "USER INPUT: \n {input} \n Given the above user input, generate a search query to look up in a vector database in order to get information relevant to the conversation")
    # ])
    # prompt.format_prompt(input="What is langgraph?")

    # response = retriever.get_relevant_documents("whay is langgraph?")
    # print(response)

    # retriever_chain = create_history_aware_retriever(
    #     llm=llm, retriever=retriever, prompt="what is ")

    return retriever


def conversational_rag_chain(retriever_chain):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")

    prompt = ChatPromptTemplate.from_messages([
        ("user",
         "Answer the following questions based on the below context \n\n CONTEXT: \n {context} \n\n QUESTION: \n {input}"),
    ])

    stuff_documents_chain = create_stuff_documents_chain(
        llm=llm, prompt=prompt)

    return create_retrieval_chain(retriever=retriever_chain, combine_docs_chain=stuff_documents_chain)


def get_response(website_url, user_query):
    document = get_data_from_url(website_url)
    chunks = split_document(document)
    vector_store = vector_store_document(chunks)
    retriever_chain = get_context_retriever_chain(
        vector_store=vector_store)
    conversation_chain = conversational_rag_chain(
        retriever_chain=retriever_chain)
    response = conversation_chain.invoke({
        "input": user_query
    })

    return response['answer']


if __name__ == "__main__":
    # url = "https://www.cricbuzz.com/cricket-news/129561/kl-rahul-ruled-out-of-ranchi-test-bumrah-rested"
    # print(url)
    # message = "user: write python code to write contents to a text file"
    # llm = ChatGoogleGenerativeAI(model="gemini-pro")
    # prompt = PromptTemplate.from_template(message)
    # print(prompt)
    # response = llm.invoke(input=prompt)
    # print(response)

    # document = get_data_from_url(url)
    # chunks = split_document(document)
    # vector_store = vector_store_document(chunks)

    # response = retriever_chain = get_context_retriever_chain(
    #     vector_store=vector_store)
    # out = conversational_rag_chain(response)
    # response = out.invoke({
    #     'input': 'why rahul ruled out?'
    # })
    # print(len(response))
    # print(response)

    # retriever_chain.invoke()

    # docs = get_data_from_url(url)
    # print(docs)
    # # print(docs[0].page_content)
    # chunks = split_document(docs)
    # print(len(chunks))
    # print(chunks[1].page_content)
    # # docs = get_data_from_url(url, 'SiteMapLoader')
    pass
