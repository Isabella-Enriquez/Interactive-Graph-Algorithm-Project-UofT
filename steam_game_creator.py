"""CSC111 Winter 2023 Course Project Phase 2: Predictive Steam Game Recommender

Summary
===============================

This module contains the functions that open our json datasets and create our SteamGraph.

Copyright and Usage Information
===============================

This file is provided solely for the private use of TA's and other University of Toronto
St. George faculty. All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

This file is Copyright (c) 2023 Isabella Enriquez, Laura Zhan, and Olivia Wong.
"""
import gzip

from player_game_classes import Player, Game, SteamGraph


def parse(path: str) -> dict:
    """
    Opens our json datasets in loose json format (courtesy of Julian McAuley, distributor of datasets).

    Since the datasets are in loose json format, a typical function that opens json files could not
    properly open our datasets. This code was given alongside the datasets by Julian McAuley, for the
    specific purpose of opening these datasets.
    """
    g = gzip.open(path, 'r')
    for l in g:
        yield eval(l)


def json_games_and_reviews_formatter(json_reviews_file: str, json_games_file: str) -> tuple[list[dict], list[dict]]:
    """Create list of mappings based on the given json files.

    The file json_reviews_file will create a list of mappings of steam users,
    which contains another mapping of steam reviews, alongside other useful information.

    The file json_games_file will create a list of mappings of steam games,
    which contains other useful information.

    Preconditions:
    - json_reviews_file and json_games_files refers to a valid json file
    in the format described in the written report.
    """
    user_reviews = list(parse(json_reviews_file))
    steam_games = list(parse(json_games_file))

    return user_reviews, steam_games


def steamgraph_creator(json_games_and_reviews: tuple[list[dict], list[dict]]) -> SteamGraph:
    """Create a SteamGraph object based on the given data from a json file.
    Preconditions:
    - json_games_and_reviews is in the same format as described in the written report.
    """
    user_reviews = json_games_and_reviews[0]
    steam_games = json_games_and_reviews[1]

    games = []
    game_names_so_far = set()

    for game in steam_games:
        # there are 3 instances (out of 32135) in steam_games where this condition is not met (from our game dataset),
        # but those games are not reviewed by any players (from our reivew dataset).
        if 'id' in game and 'app_name' in game:
            # there is at least 39 instances (out of 32135) instances where this condition is not met (from our dataset)
            # if a Game object with a shared game name already exists (duplicate name),
            # then don't create an instance of this game. This prevents complications with user input for
            # our reccomendation algorithm.
            if game['app_name'] not in game_names_so_far:
                game_names_so_far.add(game['app_name'])
                tags = []
                # there are 163 instances (out 32135) in steam_games where this condition is not met
                # (from our game dataset)
                if 'tags' in game:
                    tags = game['tags']
                # there are 3283 instances in steam_games where this condition is not met (from our game dataset)
                elif 'genres' in game:
                    tags = game['genres']

            games.append(Game(name=game['app_name'], self_id=game['id'], tags=tags))

    new_steam_graph = SteamGraph(games)

    for player in user_reviews:
        new_player = Player(player['user_id'])
        new_steam_graph.add_player(new_player)
        for review in player['reviews']:
            # there are 5317 reviews (out of 59305 reviews) that have no shared id in steam_games (from our datasets)
            # we will exclude those reviews
            if review['item_id'] in new_steam_graph.games:
                new_steam_graph.add_review(player=new_player, game_id=review['item_id'], review=review['recommend'])

    return new_steam_graph


# if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['player_game_classes', 'gzip'],
    #     'allowed-io': ['parse', 'json_games_and_reviews_formatter'],
    #     'max-line-length': 120
    # })
    # data = json_games_and_reviews_formatter('Datasets/australian_user_reviews_v1.json', 'Datasets/steam_games_v2.json')
    # graph = steamgraph_creator(data)
