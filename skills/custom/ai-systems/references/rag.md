# Retrieval-augmented generation

Build LLM applications that ground responses in external knowledge via vector databases and semantic search.

## Use when

- Building Q&A over proprietary documents or documentation assistants
- Creating chatbots that need current, factual information
- Implementing semantic search with natural language queries
- Reducing hallucinations with grounded, source-cited responses
- Giving LLMs access to domain-specific knowledge

## Do not use when

- You only need purely generative writing without retrieval
- The dataset is too small to justify embeddings
- You cannot store or process the source data safely

## Instructions

1. Define the corpus, update cadence, and evaluation targets.
2. Choose embedding models and vector store based on scale.
3. Build ingestion, chunking, and retrieval with reranking.
4. Evaluate with grounded QA metrics and monitor drift.

## Safety

- Redact sensitive data and enforce access controls. For multi-tenant retrieval, filter the vector query by tenant/user at query time (metadata filter) so one tenant can never retrieve another's documents, treat this as a hard security control, not a convenience.
- Avoid exposing source documents in responses when restricted.
- Retrieved content is untrusted: it can carry injected instructions (indirect prompt injection) and the index can be poisoned. For RAG access-control, retrieval poisoning, and embedding leakage, harden with the **ai-hardening** skill.

## Core components

### Vector databases

Store and retrieve document embeddings efficiently.

- **Pinecone**: managed, scalable, fast queries
- **Weaviate**: open-source, hybrid search
- **Milvus**: high performance, on-premise
- **Chroma**: lightweight, easy to use
- **Qdrant**: fast, filtered search
- **FAISS**: Meta's library, local deployment

### Embeddings

Convert text to vectors for similarity search.

- **text-embedding-3-small** (OpenAI): general purpose, 1536 dims (legacy: text-embedding-ada-002)
- **all-MiniLM-L6-v2** (Sentence Transformers): fast, lightweight
- **e5-large-v2**: high quality, multilingual
- **bge-large-en-v1.5**: SOTA performance

### Retrieval strategies

- **Dense**: semantic similarity via embeddings
- **Sparse**: keyword matching (BM25, TF-IDF)
- **Hybrid**: combine dense + sparse
- **Multi-query**: generate multiple query variations
- **HyDE**: generate hypothetical documents

### Reranking

Reorder retrieved results to improve quality.

- **Cross-encoders**: BERT-based reranking
- **Cohere Rerank**: API-based
- **MMR (Maximal Marginal Relevance)**: diversity + relevance
- **LLM-based**: use an LLM to score relevance

## Quick start

```python
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# 1. Load documents
loader = DirectoryLoader('./docs', glob="**/*.txt")
documents = loader.load()

# 2. Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, length_function=len
)
chunks = text_splitter.split_documents(documents)

# 3. Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)

# 4. Create retrieval chain
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True
)

# 5. Query
result = qa_chain({"query": "What are the main features?"})
print(result['result'])
print(result['source_documents'])
```

## Advanced patterns

### Hybrid search

```python
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 5
embedding_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, embedding_retriever],
    weights=[0.3, 0.7]
)
```

### Multi-query retrieval

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(), llm=ChatOpenAI()
)
results = retriever.invoke("What is the main topic?")
```

### Contextual compression

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)
compressed_docs = compression_retriever.invoke("query")
```

### Parent document retriever

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

store = InMemoryStore()
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore, docstore=store,
    child_splitter=child_splitter, parent_splitter=parent_splitter
)
```

## Chunking strategies

- **Recursive character**: split on `["\n\n", "\n", " ", ""]` in order; `chunk_size=1000`, `chunk_overlap=200`.
- **Token-based**: `TokenTextSplitter(chunk_size=512, chunk_overlap=50)`.
- **Semantic**: `SemanticChunker(embeddings, breakpoint_threshold_type="percentile")`.
- **Markdown header**: `MarkdownHeaderTextSplitter` splitting on `#`, `##`, `###`.

## Retrieval optimization

### Metadata filtering

```python
results = vectorstore.similarity_search(
    "query", filter={"category": "technical"}, k=5
)
```

### Maximal marginal relevance

```python
results = vectorstore.max_marginal_relevance_search(
    "query", k=5,
    fetch_k=20,       # fetch 20, return top 5 diverse
    lambda_mult=0.5    # 0=max diversity, 1=max relevance
)
```

### Reranking with cross-encoder

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
candidates = vectorstore.similarity_search("query", k=20)
pairs = [[query, doc.page_content] for doc in candidates]
scores = reranker.predict(pairs)
reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:5]
```

## Prompt templates

```text
# Contextual
Use the following context to answer the question. If you cannot answer
based on the context, say "I don't have enough information."
Context: {context}
Question: {question}

# With citations
Answer based on the context below. Include citations using [1], [2], etc.

# With confidence
Answer the question using the context. Provide a confidence score (0-100%).
```

## Evaluation

Track accuracy (answer vs. expected), retrieval quality (relevant docs retrieved), and groundedness (answer supported by context) across a test set, averaging each metric.

## Best practices

1. **Chunk size**: balance context and specificity (500-1000 tokens).
2. **Overlap**: 10-20% to preserve context at boundaries.
3. **Metadata**: include source, page, timestamp for filtering and debugging.
4. **Hybrid search**: combine semantic and keyword search.
5. **Reranking**: improve top results with a cross-encoder.
6. **Citations**: always return source documents for transparency.
7. **Evaluation and monitoring**: continuously test retrieval quality and track metrics in production.

## Common issues

- **Poor retrieval**: check embedding quality, chunk size, query formulation.
- **Irrelevant results**: add metadata filtering, use hybrid search, rerank.
- **Missing information**: ensure documents are properly indexed.
- **Slow queries**: optimize vector store, use caching, reduce k.
- **Hallucinations**: improve grounding prompt, add a verification step.
