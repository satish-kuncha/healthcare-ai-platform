import asyncio
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.insurance_tools import search_knowledge_base
from agents.healthcare_agent import healthcare_agent
from models.context import PatientContext


TEST_SUITE = [
    {
        "question": "What happens if I arrive 20 minutes late to my appointment?",
        "reference": (
            "Patients arriving more than 15 minutes late may need to "
            "reschedule their appointment."
        ),
    },
    {
        "question": "Does Tier A insurance cover holistic acupuncture?",
        "reference": (
            "Tier A insurance does not cover holistic acupuncture."
        ),
    },
]


async def build_dataset():

    dataset = []

    for sample in TEST_SUITE:

        question = sample["question"]

        context = await search_knowledge_base(question)

        agent_result = await healthcare_agent.run(
            f"""
Use ONLY the supplied context.

Context:
{context}

Question:
{question}
""",
            deps=PatientContext(),
        )

        dataset.append(
            {
                "user_input": question,
                "retrieved_contexts": context.split("\n\n---\n\n"),
                "response": agent_result.output,
                "reference": sample["reference"],
            }
        )

    with open("evals/evaluation_dataset.jsonl", "w") as f:

        for row in dataset:
            f.write(json.dumps(row) + "\n")

    print(f"Saved {len(dataset)} samples.")


if __name__ == "__main__":
    asyncio.run(build_dataset())