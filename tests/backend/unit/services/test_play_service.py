import pytest
from sqlmodel import select

from models import Game, Play, PlayClue
from repositories import PlayRepository, ClueRepository, GameRepository # TODO in future: MOCK PlayRepository
from services.answer_service import CORRECT_MESSAGE, WRONG_MESSAGE, AnswerResult, AnswerService
from services.play_service import (
    ClueAlreadySolvedError,
    ClueNotInPlayError,
    GameNotFoundError,
    PlayNotFoundError,
    PlayService,
    ClueNotCurrentError
)
NUM_CLUES = 3
CORRECT = AnswerResult(True, CORRECT_MESSAGE)
WRONG = AnswerResult(False, WRONG_MESSAGE)


@pytest.fixture
def mock_game_repo(mocker):
    """Mock GameRepository; finds no game by default (the `game` fixture overrides that)."""
    repo = mocker.create_autospec(GameRepository, instance=True)
    repo.get_game.return_value = None
    return repo

@pytest.fixture
def mock_clue_repo(mocker, add_clues):
    """Mock ClueRepository that picks NUM_CLUES clues. The clues are also saved, because the
    real PlayRepository still inserts play clues that reference them."""
    repo = mocker.create_autospec(ClueRepository, instance=True)
    repo.get_random_clue_ids.return_value = add_clues(NUM_CLUES)
    return repo

@pytest.fixture
def game(session, mock_game_repo):
    """A game that mock_game_repo returns. It is also saved, because the real PlayRepository
    still inserts plays that reference it."""
    game = Game(num_clues=NUM_CLUES, language_id=1, difficulty_id=1)
    session.add(game)
    session.commit()
    mock_game_repo.get_game.return_value = game
    return game

@pytest.fixture
def mock_answer_service(mocker):
    """Mock AnswerService (OCR + location); every answer is correct by default."""
    service = mocker.create_autospec(AnswerService, instance=True)
    service.verify_answer.return_value = CORRECT
    return service

@pytest.fixture
def play_service(session, mock_answer_service, mock_game_repo, mock_clue_repo):
    return PlayService(
        mock_answer_service, PlayRepository(session), mock_game_repo, mock_clue_repo
    )


@pytest.fixture
def started(play_service, game):
    return play_service.start_play(game.id)


def _saved_plays(session):
    return session.exec(select(Play)).all()

def _submit(play_service, started, clue_index=0):
    return play_service.submit_answer(started.play.id, started.clue_ids[clue_index], b"img", 49.0, -119.0)


def _play_clue(session, started, clue_index=0):
    return session.get(PlayClue, (started.play.id, started.clue_ids[clue_index]))



def test_start_play_saves_play_for_the_game(play_service, session, game, mock_game_repo):
    started = play_service.start_play(game.id)
    assert started.play.id is not None
    assert started.play.game_id == game.id
    assert len(_saved_plays(session)) == 1
    mock_game_repo.get_game.assert_called_once_with(game.id)


def test_start_play_returns_the_clues_picked_by_the_clue_repo(play_service, game, mock_clue_repo):
    picked = mock_clue_repo.get_random_clue_ids.return_value
    assert play_service.start_play(game.id).clue_ids == picked


def test_start_play_saves_the_clues_in_the_returned_order(play_service, session, game, mock_clue_repo):
    reversed_ids = mock_clue_repo.get_random_clue_ids.return_value[::-1]  # not just ascending ids
    mock_clue_repo.get_random_clue_ids.return_value = reversed_ids
    started = play_service.start_play(game.id)
    rows = session.exec(
        select(PlayClue).where(PlayClue.play_id == started.play.id).order_by(PlayClue.position)
    ).all()
    assert started.clue_ids == reversed_ids
    assert [r.clue_id for r in rows] == reversed_ids
    assert [r.position for r in rows] == [1, 2, 3]


def test_start_play_asks_for_clues_matching_the_games_ruleset(play_service, game, mock_clue_repo):
    play_service.start_play(game.id)
    mock_clue_repo.get_random_clue_ids.assert_called_once_with(
        game.language_id, game.difficulty_id, game.num_clues
    )


def test_start_play_works_with_exactly_enough_clues(play_service, game):
    assert len(play_service.start_play(game.id).clue_ids) == NUM_CLUES


def test_start_play_records_user_when_given(play_service, game):
    assert play_service.start_play(game.id, user_id=7).play.user_id == 7


def test_start_play_user_is_none_by_default(play_service, game):
    assert play_service.start_play(game.id).play.user_id is None


def test_start_play_raises_when_game_does_not_exist_and_saves_nothing(
    play_service, session, mock_game_repo, mock_clue_repo
):
    mock_game_repo.get_game.return_value = None
    with pytest.raises(GameNotFoundError):
        play_service.start_play(999)
    mock_game_repo.get_game.assert_called_once_with(999)
    mock_clue_repo.get_random_clue_ids.assert_not_called()
    assert _saved_plays(session) == []


def test_start_play_raises_when_not_enough_clues_and_saves_nothing(
    play_service, session, game, mock_clue_repo
):
    picked = mock_clue_repo.get_random_clue_ids.return_value
    mock_clue_repo.get_random_clue_ids.return_value = picked[:-1]  # one short
    with pytest.raises(ValueError, match="Not enough clues"):
        play_service.start_play(game.id)
    assert _saved_plays(session) == []
    assert session.exec(select(PlayClue)).all() == []

def test_get_play_state_current_clue_is_first_when_nothing_solved(play_service, game):
    started = play_service.start_play(game.id)
    state = play_service.get_play_state(started.play.id)
    assert state.current_clue_id == started.clue_ids[0]


def test_get_play_state_current_clue_skips_solved_ones(play_service, game, solve_clue):
    started = play_service.start_play(game.id)
    solve_clue(started.play.id, started.clue_ids[0])
    assert play_service.get_play_state(started.play.id).current_clue_id == started.clue_ids[1]


def test_get_play_state_current_clue_is_lowest_unsolved_when_solved_out_of_order(
    play_service, game, solve_clue
):
    started = play_service.start_play(game.id)
    solve_clue(started.play.id, started.clue_ids[1])  # solve the 2nd clue first
    assert play_service.get_play_state(started.play.id).current_clue_id == started.clue_ids[0]
    solve_clue(started.play.id, started.clue_ids[0])
    assert play_service.get_play_state(started.play.id).current_clue_id == started.clue_ids[2]


def test_get_play_state_current_clue_is_none_when_all_solved(play_service, game, solve_clue):
    started = play_service.start_play(game.id)
    for clue_id in started.clue_ids:
        solve_clue(started.play.id, clue_id)
    assert play_service.get_play_state(started.play.id).current_clue_id is None


def test_get_play_state_raises_for_unknown_play(play_service):
    with pytest.raises(PlayNotFoundError):
        play_service.get_play_state(999)

def test_get_play_state_counts_total_and_solved(play_service, game, solve_clue):
    started = play_service.start_play(game.id)
    state = play_service.get_play_state(started.play.id)
    assert (state.total_clues, state.solved_clues) == (NUM_CLUES, 0)

    solve_clue(started.play.id, started.clue_ids[0])
    solve_clue(started.play.id, started.clue_ids[2])  # out of order on purpose
    state = play_service.get_play_state(started.play.id)
    assert (state.total_clues, state.solved_clues) == (NUM_CLUES, 2)

def test_submit_answer_correct_solves_the_clue(play_service, session, started, mock_answer_service):
    result = _submit(play_service, started)
    assert (result.correct, result.message) == (True, CORRECT_MESSAGE)
    assert (result.attempts, result.play_complete) == (1, False)
    assert _play_clue(session, started).solved_at is not None
    mock_answer_service.verify_answer.assert_called_once_with(started.clue_ids[0], b"img", 49.0, -119.0)


def test_submit_answer_wrong_counts_attempt_but_does_not_solve(play_service, session, started, mock_answer_service):
    mock_answer_service.verify_answer.return_value = WRONG
    result = _submit(play_service, started)
    assert (result.correct, result.attempts, result.play_complete) == (False, 1, False)
    assert _play_clue(session, started).solved_at is None


def test_submit_answer_attempts_accumulate(play_service, started, mock_answer_service):
    mock_answer_service.verify_answer.return_value = WRONG
    _submit(play_service, started)
    assert _submit(play_service, started).attempts == 2
    mock_answer_service.verify_answer.return_value = CORRECT
    assert _submit(play_service, started).attempts == 3


def test_submit_answer_solving_last_clue_completes_the_play(play_service, session, started):
    results = [_submit(play_service, started, i) for i in range(NUM_CLUES)]
    assert [r.play_complete for r in results] == [False, False, True]
    assert session.get(Play, started.play.id).completed_at is not None



def test_submit_answer_wrong_answer_on_last_clue_does_not_complete(play_service, session, started, mock_answer_service):
    _submit(play_service, started, 0)
    _submit(play_service, started, 1)
    mock_answer_service.verify_answer.return_value = WRONG
    assert _submit(play_service, started, 2).play_complete is False
    assert session.get(Play, started.play.id).completed_at is None


def test_submit_answer_unknown_play_raises_without_checking(play_service, mock_answer_service):
    with pytest.raises(PlayNotFoundError):
        play_service.submit_answer(999, 1, b"img", 49.0, -119.0)
    mock_answer_service.verify_answer.assert_not_called()


def test_submit_answer_clue_not_in_play_raises_without_checking(play_service, started, mock_answer_service):
    with pytest.raises(ClueNotInPlayError):
        play_service.submit_answer(started.play.id, 999, b"img", 49.0, -119.0)
    mock_answer_service.verify_answer.assert_not_called()


def test_submit_answer_already_solved_raises_and_keeps_attempts(play_service, session, started):
    _submit(play_service, started)
    with pytest.raises(ClueAlreadySolvedError):
        _submit(play_service, started)
    assert _play_clue(session, started).attempts == 1


def test_submit_answer_unreadable_image_records_nothing(play_service, session, started, mock_answer_service):
    mock_answer_service.verify_answer.side_effect = ValueError("Not a readable image")
    with pytest.raises(ValueError):
        _submit(play_service, started)
    assert _play_clue(session, started).attempts == 0

def test_submit_answer_for_a_later_clue_raises_and_records_nothing(play_service, session, started, mock_answer_service):
    with pytest.raises(ClueNotCurrentError):
        _submit(play_service, started, 1)  # clue 2 while clue 1 is current
    mock_answer_service.verify_answer.assert_not_called()
    assert _play_clue(session, started, 1).attempts == 0


def test_submit_answer_moves_on_to_the_next_clue_after_solving(play_service, started):
    _submit(play_service, started, 0)
    assert _submit(play_service, started, 1).correct is True