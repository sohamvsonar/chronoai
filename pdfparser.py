#!/usr/bin/env python3
import os
import argparse
import openai
from PyPDF2 import PdfReader
from chronoai import ai_interaction

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Read all pages from the PDF and concatenate their text.
    """
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text

def chunk_text(text: str, max_words: int = 2000) -> list[str]:
    """
    Split the input text into chunks of up to `max_words` words each.
    """
    words = text.split()
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)]

def summarize_text(
    text: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.3
) -> str:
    """
    Send one chunk of text to the ChatCompletion API and return its summary.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user",   "content": f"Please provide a concise summary of the following text:\n\n{text}"}
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()

def main(pdf_path: str):
    # 1) Extract
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("No text found in PDF.")
        return

    # 2) Chunk
    chunks = chunk_text(text)
    print(f"Extracted {len(chunks)} text chunks; summarizing each...")

    # 3) Summarize each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks, start=1):
        print(f" Summarizing chunk {i}/{len(chunks)}...")
        s = summarize_text(chunk)
        chunk_summaries.append(s)

    # 4) Combine and refine
    combined = "\n\n".join(chunk_summaries)
    print("Combining chunk summaries into final summary...")
    final_summary = summarize_text(
        combined,
        model="gpt-3.5-turbo",
        temperature=0.3
    )

    # Output
    print("\n\n===== Final PDF Summary =====\n")
    print(final_summary)
    ai_interaction(final_summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract and summarize a PDF via the OpenAI API"
    )
    parser.add_argument(
        "pdf_path",
        help="Path to your PDF file"
    )
    args = parser.parse_args()
    main(args.pdf_path)
