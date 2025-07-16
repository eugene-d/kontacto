"""Repositories package for Personal Assistant."""

from .base_repository import BaseRepository
from .contact_repository import ContactRepository
from .note_repository import NoteRepository

__all__ = ['BaseRepository', 'ContactRepository', 'NoteRepository']
