"""Max tokens calculator."""
class MaxTokensCalculator:
    DEFAULT_MAX = 4096
    CONTEXT_OVERHEAD = 256
    def calculate(self, prompt_tokens: int) -> int:
        return max(100, self.DEFAULT_MAX - prompt_tokens - self.CONTEXT_OVERHEAD)
