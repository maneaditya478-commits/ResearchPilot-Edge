"""
Unit tests for local AI inference engines.
"""

from app.inference.fallback_backend import DeterministicLocalInferenceEngine
from app.inference.base import InferenceResult

def test_fallback_inference_generation():
    engine = DeterministicLocalInferenceEngine()
    prompt = "What is the primary evaluation dataset?"
    context = "We evaluate the pipeline on HotpotQA and ResearchPilot-Bench-5k containing 5,000 academic papers."

    result = engine.generate(prompt=prompt, context=context)

    assert isinstance(result, InferenceResult)
    assert len(result.text) > 0
    assert result.latency_ms > 0
    assert result.tokens_generated > 0
    assert "HotpotQA" in result.text or "ResearchPilot" in result.text

def test_fallback_summarization():
    engine = DeterministicLocalInferenceEngine()
    doc_text = """
    ABSTRACT
    This paper introduces Snapdragon NPU acceleration.
    
    METHODOLOGY
    We use QNN INT4 quantization on Hexagon tensor cores.
    
    RESULTS
    Achieves 38.6 tokens/sec and 4.2x energy improvement.
    """
    summary = engine.summarize(document_text=doc_text, document_name="test.pdf")

    assert summary["document"] == "test.pdf"
    assert "abstract" in summary
    assert "methodology" in summary
    assert "results" in summary

def test_fallback_comparison():
    engine = DeterministicLocalInferenceEngine()
    payload = [
        {"document": "Paper A.pdf", "text": "Snapdragon Hexagon NPU achieves 38 tokens/sec."},
        {"document": "Paper B.pdf", "text": "DirectML on Adreno GPU achieves 24 tokens/sec."}
    ]
    matrix = engine.compare(payload)

    assert len(matrix) >= 4
    first_row = matrix[0]
    assert "Category" in first_row
    assert "Paper A.pdf" in first_row
    assert "Paper B.pdf" in first_row
