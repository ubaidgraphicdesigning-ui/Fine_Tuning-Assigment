#!/usr/bin/env python3
"""Validate source CSV and chat-style JSONL fine-tuning splits."""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

LABELS = {"positive", "negative", "neutral"}
EXPECTED_ROLES = ["system", "user", "assistant"]


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python validate_dataset.py <project_folder>")

    project = Path(sys.argv[1])
    if not project.exists():
        project = Path(__file__).parent / project

    csv_path = project / "examples.csv"
    errors = []
    if not csv_path.is_file():
        raise SystemExit("ERROR: examples.csv is missing")

    with csv_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["input", "output"]:
            raise SystemExit("ERROR: CSV headers must be exactly input,output")
        rows = list(reader)

    inputs = [row["input"].strip() for row in rows]
    outputs = [row["output"].strip() for row in rows]

    if len(rows) < 100:
        errors.append(f"Only {len(rows)} examples; minimum is 100")
    if any(not text for text in inputs):
        errors.append("One or more empty inputs")
    if any(label not in LABELS for label in outputs):
        errors.append("Invalid output label found")
    if len({text.casefold() for text in inputs}) != len(inputs):
        errors.append("Duplicate inputs found")

    source_counts = Counter(outputs)
    if len(source_counts) != 3 or min(source_counts.values(), default=0) == 0:
        errors.append(f"Missing one or more labels: {dict(source_counts)}")
    elif max(source_counts.values()) > 3 * min(source_counts.values()):
        errors.append(f"Labels are not balanced: {dict(source_counts)}")

    seen_inputs = set()
    split_counts = {}
    for split_name in ("train", "val", "test"):
        path = project / f"{split_name}.jsonl"
        if not path.is_file():
            errors.append(f"Missing {path.name}")
            continue

        count = 0
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                if not line.strip():
                    errors.append(f"{path.name}:{line_number}: blank line")
                    continue
                try:
                    record = json.loads(line)
                    messages = record["messages"]
                    if [message["role"] for message in messages] != EXPECTED_ROLES:
                        raise ValueError("expected system, user, assistant roles")
                    message_text = [message["content"] for message in messages]
                    if not all(isinstance(value, str) for value in message_text):
                        raise ValueError("message content must be text")
                    if not message_text[1]:
                        raise ValueError("user input must not be empty")
                    if message_text[2] not in LABELS:
                        raise ValueError("assistant output is not a valid label")
                    if message_text[1].casefold() in seen_inputs:
                        raise ValueError("duplicate input across dataset splits")
                    seen_inputs.add(message_text[1].casefold())
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                    errors.append(f"{path.name}:{line_number}: invalid record ({exc})")
                count += 1
        split_counts[split_name] = count

    if sum(split_counts.values()) != len(rows):
        errors.append(
            f"Split total ({sum(split_counts.values())}) does not match CSV total ({len(rows)})"
        )
    if len(seen_inputs) != len(rows):
        errors.append(
            f"Unique valid split inputs ({len(seen_inputs)}) do not match CSV rows ({len(rows)})"
        )

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print("VALIDATION PASSED")
    print(f"Total CSV examples: {len(rows)}")
    print("Label counts:", dict(source_counts))
    print("Split counts:", split_counts)
    print("No duplicate inputs, invalid labels, or malformed JSONL records found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
