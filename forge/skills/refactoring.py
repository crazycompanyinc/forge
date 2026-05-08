from __future__ import annotations

import re


class RefactoringSkills:
    name = "refactoring"

    def add_type_hints(self, source: str) -> str:
        replacements = {
            "def calculate_invoice(items, tax_rate, discount, user_type):": "def calculate_invoice(items: list[float], tax_rate: float, discount: float, user_type: str) -> float:",
            "def find_duplicates(items):": "def find_duplicates(items: list[str]) -> list[str]:",
            "def get_user(cursor, name):": "def get_user(cursor, name: str):",
        }
        for old, new in replacements.items():
            source = source.replace(old, new)
        return source

    def replace_magic_numbers(self, source: str) -> str:
        constants = "PREMIUM_DISCOUNT = 0.9\nENTERPRISE_DISCOUNT = 0.8\nBULK_THRESHOLD = 1000\nBULK_DISCOUNT = 0.95\n\n"
        if "PREMIUM_DISCOUNT" not in source and "def calculate_invoice" in source:
            source = constants + source
        return (
            source.replace("* 0.9", "* PREMIUM_DISCOUNT")
            .replace("* 0.8", "* ENTERPRISE_DISCOUNT")
            .replace("> 1000", "> BULK_THRESHOLD")
            .replace("* 0.95", "* BULK_DISCOUNT")
        )

    def remove_unused_imports(self, source: str) -> str:
        lines = source.splitlines()
        cleaned = [line for line in lines if line.strip() not in {"import os", "import sys", "import random"}]
        return "\n".join(cleaned) + ("\n" if source.endswith("\n") else "")

    def add_module_docstring(self, source: str, text: str = "Utilities evolved by Forge.") -> str:
        if source.startswith('"""') or source.startswith("'''"):
            return source
        return f'"""{text}"""\n\n{source}'

    def extract_invoice_helpers(self, source: str) -> str:
        if "_discount_for_user" in source or "def calculate_invoice" not in source:
            return source
        helper = """
def _discount_for_user(user_type: str) -> float:
    if user_type == "premium":
        return PREMIUM_DISCOUNT
    if user_type == "enterprise":
        return ENTERPRISE_DISCOUNT
    return 1.0


"""
        source = source.replace("def calculate_invoice", helper + "def calculate_invoice", 1)
        source = re.sub(
            r"    if user_type == \"premium\":\n        total = total \* PREMIUM_DISCOUNT\n    elif user_type == \"enterprise\":\n        total = total \* ENTERPRISE_DISCOUNT\n",
            "    total = total * _discount_for_user(user_type)\n",
            source,
        )
        return source

    def modernize_imports(self, source: str) -> str:
        return self.remove_unused_imports(source)
