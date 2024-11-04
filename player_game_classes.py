"""CSC111 Winter 2023 Course Project Phase 2: Predictive Steam Game Reccomender

Summary
===============================

This module contains a collection of Python classes and functions that are used to
represent a SteamGraph.

Copyright and Usage Information
===============================

This file is provided solely for the private use of TA's and other University of Toronto
St. George faculty. All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

This file is Copyright (c) 2023 Isabella Enriquez, Laura Zhan, and Olivia Wong.
"""
from __future__ import annotations
import random
from python_ta.contracts import check_contracts


# @check_contracts
class Game:
    """A node that represents a Steam video game in a SteamGraph.
    Instance Attributes:
    - game_name:
        The title of the game.
    - game_id:
        A unique identifier for the game.
    - game_tags:
        A set of the game tags for the game.
    - reviewed_by:
        A mapping containing players that have reviewed the game in the SteamGraph.
        Each key in this mapping is the id of the player, and the corresponding value is a tuple of the Player object
        and a bool representing whether a player liked the game or not.
    Representation Invariants:
        - all(self.reviewed_by[id][0].games_reviewed[self.game_id][0] is self for id in self.reviewed_by)
    """
    game_name: str
    game_id: str
    game_tags: list[str]
    reviewed_by: dict[str, tuple[Player, bool]]

    def __init__(self, name: str, self_id: str, tags: list[str]) -> None:
        """Initialize a Game object with no reviews.
        Preconditions:
        - self._id not in self.reviewed_by
        """
        self.game_name = name
        self.game_id = self_id
        self.game_tags = tags
        self.reviewed_by = {}


# @check_contracts
class Player:
    """A node that represents a Steam user in a SteamGraph.
    Instance Attributes:
    - player_id:
        A unique identifier for the player.
    - games_reviewed:
        A mapping containing the reviews the player has created for games in the SteamGraph.
        Each key in this mapping is the id of the reviewed game, and the corresponding value is a tuple of the Game
        object and a bool representing whether a player liked the game or not.
    Representation Invariants:
        - all(self.games_reviewed[id][0].reviewed_by[self.player_id][0] is self for id in self.games_reviewed)
    """
    player_id: str
    games_reviewed: dict[str, tuple[Game, bool]]

    def __init__(self, self_id: str) -> None:
        """Initialize a Player object with no reviews
        Preconditions:
        - self.player_id not in self.games_reviewed
        """
        self.player_id = self_id
        self.games_reviewed = {}


# @check_contracts
class SteamGraph:
    """A graph that contains players and games.
    Instance Attributes:
    - players:
        A mapping of player ids and Player objects in this graph.
    - games:
        A mapping of game ids and Game objects in this graph.
    """
    players: dict[str, Player]
    games: dict[str, Game]

    def __init__(self, all_games: list[Game]) -> None:
        """Initialize a SteamGraph with the game objects."""
        self.games = {}
        self.players = {}
        for game in all_games:
            self.games[game.game_id] = game

    def add_player(self, player: Player) -> None:
        """Add a player to this SteamGraph."""
        self.players[player.player_id] = player

    def add_review(self, player: Player, game_id: str, review: bool) -> None:
        """Add a review for this player, and update the corresponding Game object's reviewed_by attribute.

        Preconditions:
        - player.id in self.players
        - game_id in self.games
        """
        player.games_reviewed[game_id] = (self.games[game_id], review)
        self.games[game_id].reviewed_by[player.player_id] = (player, review)

    ####################################################################################################################
    # Main Algorithm Caller & its helper functions
    ####################################################################################################################
    def get_three_games(self, user_games: list[Game], liked_genres: list[str], algorithm_type: str) -> list[Game]:
        """ Our main calculation function.

        Preconditions:
        - algorithm_type in {'players', 'genre', 'players_genre'}
        - len(user_games) == 3
        - len(liked_genres) == 3

        >>> game_ids = [id for id in graph.games]
        >>> games_with_reviews = [graph.games[id] for id in game_ids if graph.games[id].reviewed_by != {}]
        >>> graph.get_three_games([games_with_reviews[0], games_with_reviews[1], games_with_reviews[2]], \
        ['Indie', 'Action', 'Adventure'], 'players_genre')
        """
        if algorithm_type == 'players':
            return self.three_games_other_players(user_games)
        elif algorithm_type == 'genre':
            return self.three_games_genre(liked_genres)
        else:
            return self.three_games_players_and_genre(user_games, liked_genres)

    def three_games_other_players(self, user_games: list[Game]) -> list[Game]:
        """Return three games using the score_by_other_players algorithm to predict what a user would like based on
        their three inputted games. This is a helper function for get_three_games"""
        games_so_far = []
        for game in user_games:
            games_so_far += [self.score_by_other_players(game)]

        games_so_far[1].update(games_so_far[2])
        games_so_far[0].update(games_so_far[1])
        sorted_games = dict(sorted(games_so_far[0].items(), key=lambda item: item[1]))
        sorted_keys_list = list(sorted_games)

        if len(sorted_keys_list) >= 3:
            return sorted_keys_list[-3:]
        else:
            sorted_keys_list += self.generate_random_games(3 - len(sorted_keys_list))
            return sorted_keys_list

    def three_games_genre(self, liked_genres: list[str]) -> list[Game]:
        """Return three games using the score_by_genre algorithm to predict what a user would like based on their
        inputted genres they like. This is a helper function for get_three_games."""
        games_so_far = self.score_by_genre(liked_genres)
        sorted_games = dict(sorted(games_so_far.items(), key=lambda item: item[1]))
        sorted_keys_list = list(sorted_games)

        if len(sorted_keys_list) >= 3:
            return sorted_keys_list[-3:]
        else:
            sorted_keys_list += self.generate_random_games(3 - len(sorted_keys_list))
            return sorted_keys_list

    def three_games_players_and_genre(self, user_games: list, liked_genres: list) -> list[Game]:
        """Return three games using the score_by_players_and_genre algorithm to predict what a user would like based on
        their liked genres as well as the games they pick. This is a helper function for get_three_games."""
        games_so_far = []

        for game in user_games:
            score_by_other_players = self.score_by_other_players(game)
            score_by_genre = self.score_by_genre(liked_genres)
            if self.score_by_players_and_genre(score_by_other_players, score_by_genre) != {}:
                games_so_far += [self.score_by_players_and_genre(score_by_other_players, score_by_genre)]
            else:
                games_so_far += [self.generate_random_combined_games(score_by_other_players, score_by_genre,
                                                                     games_so_far)]
        games_so_far[1].update(games_so_far[2])
        games_so_far[0].update(games_so_far[1])

        sorted_games = dict(sorted(games_so_far[0].items(), key=lambda item: item[1]))
        sorted_keys_list = list(sorted_games)

        if len(sorted_keys_list) >= 3:
            return sorted_keys_list[-3:]
        else:
            sorted_keys_list += self.generate_random_games(3 - len(sorted_keys_list))
            return sorted_keys_list

    def generate_random_games(self, num_games: int) -> list[Game]:
        """Return a list of randomly generated games of length num_games.

        Preconditions:
        - num_games >= 1
        """
        games = []
        with_reviews = self.games_with_reviews()

        for _ in range(0, num_games):
            games.append(random.choice(with_reviews))

        return games

    def games_with_reviews(self) -> list[Game]:
        """Return a list of games with at least one review."""
        game_ids = list(self.games)
        return [self.games[game_id] for game_id in game_ids if self.games[game_id].reviewed_by != {}]

    ####################################################################################################################
    # 1st algorithm -- other players
    ####################################################################################################################
    def score_by_other_players(self, game: Game) -> dict[Game, int]:
        """Return a dictionary mapping the score of each game connected to a player that likes the given game.
        Key: game, value: the game's score
        >>> game_ids = [ids for ids in graph.games]
        >>> with_reviews = [graph.games[ids] for ids in game_ids if graph.games[ids].reviewed_by != {}]
        >>> graph.score_by_other_players(with_reviews[0])
        {True: 1}
        """
        other_games_so_far = {}  # maps games to its score, which is the number of players who liked it

        for key in game.reviewed_by:
            player_tup = game.reviewed_by[key]
            if player_tup[1]:  # if player likes the game

                for other_game in player_tup[0].games_reviewed:
                    reviewed_game = player_tup[0].games_reviewed[other_game]

                    # if player likes other game and this game is not the same one as the parameter 'game'
                    if reviewed_game[1] and reviewed_game[0] is not game:
                        # compute score
                        if reviewed_game[0] not in other_games_so_far:
                            other_games_so_far[reviewed_game[0]] = 1
                        else:
                            other_games_so_far[reviewed_game[0]] += 1

        return other_games_so_far

    ####################################################################################################################
    # 2nd algorithm -- genres
    ####################################################################################################################
    def games_with_genres(self) -> list[Game]:
        """Return a list of games with at least one game tag (genre)."""
        game_ids = list(self.games)
        return [self.games[game_id] for game_id in game_ids if self.games[game_id].game_tags != []]

    def score_by_genre(self, liked_genres: list[str]) -> dict[Game, int]:
        """Return a dictionary mapping each game to its score based on how many genres
        in like_genres it matches with."""

        with_genres = self.games_with_genres()
        genre_scores = {}  # key: a Game from with_reviews, value: its score
        liked_genres_len = len(liked_genres)

        for game in with_genres:
            # find how many liked_genres match with the game
            score = 0
            for liked_genre in liked_genres:
                if liked_genre in game.game_tags:
                    # genres are ordered starting with the most important, so those at the beginning of the list
                    # are weighted more.
                    significance = 0.5 * (liked_genres_len - 1 - liked_genres.index(liked_genre))
                    score += 1 + significance

            genre_scores[game] = score

        return genre_scores

    ###################################################################################################################
    # 3rd algorithm -- players and genres
    ###################################################################################################################
    def score_by_players_and_genre(self, score_by_other_players: dict, score_by_genre: dict) -> dict:
        """Return a dictionary mapping the score of each game, where the score is calculated based on the number of
        other players who liked the game as well as the genres the player likes.
        """
        combined_game_scores = {}
        for game in score_by_other_players:
            if game in score_by_genre:
                combined_game_scores[game] = score_by_other_players[game] + score_by_genre[game]
        return combined_game_scores

    def generate_random_combined_games(self, score_by_other_players: dict, score_by_genre: dict,
                                       games_so_far: list) -> dict:
        """Return a dictionary mapping a Game object to its corresponding value. This game is chosen by randomly
        selecting an algorithm, then taking the game with the highest score if it exists.
        """
        sorted_score_by_other_players = dict(sorted(score_by_other_players.items(), key=lambda item: item[1]))
        sorted_score_by_genre = dict(sorted(score_by_genre.items(), key=lambda item: item[1]))

        random_choice = random.choice(['players', 'genre'])

        if random_choice == 'players':
            score_as_list = list(sorted_score_by_other_players)
            for i in range(1, len(score_by_other_players) + 1):
                if score_as_list[-i] not in games_so_far:
                    return {score_as_list[-i]: sorted_score_by_other_players[score_as_list[-i]]}
            return {}
        else:
            score_as_list = list(sorted_score_by_genre)
            for i in range(1, len(score_by_genre) + 1):
                if score_as_list[-i] not in games_so_far:
                    return {score_as_list[-i]: sorted_score_by_genre[score_as_list[-i]]}
            return {}


# if __name__ == '__main__':
#     import python_ta
#     python_ta.check_all(config={
#         'extra-imports': ['random'],
#         'allowed-io': [],
#         'max-line-length': 120
#     })
