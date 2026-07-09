"""
prompts.py - Reusable, versioned prompt templates.

Keeping templates in one module (instead of inlining strings across the
codebase) is what makes AI-generated output consistent: every feature pulls
from the same system instructions and formatting rules.
"""

# Shared system instruction: sets tone/format rules for every feature so
# outputs stay consistent regardless of which command is used.
BASE_SYSTEM_INSTRUCTION = """You are AgentFlow, an AI software engineering assistant.
You help engineers turn requirements into clear implementation plans, generate
technical documentation, and review code for bugs and improvements.

Rules:
- Be precise, structured, and use Markdown formatting (headings, bullet lists, code blocks).
- Never invent APIs, libraries, or facts about the codebase you weren't given.
- If information is missing, state your assumptions explicitly in an "Assumptions" section.
- Keep a professional, engineering-documentation tone.
"""


PLAN_TEMPLATE = """Convert the following software requirement(s) into a structured
implementation plan.

Requirement(s):
---
{requirement}
---

Produce the plan with these sections, in Markdown:
1. **Summary** - one paragraph restating the goal.
2. **Assumptions** - anything you had to infer.
3. **Architecture / Components** - modules or services involved.
4. **Step-by-Step Implementation Plan** - numbered, actionable steps.
5. **Data Model / Interfaces** (if applicable).
6. **Testing Strategy** - how to verify correctness.
7. **Risks & Edge Cases**.
"""


DOC_TEMPLATE = """Generate technical documentation for the following code.

Code:
```{language}
{code}
```

Produce documentation with these sections in Markdown:
1. **Overview** - what this code does and why it likely exists.
2. **Public API** - functions/classes/methods, their parameters, return values, and exceptions.
3. **Usage Example** - a minimal example of calling this code.
4. **Dependencies** - external libraries/modules it relies on.
5. **Notes / Caveats** - non-obvious behavior, side effects, or limitations.
"""


CODE_REVIEW_TEMPLATE = """Perform an automated code review on the following code.

Code:
```{language}
{code}
```

Return your review in Markdown with these sections:
1. **Overall Assessment** - one short paragraph.
2. **Bugs / Correctness Issues** - concrete issues, with line references where possible.
3. **Security Concerns** - if any.
4. **Style & Maintainability** - naming, structure, readability.
5. **Performance Notes** - if relevant.
6. **Suggested Fixes** - concrete code snippets for the most important issues.
Rate severity of each issue as [Critical] / [Moderate] / [Minor].
"""


BUG_DETECTION_TEMPLATE = """Analyze the following code specifically for bugs
(logic errors, off-by-one errors, null/None handling, incorrect conditionals,
resource leaks, race conditions, exception handling gaps).

Code:
```{language}
{code}
```

For each bug found, output in Markdown:
- **Location**: (function/line)
- **Bug**: description
- **Why it's a problem**: brief explanation
- **Fix**: corrected code snippet

If no bugs are found, state that clearly and mention what you checked for.
"""


IMPROVEMENT_TEMPLATE = """Suggest concrete improvements to the following code
(readability, performance, modularity, error handling, testability).

Code:
```{language}
{code}
```

Output in Markdown:
1. **Quick Wins** - small, safe changes.
2. **Structural Improvements** - refactoring suggestions with rationale.
3. **Refactored Example** - a revised version of the most important part of the code.
"""


def build_prompt(template: str, **kwargs) -> str:
    """Fill a template with provided values. Centralizing this avoids
    scattered .format() calls and keeps template variables consistent."""
    return template.format(**kwargs)
