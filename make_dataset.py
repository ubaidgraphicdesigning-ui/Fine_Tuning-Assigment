#!/usr/bin/env python3
"""Create reproducible, stratified chat-style JSONL fine-tuning splits."""
import csv
import json
import random
import sys
from pathlib import Path

LABELS = {"positive", "negative", "neutral"}
SEED = 20261120


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python make_dataset.py <project_folder>")

    project = Path(sys.argv[1])
    if not project.exists():
        project = Path(__file__).parent / project

    system_path = project / "system_prompt.txt"
    csv_path = project / "examples.csv"
    if not system_path.is_file() or not csv_path.is_file():
        raise SystemExit("Project must contain system_prompt.txt and examples.csv")

    system_prompt = system_path.read_text(encoding="utf-8").strip()
    if not system_prompt:
        raise SystemExit("system_prompt.txt must not be empty")

    with csv_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["input", "output"]:
            raise SystemExit("CSV headers must be exactly: input,output")
        rows = [
            (row["input"].strip(), row["output"].strip())
            for row in reader
        ]

    if len(rows) < 100:
        raise SystemExit(f"Need at least 100 examples; found {len(rows)}")
    if any(not text or label not in LABELS for text, label in rows):
        raise SystemExit("Every input must be non-empty and every output a valid label")
    if len({text.casefold() for text, _ in rows}) != len(rows):
        raise SystemExit("Duplicate input examples found")

    groups = {label: [] for label in LABELS}
    for row in rows:
        groups[row[1]].append(row)

    counts = {label: len(group) for label, group in groups.items()}
    if min(counts.values()) == 0 or max(counts.values()) > 3 * min(counts.values()):
        raise SystemExit(f"Labels are not sufficiently balanced: {counts}")

    rng = random.Random(SEED)
    splits = {"train": [], "val": [], "test": []}
    for label, group in groups.items():
        rng.shuffle(group)
        train_end = int(len(group) * 0.70)
        val_end = train_end + int(len(group) * 0.15)
        splits["train"].extend(group[:train_end])
        splits["val"].extend(group[train_end:val_end])
        splits["test"].extend(group[val_end:])

    for split_name, group in splits.items():
        rng.shuffle(group)
        output_path = project / f"{split_name}.jsonl"
        with output_path.open("w", encoding="utf-8", newline="\n") as output:
            for text, label in group:
                record = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                        {"role": "assistant", "content": label},
                    ]
                }
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"{split_name}: {len(group)} examples")

    print("Dataset generation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
