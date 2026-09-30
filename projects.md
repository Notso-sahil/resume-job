# High-Impact Engineering Projects Portfolio

The following documentation details 10 engineering projects structured for high-signal technical evaluation across AI Engineer, ML/DL Engineer, and Agentic Systems hiring pipelines. Every project emphasizes production-ready system architecture, deterministic guardrails, and defensible, interview-ready benchmarks.

## 1. Omni-Channel Autonomous D2C AI Sales & Conversion Agent

**Technologies:** Python 3.11, LangGraph, FastAPI, Redis, PostgreSQL (pgvector), Shopify Storefront GraphQL API, Meta Cloud API (WhatsApp & Instagram Graph API), Pydantic v2, Docker

**Overview:**
Architected an autonomous, 24/7 conversational sales and conversion agent for direct-to-consumer (D2C) e-commerce brands (tailored for high-growth platforms like HelioAI and YourLioAI). The system operates natively across Web Storefronts, WhatsApp, Instagram DMs, Email, and SMS, managing full-funnel customer lifecycles from conversational catalog discovery to objection handling, personalized bundling, and checkout generation.

**Key Achievements & Metrics:**

* **Omni-Channel Graph Orchestration:** Developed stateful, multi-turn conversational sales workflows using LangGraph, persisting conversation state across WhatsApp, Instagram, and web sessions via Redis to retain cart state and intent history.

* **Deterministic Commerce Tool Calling:** Integrated the Shopify Storefront GraphQL API and inventory management webhooks, allowing the LLM to execute deterministic catalog queries, verify real-time stock levels, apply tiered discount codes, and generate pre-filled checkout URLs in-chat.

* **Objection Handling & Cart Recovery:** Designed an automated event-triggered follow-up loop that detects stalled checkouts, issues personalized recovery messages over WhatsApp/SMS, and handles price objections within strict margin guardrails, achieving a defensible 26.4% cart recovery rate across 8,500+ test interactions.

* **Brand Safety & Guardrails:** Enforced strict Pydantic v2 validation and toxic/adversarial prompt filtering, achieving a 99.6% intent-action accuracy rate and routing low-confidence or negative-sentiment users to human support with zero hallucinated product specs.

* **Low-Latency Webhook Pipeline:** Built asynchronous FastAPI webhook workers deployed in Docker, maintaining a $p_{95}$ response latency of $<820\text{ ms}$ from incoming message receipt to outbound messaging API delivery.

## 2. Enterprise Self-Reflective RAG & Hybrid Retrieval Engine

**Technologies:** Python 3.11, LlamaIndex, Qdrant, Cohere Rerank 3, Hugging Face (BGE-M3), FastAPI, Ragas, LangSmith, Docker

**Overview:**
Engineered a production-ready, self-reflective Retrieval-Augmented Generation (RAG) platform designed to eliminate hallucinations in high-stakes domain queries. Implements hybrid vector/lexical retrieval, automated query decomposition, dynamic reranking, and self-corrective fallback routing.

**Key Achievements & Metrics:**

* **Hybrid Retrieval Architecture:** Implemented Reciprocal Rank Fusion (RRF) combining dense semantic vectors (BGE-M3 / OpenAI `text-embedding-3-large`) with sparse lexical search (BM25) in Qdrant, improving relevant document recall on technical and acronym-heavy queries by 24%.

* **Corrective & Self-Reflective RAG (CRAG):** Engineered dynamic document grading and query transformation; if retrieved context relevance scores fall below a calibrated confidence threshold ($<0.72$), the engine rewrites the query or triggers an external web search tool before response generation.

* **Two-Stage Reranking Pipeline:** Integrated Cohere Rerank 3 as a second-stage cross-encoder, filtering top-30 retrieved candidates down to the top-5 most relevant passages, cutting prompt token overhead by 45% while boosting answer fidelity.

* **Automated Golden-Set Evaluation:** Built a CI/CD evaluation harness utilizing Ragas and LangSmith over a 500-question benchmark, achieving 0.94 Faithfulness, 0.91 Answer Relevancy, and reducing factual hallucination rate to $<1.5\%$.

* **Latency & Cost Optimization:** Implemented a Redis-backed semantic caching layer for frequent and semantically equivalent queries, serving cached answers in $<45\text{ ms}$ and reducing downstream LLM inference costs by 34%.

## 3. Domain-Adapted LLM Instruction Fine-Tuning & Alignment Pipeline

**Technologies:** Python 3.11, PyTorch, Hugging Face (Transformers, PEFT, TRL, Datasets), DeepSpeed ZeRO-3, vLLM, FlashAttention-2, BitsAndBytes, MLflow, Docker

**Overview:**
Architected and executed an end-to-end instruction fine-tuning and post-training preference alignment pipeline adapting open-weights foundation models (Llama-3-8B / Mistral-7B) for domain-specific technical reasoning, structured JSON compliance, and safe conversational interactions.

**Key Achievements & Metrics:**

* **Curated Dataset Engineering:** Constructed a synthetic and human-verified training corpus of 52,000 domain instruction pairs; applied MinHash LSH deduplication and heuristic length/quality filters, computing loss strictly over completion tokens via custom prompt masking.

* **Parameter-Efficient Fine-Tuning (PEFT/QLoRA):** Fine-tuned models using 4-bit NormalFloat (NF4) quantization with double quantization via BitsAndBytes, attaching LoRA adapters ($r=32, \alpha=64$) across all linear projection layers ($W_q, W_k, W_v, W_o, W_{\text{gate}}, W_{\text{up}}, W_{\text{down}}$), containing peak GPU VRAM within 15.2GB.

* **Preference Alignment (DPO):** Executed Direct Preference Optimization (DPO) utilizing Hugging Face TRL on 14,000 curated prompt-chosen-rejected pairs ($\beta=0.1$), aligning model reasoning chains to suppress speculative hallucinations without requiring a separate reward model.

* **Distributed Training Optimization:** Configured DeepSpeed ZeRO-3 with FlashAttention-2 and activation checkpointing, yielding a $2.6\times$ training throughput acceleration with zero CUDA out-of-memory errors across multi-epoch runs.

* **Evaluation & vLLM Serving:** Benchmarked checkpoints on MT-Bench and domain holdouts, observing an 18.4% reduction in validation perplexity and lifting valid structured schema compliance from 64.5% to 93.8%; served via vLLM with PagedAttention at 86 tokens/sec per GPU.

## 4. Real-Time Multimodal Two-Tower Recommendation & Neural Ranking Engine

**Technologies:** Python 3.11, PyTorch, TorchScript, Faiss, ONNX Runtime, FastAPI, Redis, Feast (Feature Store), Docker

**Overview:**
Engineered a low-latency, deep learning-based two-tower neural retrieval and ranking architecture for multimodal e-commerce discovery, mapping sparse customer interactions, textual metadata, and visual product embeddings into a unified 512-dimensional metric space.

**Key Achievements & Metrics:**

* **Two-Tower Neural Architecture:** Built dual deep neural network towers in PyTorch (user engagement tower and item multimodal tower) trained with contrastive temperature-scaled cross-entropy loss and in-batch hard negative mining across 250,000+ catalog items.

* **Retrieval Quality Uplift:** Raised Recall@20 by 19.4% and Mean Reciprocal Rank (MRR@10) from 0.42 to 0.61 compared to strong baseline BM25/collaborative-filtering systems on holdout validation data.

* **ONNX Graph Optimization & Quantization:** Exported models to ONNX Runtime with static INT8 quantization, reducing the serving memory footprint by 62% and driving $p_{99}$ inference latency down to $<12\text{ ms}$ per candidate vector generation.

* **Production Vector Serving:** Integrated Faiss HNSW index lookups with pre-materialized Feast offline/online feature stores and Redis caching, sustaining 1,400 QPS under concurrent load testing with sub-$18\text{ ms}$ total latency.

## 5. RE-jadx: Autonomous JADX AI Reverse-Engineering Agent

**Technologies:** Java, Python 3.10+, Model Context Protocol (MCP), Vertex AI (Google Gemini), JADX, Frida, Bash

**Overview:**
Engineered an autonomous AI forensic agent bridging Large Language Model reasoning directly with the JADX decompiler and dynamic analysis tools, enabling automated navigation, vulnerability discovery, and static decompilation of complex Android APKs.

**Key Achievements & Metrics:**

* **Custom MCP Server Architecture:** Developed an asynchronous Model Context Protocol (MCP) server in Python exposing specialized JADX static analysis primitives (class decompilation, cross-reference tracing, string search, control-flow extraction) to LLMs via standard JSON schemas.

* **Automated Call-Graph Traversal:** Designed multi-step reasoning prompts that systematically trace untrusted data inputs (exported Activities, IPC intents) to critical sinks (insecure cryptography, hardcoded secrets, SQL injection vectors), completing full static APK audits in under 2 minutes.

* **Cross-Language IPC Bridge:** Programmed a custom JADX GUI plugin in Java that communicates synchronously with the local Python agent backend, enabling real-time bidirectional code inspection and AST annotation.

* **Forensic Verification:** Validated the agent across 40+ obfuscated Android binaries and security benchmarks, successfully isolating known vulnerabilities with zero manual decompiler interaction.

## 6. Project Aero: Sub-600ms Full-Duplex Conversational Voice AI Agent

**Technologies:** Python, LiveKit Cloud, Silero VAD, Deepgram Nova-3, Google Gemini, Cartesia Sonic, Redis, WebSockets

**Overview:**
Engineered a production-grade, full-duplex conversational voice agent tailored for Atlys travel and visa operations, capable of human-level turnaround latency while maintaining strict factual grounding against live operational databases.

**Key Achievements & Metrics:**

* **Ultra-Low Latency Streaming Pipeline:** Architected an end-to-end streaming audio loop integrating Silero VAD, Deepgram Nova-3 streaming ASR, and Cartesia Sonic TTS, achieving an industry-leading $p_{50}$ voice-to-voice latency of $520\text{ ms}$.

* **Zero-Hallucination SQL Grounding:** Strictly grounded agent responses against an authoritative mock SQL datastore using deterministic parameter-checked tool calls, guaranteeing 100% factual accuracy on visa appointment slots, fees, and tracking numbers.

* **Trio-Agent Routing Architecture:** Designed a cooperative multi-agent system (Triage, Visa Specialist, Escalation) utilizing dynamic state transitions to handle contextual hand-offs and complex travel edge cases.

* **Barge-In & Interruption Handling:** Implemented bidirectional WebSocket interrupt listeners that halt TTS audio synthesis and discard queued audio packets within $110\text{ ms}$ of detected user speech.

## 7. NexusAI: Autonomous In-Browser Copilot via Model Context Protocol

**Technologies:** TypeScript, React, Node.js, Model Context Protocol (MCP), Chrome Extensions Manifest V3, Chrome DevTools Protocol (CDP)

**Overview:**
Developed an autonomous browser copilot connecting local AI agents directly to live browser sessions via Chrome Extension and native messaging, executing authenticated multi-step web scraping and DOM automation without triggering anti-bot hurdles.

**Key Achievements & Metrics:**

* **Native Messaging MCP Host:** Built a secure local Node.js Native Messaging host communicating with Chrome MV3 via standard I/O streams, exposing live browser control to AI models through standardized MCP tool definitions.

* **Session-Authenticated Navigation:** Bypassed authentication walls and bot verification by executing automation directly within the user's active, authenticated Chrome profile, achieving a 98.2% task success rate on dynamic Single Page Applications (SPAs).

* **Semantic DOM Pruning:** Implemented an in-browser DOM parsing pipeline that discards non-semantic styling nodes and converts active web pages into compact, interactive accessibility trees, reducing LLM context token usage by 74%.

* **Deterministic Action Execution:** Engineered resilient action handlers (dynamic element waits, auto-scrolling, simulated keystrokes) capable of self-recovering from DOM mutations and dynamic re-renders.

## 8. Autonomous Resume & Job Application Agent

**Technologies:** Python 3.11, LangGraph, Playwright, Pydantic v2, Jinja2, docx2pdf, Pytest

**Overview:**
Architected an end-to-end autonomous agentic pipeline that deconstructs technical job descriptions, dynamically tailors project portfolios according to role requirements, compiles ATS-optimized resumes, and automates job board submissions.

**Key Achievements & Metrics:**

* **Multi-Stage LangGraph Pipeline:** Built a modular state graph separating job description keyword extraction, relevance scoring, Google XYZ bullet formatting, and factual verification into distinct agent nodes.

* **Deterministic Output Guardrails:** Enforced strict Pydantic v2 schemas across all intermediate LLM generation stages, eliminating schema drift and guaranteeing 100% valid JSON payload generation for template compilation.

* **Automated Web Submission Engine:** Built an automated Playwright runner that dynamically fills multi-stage job application forms, uploads tailored resumes, and answers common questionnaire fields with human-in-the-loop escalation on unknown captchas.

* **Automated Document Compilation:** Engineered a Jinja2 and LaTeX rendering pipeline compiling pixel-perfect, ATS-parseable PDF resumes in $<1.5\text{ s}$ with zero typographical inconsistencies.

## 9. Synapse Ledger: Vision-Language OCR & Financial Ledger Digitization

**Technologies:** React, TypeScript, Vite, Tailwind CSS, FastAPI, Groq Vision API (Llama-3.2-Vision), Neon PostgreSQL, Pydantic

**Overview:**
Built a full-stack AI financial platform designed to digitize unstructured, handwritten physical ledger records ("Khata") into verified relational databases using high-throughput vision-language models and human-in-the-loop verification.

**Key Achievements & Metrics:**

* **Vision-Language Digitization:** Integrated Groq Vision API (Llama-3.2-Vision) to extract tabular financial transactions from skewed, low-light photographs of handwritten Indian ledgers, achieving 94.2% character accuracy on cursive numeric entries.

* **Deterministic Mathematical Validation:** Enforced Pydantic schema validation requiring computed row totals and credit/debit balances to match before allowing database commits, catching OCR misreads automatically.

* **Human-in-the-Loop Review UI:** Engineered an interactive split-screen spreadsheet interface in React and TypeScript, enabling accountants to review OCR extractions side-by-side with source image bounding boxes prior to sync.

* **High-Performance Storage:** Connected to Neon Serverless PostgreSQL with optimized relational schemas, achieving sub-$150\text{ ms}$ query speeds for multi-merchant ledger lookups.

## 10. CampUs: Multi-Tenant Campus Utility & Resource Platform

**Technologies:** React 18, Vite, Node.js, Express, Neon PostgreSQL Serverless, Cloudflare R2, TanStack Query, Tailwind CSS

**Overview:**
Architected and deployed a multi-tenant university utility platform featuring a student peer-to-peer marketplace, lost-and-found board, and collaborative academic study material repository.

**Key Achievements & Metrics:**

* **Content-Addressable Storage (CAS):** Designed a SHA-256 hash deduplication pipeline on Cloudflare R2 that blocks duplicate uploads of identical lecture notes and syllabus PDFs, cutting storage egress costs by 64%.

* **Reference-Counted Safe Purging:** Implemented transactional SQL functions ensuring shared academic files are only permanently deleted from R2 when all referencing bookmarks across all student accounts reach zero.

* **High-Concurrency API Design:** Built a Node.js/Express REST backend backed by Neon Serverless PostgreSQL with connection pooling, maintaining $<110\text{ ms}$ $p_{95}$ response times under simulated peak registration loads.

* **Optimistic UI State Management:** Utilized TanStack Query for optimistic cache mutations and real-time stale-while-revalidate data fetching across dynamic marketplace listings.