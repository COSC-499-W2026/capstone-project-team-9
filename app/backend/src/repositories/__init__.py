"""
Database Access Layer.

This package handles all direct communication with the database. 
Instead of writing SQL queries everywhere in the app, all database 
reads, writes, and updates are kept inside these repository classes 
to keep the rest of the code clean and organized.
"""

from .base_repo import BaseRepository
from .clue_repo import ClueRepository