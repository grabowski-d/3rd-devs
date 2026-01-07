"""Langfuse example."""

from .langfuse_service import LangfuseService


def main():
    print("\n" + "="*60)
    print("Langfuse Tracing Example")
    print("="*60 + "\n")

    langfuse = LangfuseService()
    print("Langfuse service initialized.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
