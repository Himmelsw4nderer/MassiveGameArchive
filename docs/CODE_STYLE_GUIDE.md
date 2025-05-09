# Python Code Style Guide for MassiveGameArchive

## Core Principles

- **Readability**: Code should be easy to read and understand
- **Simplicity**: Avoid complexity, prefer simple solutions
- **Maintainability**: Code should be easy to maintain and modify

## Specific Rules

### 1. Brief Docstrings

Docstrings should be concise and to the point:

```python
def add_game(title: str, year: int) -> Game:
    """Add a new game to the database."""
    # Code here
```

No multi-line docstrings, except for complex functions where they're truly necessary.

### 2. Simple Functions

- Functions should do ONE thing
- Ideally no more than 20 lines per function
- Maximum cyclomatic complexity of 5

```python
# GOOD
def get_platform_games(platform_id: int) -> list[Game]:
    """Return all games for a specific platform."""
    return Game.objects.filter(platform_id=platform_id)

# AVOID
def get_platform_games_with_complex_logic(platform_id: int) -> list[Game]:
    """A function that's too complex."""
    # Too much logic in one function
    # ...many lines of code...
```

### 3. No Nesting

Keep nested code blocks to a minimum:

```python
# GOOD
def check_user_permission(user: User, action: str) -> bool:
    if not user.is_authenticated:
        return False
    
    if action not in ALLOWED_ACTIONS:
        return False
        
    return user.has_permission(action)

# AVOID
def check_user_permission_nested(user: User, action: str) -> bool:
    if user.is_authenticated:
        if action in ALLOWED_ACTIONS:
            if user.has_permission(action):
                return True
    return False
```

### 4. PEP 484 Type Annotations

All functions must have type annotations according to PEP 484:

```python
def search_games(query: str, limit: int = 20) -> list[Game]:
    """Search games based on the query string."""
    # Code here
```

Common types:
- `str`, `int`, `float`, `bool`, `None`
- `list[ElementType]`, `dict[KeyType, ValueType]`, `tuple[Type1, Type2]`
- `Optional[Type]` or `Type | None` for optional values
- Use `Any` only when absolutely necessary

### 5. Use English for All Code and Documentation

- All variable names, function names, class names, and comments must be in English
- All docstrings and documentation files must be written in English
- Commit messages should also be in English

### General Formatting

- Line length: Max. 88 characters
- Indentation: 4 spaces, no tabs
- Import order: Standard library, third-party packages, local imports

## Example

```python
from typing import Optional

from django.db import models

from massivegamearchive.models import Organizer


def get_game_by_id(game_id: int) -> Optional[dict]:
    """Return game information based on ID."""
    try:
        game = Game.objects.get(id=game_id)
        return {
            "title": game.title,
            "min_players": game.min_players,
            "max_players": game.max_players,
            "organizer": game.organizer.name,
        }
    except Game.DoesNotExist:
        return None
```

These style guidelines promote clean, readable, and maintainable code that aligns with the "Vibe Coding" approach.