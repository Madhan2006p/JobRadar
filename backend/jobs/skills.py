"""Week 2: find known skills inside job text, so every job gets clean skill tags."""

# Lowercase names we look for. Add more whenever you like.
KNOWN_SKILLS = {
    "python", "java", "go", "javascript", "typescript", "c", "c++", "rust", "sql",
    "django", "fastapi", "flask", "spring boot", "node.js", "react",
    "postgresql", "mysql", "mongodb", "redis", "celery", "kafka", "rabbitmq",
    "docker", "kubernetes", "aws", "gcp", "azure", "terraform", "linux", "git",
    "airflow", "spark", "pandas",
}

# Different spellings that mean the same skill.
ALIASES = {
    "postgres": "postgresql",
    "golang": "go",
    "nodejs": "node.js",
    "node": "node.js",
    "k8s": "kubernetes",
    "js": "javascript",
    "ts": "typescript",
    "drf": "django",
}


def normalize_skill(name: str) -> str:
    """Lowercase, strip spaces, and map aliases ("Postgres" -> "postgresql")."""
    raise NotImplementedError("TODO Week 2: normalize_skill")


def extract_skills(text: str) -> list[str]:
    """Return the sorted, unique KNOWN_SKILLS (and ALIASES) found in `text`.

    Careful with short names: "go" must not match "good", and "c" must not match
    every word. Use whole-word regex matching: re.search(rf"\\b{re.escape(s)}\\b", ...)
    "c++" and "node.js" contain symbols that \\b does not handle well. Test them.
    """
    raise NotImplementedError("TODO Week 2: extract_skills")
