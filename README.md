# Roman Urdu Sentiment Detection
### Fine-Tuning Dataset Assignment

A balanced dataset for a narrow text-classification task: identify the sentiment of a short Roman Urdu message.

![Task](https://img.shields.io/badge/task-text%20classification-2563eb)
![Dataset](https://img.shields.io/badge/dataset-150%20examples-16a34a)
![Labels](https://img.shields.io/badge/labels-3-7c3aed)
![Format](https://img.shields.io/badge/format-JSONL%20%2B%20CSV-0891b2)

## Project objective

Given one short message in Roman Urdu (sometimes mixed with English), classify its expressed sentiment into exactly one of these labels:

| Label | Meaning |
|---|---|
| `positive` | Satisfaction, happiness, praise, gratitude, approval, or encouragement |
| `negative` | Dissatisfaction, sadness, anger, complaint, criticism, disappointment, or frustration |
| `neutral` | Factual information, a plain question/request, or no clear sentiment |

The task is deliberately narrow and has a fixed answer format. It is not a general-purpose chatbot and does not require retrieval of external facts.

## Required model output

Return exactly one lowercase label. Do not include explanations, punctuation, or extra text.

```text
positive
```

The same instruction is supplied to every training example in [system_prompt.txt](system_prompt.txt).

## Dataset summary

**150 unique examples**, equally balanced across all three labels.

| Label | Examples |
|---|---:|
| Positive | 50 |
| Negative | 50 |
| Neutral | 50 |
| **Total** | **150** |

### Splits

| File | Examples | Split |
|---|---:|---:|
| `train.jsonl` | 105 | 70% |
| `val.jsonl` | 21 | 14% |
| `test.jsonl` | 24 | 16% |
| **Total** | **150** | **100%** |

Each JSONL line is a chat-style training record with `system`, `user`, and `assistant` messages. The assistant response is the target sentiment label.

## Repository structure

| File | Purpose |
|---|---|
| [examples.csv](examples.csv) | Source dataset with the two required columns: `input`, `output` |
| [system_prompt.txt](system_prompt.txt) | One consistent instruction used for every example |
| [train.jsonl](train.jsonl) | Training split |
| [val.jsonl](val.jsonl) | Validation split |
| [test.jsonl](test.jsonl) | Held-out test split |
| [edge_cases.txt](edge_cases.txt) | The 18 edge cases included in the dataset |
| [review_20_examples.txt](review_20_examples.txt) | Checklist for manually reviewing 20 examples |
| [make_dataset.py](make_dataset.py) | Generates JSONL splits from the CSV |
| [validate_dataset.py](validate_dataset.py) | Checks dataset structure and quality |

## Variety and quality checks

The examples include short and longer messages, Roman Urdu and some English, informal phrasing, typos/abbreviations, praise, complaints, neutral facts, and questions. Eighteen examples (12%) are edge cases, such as missing context, short replies, indirect sentiment, or off-topic factual statements.

The messages are synthetic and do not contain real personal records. AI assistance was used to draft examples. Programmatic checks were run for duplicate inputs, valid labels, class balance, and JSONL/chat structure.

**Manual review is still required:** read [review_20_examples.txt](review_20_examples.txt) and mark whether each label is correct. Fix any example you judge to be mislabeled before class. Do not mark the review as complete until you have checked it yourself.

## Build and validate

Python 3 is required. The helper scripts use only the Python standard library.

Run from the repository root:

```bash
python validate_dataset.py .
```

To regenerate the splits after editing the CSV or system prompt:

```bash
python make_dataset.py .
python validate_dataset.py .
```

The generator uses a fixed random seed and a stratified split. **Regenerating the dataset rewrites all three JSONL files.** Once the final `test.jsonl` has been made, keep it unchanged for the base-model vs fine-tuned-model evaluation in class.

If your instructor provided official versions of `make_dataset.py` or `validate_dataset.py`, prefer those versions.

## Three sample examples

| Input | Expected output |
|---|---|
| Bohat shukriya, aap ne meri problem solve kar di. | `positive` |
| App baar baar crash ho rahi hai, bohat tang aa gaya hoon. | `negative` |
| Kal class subah aath baje shuru hogi. | `neutral` |

## Assignment submission checklist

The assignment brief asks students to bring these four files:

- [ ] `train.jsonl`
- [ ] `val.jsonl`
- [ ] `test.jsonl`
- [ ] `README.md`

Keep `examples.csv` and `system_prompt.txt` in the repository as the source data and instruction used to create the splits.

---

**Project:** Roman Urdu Sentiment Detection  
**Purpose:** Fine-tuning dataset and base-vs-fine-tuned model comparison  
**Dataset size:** 150 examples
