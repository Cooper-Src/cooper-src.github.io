---
title: TinyTalk
tag: Python · PyTorch · Machine Learning
summary: A Python project that implements, trains and runs a small decoder-only transformer language model from scratch.
tags: python pytorch machine-learning systems
repo:
---

TinyTalk is a Python language-model project built around a custom decoder-only Transformer implementation.

## Model architecture

The current model configuration defines:

- 2,000-token vocabulary
- 256-token context length
- 512-dimensional token embeddings
- 8 Transformer layers
- 8 attention heads per layer
- 1,536-dimensional feed-forward layers
- Rotary positional embeddings (RoPE)
- RMSNorm
- Weight tying between token embeddings and the language-model head

The attention implementation applies a causal upper-triangular mask, so each token can only attend to the current position and earlier positions.

## Training

Training is implemented with PyTorch. The trainer:

- Uses CUDA automatically when PyTorch reports a CUDA device, otherwise CPU
- Builds the dataset from `data/train.txt`
- Trains with cross-entropy next-token prediction
- Uses gradient clipping with a maximum norm of `1.0`
- Uses AdamW-style optimizer and scheduler helpers from the project
- Saves checkpoints during training and can resume from the latest checkpoint

The repository currently contains a `checkpoints/latest.pt` checkpoint and tokenizer files generated for TinyTalk.

## Tokenizer

TinyTalk uses SentencePiece with a BPE tokenizer. The current tokenizer configuration uses a vocabulary size of 2,000 tokens and reserves IDs for padding, unknown tokens, beginning-of-sequence and end-of-sequence markers.

## Generation

`tinytalk/generate.py` implements autoregressive generation. It supports:

- Maximum new-token limits
- Temperature sampling
- Top-k sampling
- Context-window truncation to the configured 256-token limit
- Early stopping on the tokenizer's end-of-sequence token

## Interactive chat

The repository includes `chat.py`, which loads the model and tokenizer, restores a checkpoint, and provides a terminal chat loop. Prompts are passed into the generation function and the generated response is printed back to the terminal.

## Dataset pipeline

The dataset pipeline is split into separate stages. `build_dataset.py` combines processed text files from `data/processed` into `data/train.txt`, while `train_tokenizer.py` trains and verifies the SentencePiece tokenizer against that corpus.

## Project structure

```text
config/                Model, tokenizer and training configuration
tinytalk/              Model, data, generation and training code
tinytalk/layers/       Transformer building blocks
tinytalk/training/     Checkpoint, optimizer, scheduler and loss helpers
tokenizer/             SentencePiece tokenizer files and wrapper
tests/                 Dataset, forward-pass and training-step tests
chat.py                Interactive terminal chat
train.py               Training entry point
build_dataset.py       Training-corpus builder
train_tokenizer.py     Tokenizer training script
```

## Source

The portfolio page describes the uploaded project source. A public repository link can be added here when the TinyTalk repository URL is available.
