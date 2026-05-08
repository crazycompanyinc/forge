from __future__ import annotations


class SecuritySkills:
    name = "security"

    def patch_sql_injection(self, source: str) -> str:
        unsafe = 'cursor.execute("SELECT * FROM users WHERE name = \'%s\'" % name)'
        safe = 'cursor.execute("SELECT * FROM users WHERE name = ?", (name,))'
        return source.replace(unsafe, safe)
