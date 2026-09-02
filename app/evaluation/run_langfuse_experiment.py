from langfuse import Evaluation

from app.observability.langfuse_client import langfuse
from app.rag_service import answer_question
import json

from langfuse.openai import OpenAI


DATASET_NAME = "employee-handbook-v1"
judge_client = OpenAI()

def run_rag(*, item, **kwargs):
    question = item.input["question"]

    result = answer_question(question)

    return {
        "answer": result["answer"],
        "sources": [
            {
                "filename": source.filename,
                "page_number": source.page_number,
                "content": source.content,
            }
            for source in result["sources"]
        ],
    }


def expected_fact_evaluator(
    *,
    input,
    output,
    expected_output,
    metadata,
    **kwargs,
):
    expected_answer = expected_output["answer"]
    actual_answer = output["answer"]

    expected_lower = expected_answer.lower()
    actual_lower = actual_answer.lower()

    category = metadata.get("category")

    if category == "annual_leave":
        passed = "30" in actual_lower

    elif category == "remote_work":
        passed = (
            "three" in actual_lower
            or "3" in actual_lower
        )

    elif category == "learning_and_development":
        passed = (
            "1,500" in actual_lower
            or "1500" in actual_lower
        )

    elif category == "expenses":
        passed = "30 days" in actual_lower

    elif category == "information_security":
        passed = (
            "approved" in actual_lower
            and "system" in actual_lower
        )

    elif category == "unknown":
        passed = (
            "don't know" in actual_lower
            or "do not know" in actual_lower
            or "couldn't find" in actual_lower
        )

    else:
        passed = expected_lower in actual_lower

    return Evaluation(
        name="expected_fact",
        value=1.0 if passed else 0.0,
        comment=(
            "Expected fact found in generated answer."
            if passed
            else "Expected fact was not found in generated answer."
        ),
    )

def correctness_evaluator(
    *,
    input,
    output,
    expected_output,
    **kwargs,
):
    question = input["question"]
    actual_answer = output["answer"]
    expected_answer = expected_output["answer"]

    judge_prompt = f"""
You are evaluating the correctness of an answer produced by a RAG system.

Question:
{question}

Expected answer:
{expected_answer}

Actual answer:
{actual_answer}

Determine whether the actual answer correctly answers the question.

The wording does not need to exactly match the expected answer.

Return ONLY valid JSON in this format:

{{
  "score": 1,
  "reason": "Short explanation"
}}

Use:
1 = correct
0 = incorrect

Do not include markdown or additional text.
"""

    response = judge_client.responses.create(
        model="gpt-4.1-mini",
        input=judge_prompt,
    )

    result = json.loads(response.output_text)

    return Evaluation(
        name="correctness",
        value=float(result["score"]),
        comment=result["reason"],
    )

def groundedness_evaluator(
    *,
    input,
    output,
    **kwargs,
):
    actual_answer = output["answer"]
    sources = output["sources"]

    context = "\n\n".join(
        source["content"]
        for source in sources
    )

    judge_prompt = f"""
You are evaluating the groundedness of an answer produced by a RAG system.

Retrieved context:
{context}

Generated answer:
{actual_answer}

Determine whether every factual claim in the generated answer is supported
by the retrieved context.

Return ONLY valid JSON in this format:

{{
  "score": 1,
  "reason": "Short explanation"
}}

Use:
1 = fully grounded
0 = contains unsupported factual claims

Do not judge whether the answer matches an expected answer.
Judge only whether the generated answer is supported by the provided context.

Do not include markdown or additional text.
"""

    response = judge_client.responses.create(
        model="gpt-4.1-mini",
        input=judge_prompt,
    )

    result = json.loads(response.output_text)

    return Evaluation(
        name="groundedness",
        value=float(result["score"]),
        comment=result["reason"],
    )

def main():
    dataset = langfuse.get_dataset(DATASET_NAME)

    result = dataset.run_experiment(
        name="rag-hallucination-test-v1",
        description=(
            "Baseline employee handbook RAG experiment "
            "with deterministic expected-fact evaluation."
        ),
        task=run_rag,
        evaluators=[
            expected_fact_evaluator,
            correctness_evaluator,
            groundedness_evaluator,
        ],
    )

    print(result.format())



if __name__ == "__main__":
    main()