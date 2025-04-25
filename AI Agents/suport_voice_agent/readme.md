# 🎙️ Interactive AI Voice Support Agent

A Streamlit-based AI assistant that crawls documentation from a website, stores it in a vector database, and provides natural, voice-based answers to user queries using OpenAI's GPT and TTS models.

---

## 🚀 Features

- 🔍 **Automatic Documentation Crawling** via [Firecrawl](https://firecrawl.dev)
- 📚 **Semantic Search** powered by [Qdrant Vector DB](https://qdrant.tech)
- 🧠 **Context-Aware Question Answering** using GPT-4o
- 🗣️ **Realistic Text-to-Speech Responses** via OpenAI's TTS engine
- 🎛️ **Interactive Voice Selection** for different speaking styles
- 🖥️ **Streamlit UI** for an intuitive and responsive user experience

---

## 🧩 Architecture Overview

```plaintext
User Query
   ↓
Streamlit UI
   ↓
Embed Query (FastEmbed)
   ↓
Qdrant DB Search
   ↓
Relevant Docs → Processor Agent (GPT-4o)
   ↓
Answer → TTS Agent (GPT-4o-mini-TTS)
   ↓
Audio Generation → Streamlit Audio Player

```

## 🛠️ Setup Instructions

1. Clone the Repository
```
git clone https://github.com/your-username/support_voice_agent.git
cd support_voice_agent
```
2. Install Python Dependencies
```
pip install -r requirements.txt
```
3. Initialize Variables
```
QDRANT_URL=https://your-qdrant-url
QDRANT_API_KEY=your_qdrant_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
OPENAI_API_KEY=your_openai_api_key
DOC_URL=https://docs.firecrawl.dev/introduction
```
4. Run the App
```
streamlit run support_voice_agent
```

##  🧱 Built With
* [OpenAI GPT-4o](https://platform.openai.com/docs/guides/gpt)
* [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech)
* [Firecrawl](https://firecrawl.dev/) - for documentation crawling
* [Qdrant](https://qdrant.tech/) - vector database
* [FastEmbed](https://github.com/qdrant/fastembed) - embedding generation
* [Streamlit](https://streamlit.io/) - frontend and app hosting
 

##  🙏 Acknowledgments
* [Awesome LLM Apps](https://github.com/Shubhamsaboo/awesome-llm-apps)
 