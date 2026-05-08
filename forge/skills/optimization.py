from __future__ import annotations


class OptimizationSkills:
    name = "optimization"

    def optimize_duplicate_detection(self, source: str) -> str:
        old = """def find_duplicates(items):
    results = []
    for item in items:
        if items.count(item) > 1 and item not in results:
            results.append(item)
    return results
"""
        new = """def find_duplicates(items: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return sorted(duplicates)
"""
        return source.replace(old, new)
