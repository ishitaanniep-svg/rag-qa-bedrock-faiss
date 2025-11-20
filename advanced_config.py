"""
Advanced Configuration Examples
Contains different configuration presets for various use cases
"""

# ============================================================================
# Configuration Presets for Different Use Cases
# ============================================================================

# 1. FAST RESPONSES (For quick answers with less accuracy)
FAST_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "retrieval_k": 1,
    "temperature": 0.5,
    "model_id": "anthropic.claude-3-haiku-20240307-v1:0"  # Faster, cheaper model
}

# 2. ACCURATE RESPONSES (For in-depth answers with high accuracy)
ACCURATE_CONFIG = {
    "chunk_size": 1500,
    "chunk_overlap": 300,
    "retrieval_k": 5,
    "temperature": 0.3,
    "model_id": "anthropic.claude-3-opus-20240229-v1:0"  # Most capable model
}

# 3. BALANCED RESPONSES (Good for most use cases - DEFAULT)
BALANCED_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "retrieval_k": 3,
    "temperature": 0.7,
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0"  # Recommended
}

# 4. CREATIVE RESPONSES (For brainstorming and ideation)
CREATIVE_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "retrieval_k": 5,
    "temperature": 0.9,
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0"
}

# 5. RESEARCH MODE (For detailed analysis with multiple sources)
RESEARCH_CONFIG = {
    "chunk_size": 2000,
    "chunk_overlap": 400,
    "retrieval_k": 5,
    "temperature": 0.2,
    "model_id": "anthropic.claude-3-opus-20240229-v1:0"
}

# 6. SUMMARY MODE (For quick document overviews)
SUMMARY_CONFIG = {
    "chunk_size": 800,
    "chunk_overlap": 100,
    "retrieval_k": 2,
    "temperature": 0.5,
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0"
}

# ============================================================================
# Custom Prompt Templates for Different Purposes
# ============================================================================

# 1. STANDARD Q&A PROMPT (Default)
STANDARD_PROMPT = """Use the following pieces of context to answer the user's question. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer:"""

# 2. DETAILED ANSWER PROMPT (More comprehensive)
DETAILED_PROMPT = """You are a helpful assistant. Use the provided context to answer the user's question comprehensively.
Provide detailed explanations with examples where relevant.
If the context doesn't contain enough information, acknowledge the limitation.

Context:
{context}

Question: {question}

Detailed Answer:"""

# 3. SUMMARY PROMPT (Concise answers)
SUMMARY_PROMPT = """You are a concise assistant. Use the following context to provide a brief, clear answer.
Keep your response to 2-3 sentences maximum.

Context:
{context}

Question: {question}

Brief Answer:"""

# 4. EXPERT ANALYSIS PROMPT
EXPERT_PROMPT = """You are an expert analyst. Using the provided context, analyze the user's question 
and provide professional insights. Include relevant details and nuances.

Context:
{context}

Question: {question}

Expert Analysis:"""

# 5. TEACHING PROMPT (Educational style)
TEACHING_PROMPT = """You are an educator. Use the context to explain the answer clearly, 
as if teaching someone new to the topic. Break down complex concepts into simple parts.

Context:
{context}

Question: {question}

Educational Explanation:"""

# 6. CRITICAL REVIEW PROMPT
CRITICAL_PROMPT = """You are a critical reviewer. Based on the context, analyze the question and provide:
1. The direct answer
2. Potential limitations or caveats
3. Alternative perspectives if applicable

Context:
{context}

Question: {question}

Critical Analysis:"""

# ============================================================================
# Model Configurations
# ============================================================================

MODELS = {
    "embedding": {
        "v1": "amazon.titan-embed-text-v1",
        "v2": "amazon.titan-embed-text-v2-v1",
        "cohere": "cohere.embed-english-v3"
    },
    "llm": {
        "claude_haiku": "anthropic.claude-3-haiku-20240307-v1:0",       # Fast, cheap
        "claude_sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",     # Balanced
        "claude_opus": "anthropic.claude-3-opus-20240229-v1:0",         # Most capable
        "llama_70b": "meta.llama2-70b-chat-v1",                         # Open source
        "mistral_large": "mistral.mistral-large-2402-v1:0"              # Open source
    }
}

# ============================================================================
# Processing Configurations
# ============================================================================

DOCUMENT_PROCESSING = {
    "minimal": {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "description": "For short documents or quick processing"
    },
    "standard": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "description": "Default for most documents"
    },
    "detailed": {
        "chunk_size": 1500,
        "chunk_overlap": 300,
        "description": "For comprehensive context preservation"
    },
    "deep": {
        "chunk_size": 2000,
        "chunk_overlap": 500,
        "description": "For complex documents requiring extensive context"
    }
}

# ============================================================================
# Retrieval Strategies
# ============================================================================

RETRIEVAL_STRATEGIES = {
    "precise": {
        "k": 1,
        "search_type": "similarity",
        "description": "Most relevant document only"
    },
    "focused": {
        "k": 3,
        "search_type": "similarity",
        "description": "Top 3 most relevant (recommended default)"
    },
    "comprehensive": {
        "k": 5,
        "search_type": "similarity",
        "description": "Multiple perspectives on the topic"
    },
    "exhaustive": {
        "k": 10,
        "search_type": "similarity",
        "description": "Comprehensive coverage (slower)"
    }
}

# ============================================================================
# Temperature Settings Explained
# ============================================================================

TEMPERATURE_GUIDE = {
    0.0: {
        "name": "Deterministic",
        "use": "Factual Q&A, legal documents, technical specs",
        "behavior": "Always the same answer"
    },
    0.3: {
        "name": "Very Conservative",
        "use": "Research, analysis, technical content",
        "behavior": "Mostly deterministic with minor variations"
    },
    0.5: {
        "name": "Conservative",
        "use": "Professional writing, news, summaries",
        "behavior": "Focused with some variation"
    },
    0.7: {
        "name": "Balanced",
        "use": "General purpose Q&A (RECOMMENDED)",
        "behavior": "Good mix of consistency and variation"
    },
    0.9: {
        "name": "Creative",
        "use": "Brainstorming, creative writing, ideation",
        "behavior": "More varied and creative"
    },
    1.0: {
        "name": "Maximum Randomness",
        "use": "Not recommended for RAG",
        "behavior": "Highly unpredictable"
    }
}

# ============================================================================
# Use Case Examples
# ============================================================================

USE_CASES = {
    "legal_research": {
        "config": "ACCURATE_CONFIG",
        "prompt": "DETAILED_PROMPT",
        "notes": "Use high retrieval_k for comprehensive coverage"
    },
    "technical_support": {
        "config": "FAST_CONFIG",
        "prompt": "STANDARD_PROMPT",
        "notes": "Users want quick answers"
    },
    "academic_research": {
        "config": "RESEARCH_CONFIG",
        "prompt": "EXPERT_PROMPT",
        "notes": "Require detailed analysis with sources"
    },
    "student_learning": {
        "config": "BALANCED_CONFIG",
        "prompt": "TEACHING_PROMPT",
        "notes": "Educational approach with explanations"
    },
    "executive_summary": {
        "config": "SUMMARY_CONFIG",
        "prompt": "SUMMARY_PROMPT",
        "notes": "Concise, actionable insights"
    },
    "content_creation": {
        "config": "CREATIVE_CONFIG",
        "prompt": "DETAILED_PROMPT",
        "notes": "Balance between creativity and accuracy"
    }
}

# ============================================================================
# AWS Cost Optimization
# ============================================================================

COST_OPTIMIZATION = {
    "low_cost": {
        "embedding_model": "amazon.titan-embed-text-v1",
        "llm_model": "anthropic.claude-3-haiku-20240307-v1:0",
        "retrieval_k": 1,
        "notes": "Minimal cost, basic functionality"
    },
    "balanced": {
        "embedding_model": "amazon.titan-embed-text-v1",
        "llm_model": "anthropic.claude-3-sonnet-20240229-v1:0",
        "retrieval_k": 3,
        "notes": "Good cost/performance balance (RECOMMENDED)"
    },
    "high_quality": {
        "embedding_model": "amazon.titan-embed-text-v2-v1",
        "llm_model": "anthropic.claude-3-opus-20240229-v1:0",
        "retrieval_k": 5,
        "notes": "Best quality, higher cost"
    }
}

# ============================================================================
# Implementation Examples
# ============================================================================

"""
Example 1: Using a configuration preset in your code

from advanced_config import FAST_CONFIG, STANDARD_PROMPT

def setup_fast_qa():
    chunk_size = FAST_CONFIG["chunk_size"]
    retrieval_k = FAST_CONFIG["retrieval_k"]
    temperature = FAST_CONFIG["temperature"]
    # ... rest of setup


Example 2: Selecting prompt based on use case

from advanced_config import USE_CASES

use_case = "legal_research"
config_name = USE_CASES[use_case]["config"]
prompt_template = USE_CASES[use_case]["prompt"]


Example 3: Dynamic configuration based on document size

def get_config_for_document_size(num_pages):
    if num_pages < 10:
        return "minimal"
    elif num_pages < 50:
        return "standard"
    elif num_pages < 200:
        return "detailed"
    else:
        return "deep"


Example 4: A/B Testing different configurations

configs_to_test = ["FAST_CONFIG", "BALANCED_CONFIG", "ACCURATE_CONFIG"]
for config in configs_to_test:
    setup_with_config(config)
    results = test_qa_quality()
    log_results(config, results)
"""

# ============================================================================
# Monitoring and Metrics
# ============================================================================

MONITORING = {
    "metrics_to_track": [
        "query_latency",
        "answer_quality_score",
        "token_usage",
        "api_cost",
        "cache_hit_rate",
        "retrieval_accuracy"
    ],
    "logging_intervals": {
        "development": "every_query",
        "staging": "every_100_queries",
        "production": "every_1000_queries"
    }
}

# ============================================================================
# Best Practices Based on Document Type
# ============================================================================

DOCUMENT_TYPE_CONFIGS = {
    "research_papers": {
        "chunk_size": 1500,
        "retrieval_k": 5,
        "temperature": 0.3,
        "reason": "Need context for citations and methodology"
    },
    "manuals_guides": {
        "chunk_size": 1000,
        "retrieval_k": 3,
        "temperature": 0.5,
        "reason": "Step-by-step clarity important"
    },
    "contracts_legal": {
        "chunk_size": 500,
        "retrieval_k": 3,
        "temperature": 0.0,
        "reason": "Precision critical, no ambiguity"
    },
    "news_articles": {
        "chunk_size": 800,
        "retrieval_k": 2,
        "temperature": 0.7,
        "reason": "Quick retrieval of key facts"
    },
    "technical_docs": {
        "chunk_size": 1000,
        "retrieval_k": 3,
        "temperature": 0.2,
        "reason": "Accuracy important"
    },
    "creative_writing": {
        "chunk_size": 1500,
        "retrieval_k": 4,
        "temperature": 0.8,
        "reason": "Context and creativity both matter"
    }
}

if __name__ == "__main__":
    print("Advanced Configuration Examples")
    print("=" * 60)
    print("\nConfiguration Presets:")
    for name, config in [
        ("FAST", FAST_CONFIG),
        ("BALANCED", BALANCED_CONFIG),
        ("ACCURATE", ACCURATE_CONFIG)
    ]:
        print(f"\n{name}:")
        for key, value in config.items():
            print(f"  {key}: {value}")
