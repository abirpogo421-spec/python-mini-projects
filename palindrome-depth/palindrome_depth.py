import sys
from collections import defaultdict

# Lychrel candidates like 196 never reach a palindrome, so cap the search
MAX_STEPS = 1000


def is_palindrome(n):
    s = str(n)
    return s == s[::-1]


def depth(n):
    """Number of reverse-and-add steps before n becomes a palindrome, or None."""
    for steps in range(MAX_STEPS + 1):
        if is_palindrome(n):
            return steps
        n += int(str(n)[::-1])
    return None


def main():
    limit = int(input("Classify numbers from 1 up to: "))
    if limit < 1:
        sys.exit("Error: enter a positive integer.")

    groups = defaultdict(list)
    for n in range(1, limit + 1):
        groups[depth(n)].append(n)

    for d in sorted(k for k in groups if k is not None):
        print(f"Depth {d}: {groups[d]}")
    if None in groups:
        print(f"No palindrome within {MAX_STEPS} steps: {groups[None]}")


if __name__ == "__main__":
    main()
