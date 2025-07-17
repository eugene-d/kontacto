"""Fuzzy matching utilities for command suggestions."""

from typing import Optional
import shlex
from rapidfuzz import distance as rapidfuzz_distance, fuzz


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Distance between strings
    """
    return int(rapidfuzz_distance.Levenshtein.distance(s1.lower(), s2.lower()))


def find_best_match(query: str, candidates: list[str], threshold: float = 0.6) -> Optional[str]:
    """
    Find the best matching string from candidates.
    
    Args:
        query: Query string
        candidates: List of candidate strings
        threshold: Minimum similarity ratio (0.0 to 1.0)
        
    Returns:
        Best matching string or None if no good match
    """
    if not candidates:
        return None
    
    query_lower = query.lower()
    best_match = None
    best_ratio = 0.0
    
    for candidate in candidates:
        ratio = fuzz.ratio(query_lower, candidate.lower()) / 100.0
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = candidate
    
    return best_match


def find_suggestions(query: str, candidates: list[str], max_suggestions: int = 3) -> list[tuple[str, float]]:
    """
    Find multiple matching suggestions sorted by similarity.
    
    Args:
        query: Query string
        candidates: List of candidate strings
        max_suggestions: Maximum number of suggestions to return
        
    Returns:
        List of (suggestion, similarity_ratio) tuples
    """
    if not candidates:
        return []
    
    query_lower = query.lower()
    suggestions = []
    
    for candidate in candidates:
        ratio = fuzz.ratio(query_lower, candidate.lower()) / 100.0
        suggestions.append((candidate, ratio))
    
    # Sort by ratio (descending) and return top suggestions
    suggestions.sort(key=lambda x: x[1], reverse=True)
    return suggestions[:max_suggestions]


def is_partial_match(query: str, candidate: str) -> bool:
    """
    Check if query is a partial match (prefix) of candidate.
    
    Args:
        query: Query string
        candidate: Candidate string
        
    Returns:
        True if query is a prefix of candidate
    """
    return candidate.lower().startswith(query.lower())


def get_command_suggestions(input_text: str, available_commands: list[str]) -> list[str]:
    """
    Get command suggestions based on user input.
    
    Args:
        input_text: User input text
        available_commands: List of available commands
        
    Returns:
        List of suggested commands
    """
    # First, check for exact matches or prefix matches
    prefix_matches = [cmd for cmd in available_commands if is_partial_match(input_text, cmd)]
    if prefix_matches:
        return prefix_matches[:3]
    
    # If no prefix matches, use fuzzy matching
    fuzzy_suggestions = find_suggestions(input_text, available_commands, max_suggestions=3)
    
    # Filter out suggestions with very low similarity
    return [cmd for cmd, ratio in fuzzy_suggestions if ratio > 0.4]


def parse_command_input(input_text: str, command_aliases: dict) -> tuple[str, list[str]]:
    """
    Parse command input into command and arguments.
    
    Args:
        input_text: User input text
        command_aliases: Dictionary mapping aliases to canonical commands
        
    Returns:
        Tuple of (command, arguments)
    """
    try:
        # Use shlex to properly handle quoted arguments
        parts = shlex.split(input_text.strip())
    except ValueError:
        # If shlex fails (e.g., unmatched quotes), fall back to simple split
        parts = input_text.strip().split()
    
    if not parts:
        return "", []
    
    command = parts[0].lower()
    args = parts[1:]
    
    # Check if command is an alias
    if command in command_aliases:
        command = command_aliases[command]
    
    return command, args 