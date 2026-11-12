from datetime import datetime

import pytest

from models import Game, Play, PlayClue
from repositories import PlayRepository, ClueRepository, GameRepository
from services.answer_service import CORRECT_MESSAGE, WRONG_MESSAGE, AnswerResult, AnswerService
from services.play_service import (
    ClueAlreadySolvedError,
    ClueNotInPlayError,
    GameNotFoundError,
    PlayNotFoundError,
    PlayService,
    ClueNotCurrentError
)

# FIXTURES & CONSTANTS --------------------------------------------------------

NUM_CLUES = 3
CLUE_IDS = [1, 2, 3]
PLAY_ID = 1
CLUE_ID = CLUE_IDS[0]  # the clue the submit_answer tests answer
CORRECT = AnswerResult(True, CORRECT_MESSAGE)
WRONG = AnswerResult(False, WRONG_MESSAGE)

@pytest.fixture
def mock_answer_service(mocker):
    """Mock AnswerService (OCR + location); every answer is correct by default."""
    service = mocker.create_autospec(AnswerService, instance=True)
    service.verify_answer.return_value = CORRECT
    return service

@pytest.fixture
def mock_clue_repo(mocker):
    """Mock ClueRepository that picks CLUE_IDS."""
    repo = mocker.create_autospec(ClueRepository, instance=True)
    repo.get_random_clue_ids.return_value = list(CLUE_IDS)
    return repo

@pytest.fixture
def mock_game_repo(mocker):
    """Mock GameRepository; finds no game by default (the `game` fixture overrides that)."""
    repo = mocker.create_autospec(GameRepository, instance=True)
    repo.get_game.return_value = None
    return repo

@pytest.fixture
def game(mock_game_repo):
    """A game that mock_game_repo returns."""
    game = Game(id=1, num_clues=NUM_CLUES, language_id=1, difficulty_id=1)
    mock_game_repo.get_game.return_value = game
    return game

@pytest.fixture
def play():
    return Play(id=PLAY_ID, game_id=1)

@pytest.fixture
def play_clue():
    """The unsolved play clue for CLUE_ID that submit_answer works on."""
    return PlayClue(play_id=PLAY_ID, clue_id=CLUE_ID, position=1, attempts=0, solved_at=None)

@pytest.fixture
def mock_play_repo(mocker, play, play_clue):
    """Mock PlayRepository set up for a normal submit: the play and clue exist, the clue is
    unsolved and is the current one. start_play saves the play it is given, with an id."""
    repo = mocker.create_autospec(PlayRepository, instance=True)

    def add_play_with_clues(new_play, clue_ids):
        new_play.id = PLAY_ID
        return new_play

    repo.add_play_with_clues.side_effect = add_play_with_clues
    repo.get_play.return_value = play
    repo.get_play_clue.return_value = play_clue
    repo.get_current_clue_id.return_value = CLUE_ID
    return repo

@pytest.fixture
def play_service(mock_answer_service, mock_play_repo, mock_game_repo, mock_clue_repo):
    return PlayService(mock_answer_service, mock_play_repo, mock_game_repo, mock_clue_repo)


def _submit(play_service):
    return play_service.submit_answer(PLAY_ID, CLUE_ID, b"img", 49.0, -119.0)


# START_PLAY TESTS --------------------------------------------------------

def test_start_play__saves_play_for_game(play_service, game, mock_play_repo, mock_game_repo):
    started = play_service.start_play(game.id)
    assert started.play.id == PLAY_ID
    assert started.play.game_id == game.id
    mock_play_repo.add_play_with_clues.assert_called_once()
    mock_game_repo.get_game.assert_called_once_with(game.id)


def test_start_play__returns_picked_clues(play_service, game):
    assert play_service.start_play(game.id).clue_ids == CLUE_IDS


def test_start_play__saves_clues_in_order(play_service, game, mock_play_repo, mock_clue_repo):
    reversed_ids = CLUE_IDS[::-1]
    mock_clue_repo.get_random_clue_ids.return_value = reversed_ids
    started = play_service.start_play(game.id)
    saved_play, saved_clue_ids = mock_play_repo.add_play_with_clues.call_args.args
    assert saved_clue_ids == reversed_ids
    assert started.clue_ids == reversed_ids


def test_start_play__asks_for_clues_matching_game_rules(play_service, game, mock_clue_repo):
    play_service.start_play(game.id)
    mock_clue_repo.get_random_clue_ids.assert_called_once_with(
        game.language_id, game.difficulty_id, game.num_clues
    )


def test_start_play__works_with_exact_clue_count(play_service, game):
    assert len(play_service.start_play(game.id).clue_ids) == NUM_CLUES


def test_start_play__records_given_user(play_service, game):
    assert play_service.start_play(game.id, user_id=7).play.user_id == 7


def test_start_play__user_defaults_to_none(play_service, game):
    assert play_service.start_play(game.id).play.user_id is None


def test_start_play__unknown_game_raises_and_saves_nothing(
    play_service, mock_game_repo, mock_clue_repo, mock_play_repo
):
    mock_game_repo.get_game.return_value = None
    with pytest.raises(GameNotFoundError):
        play_service.start_play(999)
    mock_game_repo.get_game.assert_called_once_with(999)
    mock_clue_repo.get_random_clue_ids.assert_not_called()
    mock_play_repo.add_play_with_clues.assert_not_called()


def test_start_play__too_few_clues_raises_and_saves_nothing(
    play_service, game, mock_clue_repo, mock_play_repo
):
    mock_clue_repo.get_random_clue_ids.return_value = CLUE_IDS[:-1]  # one short
    with pytest.raises(ValueError, match="Not enough clues"):
        play_service.start_play(game.id)
    mock_play_repo.add_play_with_clues.assert_not_called()


# GET_PLAY_STATE TESTS --------------------------------------------------------

def test_get_play_state__returns_play_current_clue_and_counts(play_service, play, mock_play_repo):
    mock_play_repo.get_current_clue_id.return_value = 2
    mock_play_repo.count_play_clues.return_value = NUM_CLUES
    mock_play_repo.count_solved_play_clues.return_value = 1
    state = play_service.get_play_state(PLAY_ID)
    assert state.play is play
    assert (state.current_clue_id, state.total_clues, state.solved_clues) == (2, NUM_CLUES, 1)
    mock_play_repo.get_play.assert_called_once_with(PLAY_ID)


def test_get_play_state__current_clue_none_when_all_solved(play_service, mock_play_repo):
    mock_play_repo.get_current_clue_id.return_value = None
    assert play_service.get_play_state(PLAY_ID).current_clue_id is None


def test_get_play_state__unknown_play_raises(play_service, mock_play_repo):
    mock_play_repo.get_play.return_value = None
    with pytest.raises(PlayNotFoundError):
        play_service.get_play_state(999)
    mock_play_repo.get_current_clue_id.assert_not_called()


# SUBMIT_ANSWER TESTS --------------------------------------------------------

def test_submit_answer__correct_records_correct_attempt(
    play_service, play_clue, mock_play_repo, mock_answer_service
):
    result = _submit(play_service)
    assert (result.correct, result.message, result.play_complete) == (True, CORRECT_MESSAGE, False)
    mock_answer_service.verify_answer.assert_called_once_with(CLUE_ID, b"img", 49.0, -119.0)
    mock_play_repo.record_attempt.assert_called_once_with(play_clue, True)


def test_submit_answer__wrong_records_wrong_attempt(
    play_service, play_clue, mock_play_repo, mock_answer_service
):
    mock_answer_service.verify_answer.return_value = WRONG
    result = _submit(play_service)
    assert (result.correct, result.message, result.play_complete) == (False, WRONG_MESSAGE, False)
    mock_play_repo.record_attempt.assert_called_once_with(play_clue, False)
    mock_play_repo.mark_play_complete.assert_not_called()


def test_submit_answer__reports_attempts_after_recording(play_service, play_clue, mock_play_repo):
    mock_play_repo.record_attempt.side_effect = lambda pc, correct: setattr(pc, "attempts", pc.attempts + 1)
    play_clue.attempts = 2  # two earlier attempts
    assert _submit(play_service).attempts == 3


def test_submit_answer__last_clue_completes_play(play_service, play, mock_play_repo):
    mock_play_repo.get_current_clue_id.side_effect = [CLUE_ID, None]  # before and after solving
    assert _submit(play_service).play_complete is True
    mock_play_repo.mark_play_complete.assert_called_once_with(play)


def test_submit_answer__non_last_clue_does_not_complete_play(play_service, mock_play_repo):
    mock_play_repo.get_current_clue_id.side_effect = [CLUE_ID, CLUE_IDS[1]]
    assert _submit(play_service).play_complete is False
    mock_play_repo.mark_play_complete.assert_not_called()


def test_submit_answer__wrong_on_last_clue_does_not_complete_play(
    play_service, mock_play_repo, mock_answer_service
):
    mock_answer_service.verify_answer.return_value = WRONG
    mock_play_repo.get_current_clue_id.side_effect = [CLUE_ID, None]  # would look complete if asked again
    assert _submit(play_service).play_complete is False
    mock_play_repo.mark_play_complete.assert_not_called()


def test_submit_answer__unknown_play_raises_without_checking(play_service, mock_play_repo, mock_answer_service):
    mock_play_repo.get_play.return_value = None
    with pytest.raises(PlayNotFoundError):
        play_service.submit_answer(999, CLUE_ID, b"img", 49.0, -119.0)
    mock_answer_service.verify_answer.assert_not_called()
    mock_play_repo.record_attempt.assert_not_called()


def test_submit_answer__clue_not_in_play_raises_without_checking(
    play_service, mock_play_repo, mock_answer_service
):
    mock_play_repo.get_play_clue.return_value = None
    with pytest.raises(ClueNotInPlayError):
        play_service.submit_answer(PLAY_ID, 999, b"img", 49.0, -119.0)
    mock_answer_service.verify_answer.assert_not_called()
    mock_play_repo.record_attempt.assert_not_called()


def test_submit_answer__already_solved_raises_and_records_nothing(
    play_service, play_clue, mock_play_repo, mock_answer_service
):
    play_clue.solved_at = datetime(2026, 11, 12)
    with pytest.raises(ClueAlreadySolvedError):
        _submit(play_service)
    mock_answer_service.verify_answer.assert_not_called()
    mock_play_repo.record_attempt.assert_not_called()


def test_submit_answer__unreadable_image_records_nothing(play_service, mock_play_repo, mock_answer_service):
    mock_answer_service.verify_answer.side_effect = ValueError("Not a readable image")
    with pytest.raises(ValueError):
        _submit(play_service)
    mock_play_repo.record_attempt.assert_not_called()


def test_submit_answer__non_current_clue_raises_and_records_nothing(
    play_service, mock_play_repo, mock_answer_service
):
    mock_play_repo.get_current_clue_id.return_value = CLUE_IDS[0] - 1  # some other clue is current
    with pytest.raises(ClueNotCurrentError):
        _submit(play_service)
    mock_answer_service.verify_answer.assert_not_called()
    mock_play_repo.record_attempt.assert_not_called()