"""
Business Logic Layer (Services).

This package handles the brains and rules of the application. 
Services take clean data from the API endpoints, process it (like 
hashing passwords or checking business rules), and coordinate with 
the repository layer to save the results. No HTTP or raw SQL goes here.
"""

# NOTE: if a service B depends on service A, then B must be imported AFTER A in this file

from .game_options_service import GameOptionsService
from .game_service import GameService
from .location_service import LocationService
from .play_service import PlayService
