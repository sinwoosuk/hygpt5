from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import DirectoryLoader

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


# CSVLoader 확장
class CustomCSVLoader(CSVLoader):
    def __init__(self, file_path, encoding="CP949", **kwargs):
        super().__init__(file_path, encoding=encoding, **kwargs)


# DirectoryLoader 사용
csv_loader = DirectoryLoader("static/data", glob="*.csv", loader_cls=CustomCSVLoader)
data = csv_loader.load()


# VectorStore 및 Retriever 설정
vectorstore = Chroma.from_documents(documents=data, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 템플릿 객체 생성
template = """당신은 한영대학교의 정보에 대해서 알려주는 어시스턴트입니다.
다음과 같은 맥락을 사용하여 마지막 질문에 대답하십시오.
모르는 내용에 대해서는 대답하지 마십시오.
답변은 최대 세 문장으로 하고 가능한 한 간결하게 유지하십시오.
교수 또는 학교 정보에 대해 물어봤을때만 관련 내용에 대하여 답하십시오.
학교 이외의 내용을 물어봤을 때는 학교 내용을 배제하고 답하십시오.

가독성을 위해 적절히 줄바꿈을 사용하십시오.
말끝마다 상황에 적합한 이모지를 사용하십시오.
{context}
질문:{question}
도움이 되는 답변:"""

rag_prompt_custom = PromptTemplate.from_template(template)

# LLM 설정
# llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# RAG chain 설정
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} | rag_prompt_custom | llm
)


async def handle_query(question: str):
    try:
        # 질문을 처리하고 답변을 반환하는 함수
        answer = rag_chain.invoke(question)
        
        # answer가 객체일 경우 문자열로 변환하고 content만 반환
        if isinstance(answer, dict):
            content = answer[content]  # 'content' 필드에서 텍스트 가져오기
            
            content = content.replace('\\n', ' ').replace('\n', ' ')  # 개행 문자 제거
            print(content)
            return content.strip()  # 양쪽 공백 제거 후 반환
        return str(answer)
    except Exception as e:
        raise e