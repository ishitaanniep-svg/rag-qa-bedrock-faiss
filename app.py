import streamlit as st
import os
import json
from pathlib import Path
from typing import List, Tuple
import time
from datetime import datetime
import uuid

# AWS and LangChain imports
import boto3
from botocore.exceptions import ClientError
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_core.prompts import PromptTemplate
from utils import RetrieverManager
from evaluation_logging import (
    RAGASEvaluator,
    PerformanceTracker,
    ResponsibleAIMonitor,
    QueryLogger,
    QueryLog
)

# Configure Streamlit page
st.set_page_config(
    page_title="Local RAG Q&A Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton > button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "bedrock_llm" not in st.session_state:
    st.session_state.bedrock_llm = None
if "bedrock_embeddings" not in st.session_state:
    st.session_state.bedrock_embeddings = None
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "retriever_manager" not in st.session_state:
    st.session_state.retriever_manager = None
if "retrieval_strategy" not in st.session_state:
    st.session_state.retrieval_strategy = os.getenv("RETRIEVAL_STRATEGY", "semantic")
if "ragas_evaluator" not in st.session_state:
    st.session_state.ragas_evaluator = None
if "responsible_ai_monitor" not in st.session_state:
    st.session_state.responsible_ai_monitor = None
if "query_logger" not in st.session_state:
    st.session_state.query_logger = QueryLogger()
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "enable_ragas" not in st.session_state:
    st.session_state.enable_ragas = os.getenv("ENABLE_RAGAS_EVALUATION", "true").lower() == "true"
if "enable_responsible_ai" not in st.session_state:
    st.session_state.enable_responsible_ai = os.getenv("ENABLE_RESPONSIBLE_AI", "true").lower() == "true"


@st.cache_resource
def initialize_bedrock_clients():
    """Initialize Bedrock embeddings and LLM clients"""
    try:
        embeddings = BedrockEmbeddings(
            region_name="us-east-1",
            model_id="amazon.titan-embed-text-v1"
        )
        
        llm = ChatBedrock(
            region_name="us-east-1",
            model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        return embeddings, llm
    except ClientError as e:
        st.error(f"AWS Bedrock Error: {str(e)}")
        st.info("Please ensure you have configured AWS credentials and have access to Bedrock models.")
        return None, None


def load_and_process_pdfs(pdf_files: List) -> Tuple[int, int]:
    """Load and process PDF files, return (total_documents, total_chunks)"""
    documents = []
    total_docs = 0
    
    for pdf_file in pdf_files:
        try:
            # Save uploaded file temporarily
            with open(f"temp_{pdf_file.name}", "wb") as f:
                f.write(pdf_file.getbuffer())
            
            # Load PDF
            loader = PyPDFLoader(f"temp_{pdf_file.name}")
            pages = loader.load()
            documents.extend(pages)
            total_docs += len(pages)
            
            # Clean up temp file
            os.remove(f"temp_{pdf_file.name}")
            
        except Exception as e:
            st.warning(f"Error loading {pdf_file.name}: {str(e)}")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    
    return total_docs, len(chunks)


def create_vector_store(pdf_files: List) -> bool:
    """Create FAISS vector store from PDF files"""
    try:
        with st.spinner("Processing documents..."):
            # Load and process PDFs
            total_docs, total_chunks = load_and_process_pdfs(pdf_files)
            
            if not pdf_files:
                st.error("No PDF files to process")
                return False
            
            st.write(f"📄 Loaded {total_docs} pages into {total_chunks} chunks")
            
        # Create vector store
        with st.spinner("Creating vector embeddings (this may take a moment)..."):
            documents = []
            
            for pdf_file in pdf_files:
                with open(f"temp_{pdf_file.name}", "wb") as f:
                    f.write(pdf_file.getbuffer())
                
                loader = PyPDFLoader(f"temp_{pdf_file.name}")
                pages = loader.load()
                documents.extend(pages)
                
                os.remove(f"temp_{pdf_file.name}")
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create FAISS vector store
            if not chunks:
                st.error("No documents to embed")
                return False
                
            st.session_state.vector_store = FAISS.from_documents(
                chunks,
                st.session_state.bedrock_embeddings
            )
            
            # Initialize retriever manager with advanced strategies
            st.session_state.retriever_manager = RetrieverManager(
                st.session_state.vector_store,
                st.session_state.bedrock_llm
            )
            st.session_state.retriever_manager.initialize_strategy(
                st.session_state.retrieval_strategy
            )
            
        st.success("✅ Vector store created successfully!")
        st.session_state.documents_loaded = True
        
        # Save vector store locally
        save_vector_store()
        
        return True
        
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return False


def save_vector_store(store_path: str = "faiss_store"):
    """Save FAISS vector store locally"""
    try:
        if st.session_state.vector_store:
            st.session_state.vector_store.save_local(store_path)
            st.success(f"✅ Vector store saved to {store_path}/")
    except Exception as e:
        st.warning(f"Could not save vector store: {str(e)}")


def load_vector_store(store_path: str = "faiss_store") -> bool:
    """Load FAISS vector store from local storage"""
    try:
        if os.path.exists(store_path):
            with st.spinner("Loading vector store..."):
                st.session_state.vector_store = FAISS.load_local(
                    store_path,
                    st.session_state.bedrock_embeddings,
                    allow_dangerous_deserialization=True
                )
                
                # Initialize retriever manager with advanced strategies
                st.session_state.retriever_manager = RetrieverManager(
                    st.session_state.vector_store,
                    st.session_state.bedrock_llm
                )
                st.session_state.retriever_manager.initialize_strategy(
                    st.session_state.retrieval_strategy
                )
                
            st.session_state.documents_loaded = True
            return True
    except Exception as e:
        st.warning(f"Could not load existing vector store: {str(e)}")
    return False


def create_qa_chain():
    """Create RetrievalQA chain"""
    if not st.session_state.vector_store or not st.session_state.bedrock_llm:
        return None
    
    prompt_template = """Use the following pieces of context to answer the user's question. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Create a simple QA function using the retriever manager
    def qa_chain(query, k=3):
        # Use retriever manager if available, otherwise fallback
        if st.session_state.retriever_manager:
            docs = st.session_state.retriever_manager.retrieve(query, k=k)
        else:
            docs = st.session_state.vector_store.similarity_search(query, k=k)
        
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt_text = prompt_template.format(context=context, question=query)
        answer = st.session_state.bedrock_llm.invoke(prompt_text)
        return {"result": answer, "source_documents": docs}
    
    return qa_chain


def main():
    st.title("🤖 Local RAG Q&A Chatbot")
    st.markdown("*Powered by Amazon Bedrock, FAISS, and LangChain*")
    
    # Initialize Bedrock clients
    if st.session_state.bedrock_embeddings is None:
        with st.spinner("Initializing AWS Bedrock..."):
            embeddings, llm = initialize_bedrock_clients()
            if embeddings and llm:
                st.session_state.bedrock_embeddings = embeddings
                st.session_state.bedrock_llm = llm
                
                # Initialize evaluation and monitoring components
                st.session_state.ragas_evaluator = RAGASEvaluator(llm)
                st.session_state.responsible_ai_monitor = ResponsibleAIMonitor(llm)
            else:
                st.stop()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Document upload section
        st.subheader("📤 Upload Documents")
        pdf_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Create Vector Store", use_container_width=True):
                if pdf_files:
                    create_vector_store(pdf_files)
                else:
                    st.error("Please upload PDF files first")
        
        with col2:
            if st.button("💾 Load Saved Store", use_container_width=True):
                if load_vector_store():
                    st.success("Vector store loaded!")
        
        # Display status
        st.divider()
        st.subheader("📊 Status")
        if st.session_state.documents_loaded:
            st.info("✅ Documents loaded and ready for questions")
            
            # Show vector store info
            if st.session_state.vector_store:
                st.metric("Vector Store Index", "Active")
        else:
            st.warning("⚠️ No documents loaded yet")
        
        # Settings
        st.divider()
        st.subheader("🎛️ Settings")
        
        # Retrieval Strategy Selection
        if st.session_state.documents_loaded and st.session_state.retriever_manager:
            available_strategies = st.session_state.retriever_manager.list_available_strategies()
            selected_strategy = st.selectbox(
                "Retrieval Strategy",
                available_strategies,
                index=available_strategies.index(st.session_state.retrieval_strategy) 
                    if st.session_state.retrieval_strategy in available_strategies else 0
            )
            
            if selected_strategy != st.session_state.retrieval_strategy:
                st.session_state.retriever_manager.switch_strategy(selected_strategy)
                st.session_state.retrieval_strategy = selected_strategy
                st.success(f"✅ Switched to {selected_strategy} strategy")
            
            # Show strategy info
            strategy_info = st.session_state.retriever_manager.get_strategy_info()
            with st.expander("ℹ️ Strategy Details"):
                st.json(strategy_info)
        
        retrieval_k = st.slider(
            "Number of similar documents to retrieve",
            min_value=1,
            max_value=5,
            value=3
        )
        
        temperature = st.slider(
            "Model Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        
        # Evaluation & Logging Settings
        st.divider()
        st.subheader("📊 Evaluation & Logging")
        
        st.session_state.enable_ragas = st.checkbox(
            "Enable RAGAS Evaluation",
            value=st.session_state.enable_ragas,
            help="Evaluate faithfulness and context recall (adds latency)"
        )
        
        st.session_state.enable_responsible_ai = st.checkbox(
            "Enable Responsible AI Filtering",
            value=st.session_state.enable_responsible_ai,
            help="Filter responses for inappropriate content"
        )
        
        if st.button("📈 View Metrics Dashboard", use_container_width=True):
            st.session_state.show_metrics = True
    
    # Main content area
    if st.session_state.documents_loaded:
        st.success("✅ Ready to answer questions!")
        
        # Create QA chain if not exists
        if st.session_state.qa_chain is None:
            st.session_state.qa_chain = create_qa_chain()
        
        # Question input
        st.subheader("❓ Ask a Question")
        user_question = st.text_input(
            "Enter your question about the documents:",
            placeholder="What is the main topic of the documents?"
        )
        
        if user_question:
            with st.spinner("🔍 Searching and generating answer..."):
                # Initialize performance tracker
                perf_tracker = PerformanceTracker()
                perf_tracker.start_total()
                
                retrieved_docs = []
                ragas_metrics = None
                responsible_ai_events = []
                success = True
                error_message = None
                original_answer = ""
                filtered_answer = ""
                
                try:
                    # Track retrieval performance
                    perf_tracker.start_retrieval()
                    response = st.session_state.qa_chain(user_question, k=retrieval_k)
                    retrieved_docs = response.get("source_documents", [])
                    perf_tracker.end_retrieval(len(retrieved_docs))
                    
                    # Track LLM performance
                    perf_tracker.start_llm()
                    original_answer = response["result"].content if hasattr(response["result"], "content") else str(response["result"])
                    
                    # Estimate tokens (rough approximation)
                    input_tokens = len(user_question.split()) * 1.3
                    output_tokens = len(original_answer.split()) * 1.3
                    perf_tracker.end_llm(int(input_tokens), int(output_tokens))
                    
                    # Responsible AI filtering
                    if st.session_state.enable_responsible_ai and st.session_state.responsible_ai_monitor:
                        filtered_answer, was_filtered, filter_reason = st.session_state.responsible_ai_monitor.filter_response(
                            user_question,
                            original_answer
                        )
                        responsible_ai_events = [
                            event.to_dict() for event in st.session_state.responsible_ai_monitor.get_events()
                        ]
                        
                        if was_filtered:
                            st.warning(f"⚠️ Response filtered: {filter_reason}")
                    else:
                        filtered_answer = original_answer
                    
                    # RAGAS Evaluation
                    if st.session_state.enable_ragas and st.session_state.ragas_evaluator:
                        with st.spinner("📊 Evaluating response quality..."):
                            ragas_result = st.session_state.ragas_evaluator.evaluate_all(
                                query=user_question,
                                context=retrieved_docs,
                                answer=original_answer
                            )
                            ragas_metrics = ragas_result.to_dict()
                            
                            # Show quality metrics
                            if not ragas_result.meets_threshold():
                                st.warning("⚠️ Response quality below threshold")
                    
                    perf_tracker.end_total()
                    
                    # Display answer
                    st.subheader("💡 Answer")
                    st.markdown(filtered_answer)
                    
                    # Display metrics
                    perf_metrics = perf_tracker.get_metrics()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Retrieval Time", f"{perf_metrics.retrieval_latency_ms:.0f}ms")
                    with col2:
                        st.metric("LLM Time", f"{perf_metrics.llm_latency_ms:.0f}ms")
                    with col3:
                        st.metric("Total Time", f"{perf_metrics.total_latency_ms:.0f}ms")
                    
                    # Display RAGAS metrics if enabled
                    if ragas_metrics:
                        with st.expander("📊 RAGAS Quality Metrics"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(
                                    "Faithfulness",
                                    f"{ragas_metrics['faithfulness']:.2f}",
                                    delta="Good" if ragas_metrics['faithfulness'] >= 0.80 else "Low"
                                )
                                st.metric(
                                    "Context Precision",
                                    f"{ragas_metrics['context_precision']:.2f}"
                                )
                            with col2:
                                st.metric(
                                    "Context Recall",
                                    f"{ragas_metrics['context_recall']:.2f}",
                                    delta="Good" if ragas_metrics['context_recall'] >= 0.70 else "Low"
                                )
                                st.metric(
                                    "Answer Relevancy",
                                    f"{ragas_metrics['answer_relevancy']:.2f}"
                                )
                    
                    # Display source documents
                    with st.expander("📚 Source Documents"):
                        if retrieved_docs:
                            for i, doc in enumerate(retrieved_docs, 1):
                                st.markdown(f"**Source {i}:**")
                                st.text(doc.page_content[:500] + "...")
                                if doc.metadata:
                                    st.caption(f"Metadata: {doc.metadata}")
                    
                    # Log query
                    query_log = QueryLog(
                        timestamp=datetime.now().isoformat(),
                        session_id=st.session_state.session_id,
                        query=user_question,
                        response=filtered_answer,
                        retrieval_strategy=st.session_state.retrieval_strategy,
                        documents_retrieved=[doc.page_content[:200] for doc in retrieved_docs],
                        performance_metrics=perf_metrics.to_dict(),
                        ragas_metrics=ragas_metrics,
                        responsible_ai_events=responsible_ai_events,
                        success=success,
                        error_message=error_message
                    )
                    st.session_state.query_logger.log_query(query_log)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": user_question,
                        "answer": filtered_answer,
                        "timestamp": time.time(),
                        "metrics": perf_metrics.to_dict(),
                        "ragas": ragas_metrics
                    })
                    
                except Exception as e:
                    success = False
                    error_message = str(e)
                    st.error(f"Error generating answer: {error_message}")
                    
                    # Log failed query
                    perf_tracker.end_total()
                    query_log = QueryLog(
                        timestamp=datetime.now().isoformat(),
                        session_id=st.session_state.session_id,
                        query=user_question,
                        response="",
                        retrieval_strategy=st.session_state.retrieval_strategy,
                        documents_retrieved=[],
                        performance_metrics=perf_tracker.get_metrics().to_dict(),
                        ragas_metrics=None,
                        responsible_ai_events=[],
                        success=success,
                        error_message=error_message
                    )
                    st.session_state.query_logger.log_query(query_log)
        
        # Chat history
        if st.session_state.chat_history:
            st.divider()
            st.subheader("📜 Chat History")
            
            for i, item in enumerate(st.session_state.chat_history, 1):
                with st.expander(f"Q{i}: {item['question'][:50]}..."):
                    st.write(f"**Question:** {item['question']}")
                    st.write(f"**Answer:** {item['answer']}")
                    
                    if 'metrics' in item:
                        st.caption(f"⏱️ Response time: {item['metrics']['total_latency_ms']:.0f}ms")
                    
                    if 'ragas' in item and item['ragas']:
                        st.caption(
                            f"📊 Quality: F={item['ragas']['faithfulness']:.2f} | "
                            f"CR={item['ragas']['context_recall']:.2f}"
                        )
    
    else:
        st.info("👈 Start by uploading PDF documents in the sidebar")
        
        # Instructions
        with st.expander("📖 How to use this app"):
            st.markdown("""
            1. **Upload PDFs**: Click the "Upload Documents" button in the sidebar
            2. **Create Vector Store**: Click "Create Vector Store" to process the documents
            3. **Ask Questions**: Type your question in the main area
            4. **View Results**: See the AI-generated answer with source citations
            5. **Load Saved Store**: Reuse previously created vector stores
            
            **Features:**
            - 🔍 Semantic search using FAISS
            - 🤖 AI-powered answers using Amazon Bedrock
            - 📚 Source document references
            - 💾 Local vector store persistence
            """)


if __name__ == "__main__":
    main()

