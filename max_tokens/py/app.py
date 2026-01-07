"""Token counter example."""

from .token_counter import TokenCounter


def main():
    print("\n" + "="*60)
    print("Token Counter Example")
    print("="*60 + "\n")

    text = "This is a sample text for token counting."
    count = TokenCounter.count(text)
    print(f"Text: {text}")
    print(f"Tokens: {count}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
