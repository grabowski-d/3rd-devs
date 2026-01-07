"""Hybrid search example."""

from .text_service import TextService


def main():
    print("\n" + "="*60)
    print("Hybrid Search Example")
    print("="*60 + "\n")

    text_service = TextService()
    tokens = text_service.tokenize("Hello World")
    print(f"Tokens: {tokens}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
