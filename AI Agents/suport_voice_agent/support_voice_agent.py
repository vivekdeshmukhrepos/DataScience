from typing import List, Dict, Optional
from pathlib import Path
from firecrawl import FirecrawlApp
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from fastembed import TextEmbedding
from agents import Agent, Runner
from openai import AsyncOpenAI
import tempfile
import uuid
import os
from datetime import datetime
import time
import streamlit as st
from dotenv import load_dotenv
import asyncio
 
def init_session_state():
    defaults = {
        "initialized": False,
        "QDRANT_URL": "<QDRANT_URL>",
        "QDRANT_API_KEY": "<QDRANT_API_KEY>",
        "FIRECRAWL_API_KEY": "<FIRECRAWL_API_KEY>",
        "OPENAI_API_KEY": "sk-proj-",
        "DOC_URL": "https://docs.firecrawl.dev/introduction",
        "setup_complete": False,
        "client": None,
        "embedding_model": None,
        "processor_agent": None,
        "tts_agent": None,
        "selected_voice": "coral"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

st.set_page_config(
        page_title="Customer Support Voice Agent",
        page_icon="🎙️",
        layout="wide"
    )
st.title("🎙️ Customer Support Voice Agent")
st.caption("Your personal assistant for website — with voice!")


def sidebar_config():
    with st.sidebar:
        st.markdown("### 🎤 Voice Settings")
        voices = ["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"]
        st.session_state.selected_voice = st.selectbox(
            "Select Voice",
            options=voices,
            index=voices.index(st.session_state.selected_voice),
            help="Choose the voice for audio response"
        )
        if st.button("📥 Load Docs & Index"):
            if all([
                st.session_state.QDRANT_URL,
                st.session_state.QDRANT_API_KEY,
                st.session_state.FIRECRAWL_API_KEY,
                st.session_state.OPENAI_API_KEY,
                st.session_state.DOC_URL
            ]):
                progress_placeholder = st.empty()
                with progress_placeholder.container():
                    try:
                        st.markdown("🔄 Setting up Qdrant connection...")
                        client, embedding_model = setup_qdrant_collection(
                            st.session_state.QDRANT_URL,
                            st.session_state.QDRANT_API_KEY
                        )
                        st.session_state.client = client
                        st.session_state.embedding_model = embedding_model
                        st.markdown("✅ Qdrant setup complete!")
                        
                        st.markdown("🔄 Crawling and indexing documentation...")
                        pages = crawl_documentation(
                            st.session_state.FIRECRAWL_API_KEY,
                            st.session_state.DOC_URL
                        )
                        st.markdown(f"✅ Crawled {len(pages)} documentation pages!")
                        
                        store_embeddings(
                            client,
                            embedding_model,
                            pages,
                            "docs_embeddings"
                        )
                        
                        processor_agent, tts_agent = setup_agents(
                            st.session_state.OPENAI_API_KEY
                        )
                        st.session_state.processor_agent = processor_agent
                        st.session_state.tts_agent = tts_agent
                        
                        st.session_state.setup_complete = True
                        st.success("✅ System initialized successfully!")
                        
                    except Exception as e:
                        st.error(f"Error during setup: {str(e)}")
            else:
                st.error("Please click on Load Docs & Index!")

def setup_qdrant_collection(QDRANT_URL: str, QDRANT_API_KEY: str, collection_name: str = "docs_embeddings"):
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    embedding_model = TextEmbedding()
    test_embedding = list(embedding_model.embed(["test"]))[0]
    embedding_dim = len(test_embedding)
    
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
        )
    except Exception as e:
        if "already exists" not in str(e):
            raise e
    
    return client, embedding_model

def crawl_documentation(FIRECRAWL_API_KEY: str, url: str, output_dir: Optional[str] = None):
    firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    pages = []

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    response = firecrawl.crawl_url(
        url,
        limit= 5,
        params={
            'scrapeOptions': {
                'formats': ['markdown', 'html']
            }
        }
    )

    # Convert the response to a dictionary
    response_dict = response.model_dump()

    while True:
        for page in response_dict.get('data', []):
            content = page.get('markdown') or page.get('html', '')
            metadata = page.get('metadata', {})
            source_url = metadata.get('sourceURL', '')

            if output_dir and content:
                filename = f"{uuid.uuid4()}.md"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

            pages.append({
                "content": content,
                "url": source_url,
                "metadata": {
                    "title": metadata.get('title', ''),
                    "description": metadata.get('description', ''),
                    "language": metadata.get('language', 'en'),
                    "crawl_date": datetime.now().isoformat()
                }
            })

        next_url = response_dict.get('next')
        if not next_url:
            break

        response = firecrawl.get(next_url)
        response_dict = response.model_dump()  # Update dict for next iteration
        time.sleep(1)

    return pages
def store_embeddings(client: QdrantClient, embedding_model: TextEmbedding, pages: List[Dict], collection_name: str):
    for page in pages:
        embedding = list(embedding_model.embed([page["content"]]))[0]
        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding.tolist(),
                    payload={
                        "content": page["content"],
                        "url": page["url"],
                        **page["metadata"]
                    }
                )
            ]
        )

def setup_agents(OPENAI_API_KEY: str):
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    
    processor_agent = Agent(
        name="Documentation Processor",
        instructions="""You are a helpful documentation assistant. Your task is to:
        1. Analyze the provided documentation content
        2. Answer the user's question clearly and concisely
        3. Include relevant examples when available
        4. Cite the source URLs when referencing specific content
        5. Keep responses natural and conversational
        6. Format your response in a way that's easy to speak out loud""",
        model="gpt-4o"
    )

    tts_agent = Agent(
        name="Text-to-Speech Agent",
        instructions="""You are a text-to-speech agent. Your task is to:
        1. Convert the processed documentation response into natural speech
        2. Maintain proper pacing and emphasis
        3. Handle technical terms clearly
        4. Keep the tone professional but friendly
        5. Use appropriate pauses for better comprehension
        6. Ensure the speech is clear and well-articulated""",
        model="gpt-4o-mini-tts"
    )
    
    return processor_agent, tts_agent

async def process_query(
    query: str,
    client: QdrantClient,
    embedding_model: TextEmbedding,
    processor_agent: Agent,
    tts_agent: Agent,
    collection_name: str,
    OPENAI_API_KEY: str
):
    try:
        query_embedding = list(embedding_model.embed([query]))[0]
        search_response = client.query_points(
            collection_name=collection_name,
            query=query_embedding.tolist(),
            limit=3,
            with_payload=True
        )
        
        search_results = search_response.points if hasattr(search_response, 'points') else []
        
        if not search_results:
            raise Exception("No relevant documents found in the vector database")
        
        context = "Based on the following documentation:\n\n"
        for result in search_results:
            payload = result.payload
            if not payload:
                continue
            url = payload.get('url', 'Unknown URL')
            content = payload.get('content', '')
            context += f"From {url}:\n{content}\n\n"
        
        context += f"\nUser Question: {query}\n\n"
        context += "Please provide a clear, concise answer that can be easily spoken out loud."
        
        processor_result = await Runner.run(processor_agent, context)
        processor_response = processor_result.final_output
        
        tts_result = await Runner.run(tts_agent, processor_response)
        tts_response = tts_result.final_output
        
        async_openai = AsyncOpenAI(api_key=OPENAI_API_KEY)
        audio_response = await async_openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=st.session_state.selected_voice,
            input=processor_response,
            instructions=tts_response,
            response_format="mp3"
        )
        
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, f"response_{uuid.uuid4()}.mp3")
        
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)
                
        return {
            "status": "success",
            "text_response": processor_response,
            "tts_instructions": tts_response,
            "audio_path": audio_path,
            "sources": [r.payload.get("url", "Unknown URL") for r in search_results if r.payload],
            "query_details": {
                "vector_size": len(query_embedding),
                "results_found": len(search_results),
                "collection_name": collection_name
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": query
        }

def run_streamlit():
    
    init_session_state()
    sidebar_config()
    
    query = st.text_input(
        "💬 Ask a question about the documentation:",
        placeholder="e.g., How do I authenticate with the API?",
        disabled=not st.session_state.setup_complete
    )
    
    if query and st.session_state.setup_complete:
        with st.status("Processing your query...", expanded=True) as status:
            try:
                st.markdown("🔄 Searching documentation and generating response...")
                result = asyncio.run(process_query(
                    query,
                    st.session_state.client,
                    st.session_state.embedding_model,
                    st.session_state.processor_agent,
                    st.session_state.tts_agent,
                    "docs_embeddings",
                    st.session_state.OPENAI_API_KEY
                ))
                
                if result["status"] == "success":
                    status.update(label="✅ Query processed!", state="complete")
                    
                    st.markdown("### Response:")
                    st.write(result["text_response"])
                    
                    if "audio_path" in result:
                        st.markdown(f"### 🔊 Audio Response (Voice: {st.session_state.selected_voice})")
                        st.audio(result["audio_path"], format="audio/mp3", start_time=0)
                        
                        with open(result["audio_path"], "rb") as audio_file:
                            audio_bytes = audio_file.read()
                            st.download_button(
                                label="📥 Download Audio Response",
                                data=audio_bytes,
                                file_name=f"voice_response_{st.session_state.selected_voice}.mp3",
                                mime="audio/mp3"
                            )
                    
                    st.markdown("### Sources:")
                    for source in result["sources"]:
                        st.markdown(f"- {source}")
                else:
                    status.update(label="❌ Error processing query", state="error")
                    st.error(f"Error: {result.get('error', 'Unknown error occurred')}")
                    
            except Exception as e:
                status.update(label="❌ Error processing query", state="error")
                st.error(f"Error processing query: {str(e)}")
    
    elif not st.session_state.setup_complete:
        st.info("👈 Please click on Load Docs & Index first!")

if __name__ == "__main__":
    run_streamlit()