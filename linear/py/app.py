"""Linear algebra example."""

from .linear_service import LinearService


def main():
    print("\n" + "="*60)
    print("Linear Algebra Example")
    print("="*60 + "\n")

    a = [1, 2, 3]
    b = [4, 5, 6]

    dot = LinearService.dot_product(a, b)
    sim = LinearService.cosine_similarity(a, b)

    print(f"Dot product: {dot}")
    print(f"Cosine similarity: {sim:.4f}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
