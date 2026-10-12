"""RAGAS 0.1 adapter with explicit evaluator model provenance."""
from __future__ import annotations

import math
import os
from types import SimpleNamespace


def evaluate_ragas(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> dict:
    lengths = {len(questions), len(answers), len(contexts), len(ground_truths)}
    if len(lengths) != 1:
        raise ValueError("RAGAS input lists must have the same length")
    if not questions:
        raise ValueError("RAGAS input cannot be empty")

    from datasets import Dataset
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas import evaluate
    from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

    llm_model = os.getenv("RAGAS_LLM_MODEL", "gpt-4o-mini")
    embedding_model = os.getenv("RAGAS_EMBEDDING_MODEL", "text-embedding-3-small")
    llm = ChatOpenAI(model=llm_model, temperature=0)
    embeddings = OpenAIEmbeddings(model=embedding_model)
    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=llm,
        embeddings=embeddings,
        raise_exceptions=True,
    )
    frame = result.to_pandas()
    rows = []
    for record in frame.to_dict(orient="records"):
        values = {
            name: float(record[name])
            for name in ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
        }
        if any(not math.isfinite(value) or not 0 <= value <= 1 for value in values.values()):
            raise ValueError(f"RAGAS returned invalid metric values: {values}")
        rows.append(SimpleNamespace(**values))
    return {
        "per_question": rows,
        "metadata": {"evaluator_models": [llm_model, embedding_model]},
    }
