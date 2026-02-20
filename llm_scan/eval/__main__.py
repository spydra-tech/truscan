"""Allow running the eval runner as python -m llm_scan.eval."""

from .runner import main

if __name__ == "__main__":
    raise SystemExit(main())
