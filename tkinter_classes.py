"""CSC111 Winter 2023 Course Project Phase 2: Predictive Steam Game Recommender

Summary
===============================

This module contains a data class for our tkinter graphical user interface (GUI), where all of our code
across all files comes together.

Copyright and Usage Information
===============================

This file is provided solely for the private use of TA's and other University of Toronto
St. George faculty. All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

This file is Copyright (c) 2023 Isabella Enriquez, Laura Zhan, and Olivia Wong.
"""
from tkinter import *
from tkinter import ttk
import steam_game_creator
from player_game_classes import *


class SteamRecRunner:
    """
    Main runner for tkinter GUI. Creates a GUI window, takes user input, runs our Steam Game Recommender
    algorithms, and produces an output window.

    Instance Attributes:
    - games_dict:
        A mapping of all Steam game names in self.steam_graph to their Game object.
    - genre_list:
        A list of all the Steam genres.
    - raw_data:
        The raw data from opening our json dataset files. Used to create our SteamGraph.
    - steam_graph:
        Our main SteamGraph created from our datasets.
    - frame:
        The main tkinter frame widget that holds all other widgets.
    - mainroot:
        The main tkinter window that holds self.frame and all other widgets. Is responsible for handling
        all user interaction/input/outupt.
    """
    games_dict: dict[str, Game]
    genre_list: list[str]
    raw_data: tuple[list, list]
    steam_graph: SteamGraph
    frame: ttk.Frame
    main_root: Tk

    def __init__(self, root: Tk) -> None:
        """
        Initializes a tkinter window. Takes user input and calls self.compute_recs, which calls our algorithms.
        """
        # Creates instances of all the game titles and genres the user can choose from
        self.compute_games_dict()
        self.compute_genre_list()
        self.main_root = root

        # Initializes the window
        self.main_root.title("Steam Game Recommender")
        self.main_root.columnconfigure(0, weight=1)
        self.main_root.rowconfigure(0, weight=1)

        # Creates a frame widget where all widgets will be placed
        mainframe = ttk.Frame(self.main_root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))    # grid: maps the widget to a certain location on window
        mainframe['borderwidth'] = 2
        mainframe['relief'] = 'sunken'
        self.frame = mainframe

        # Creating label widgets that place text on the frame
        ttk.Label(mainframe, text="Welcome to our Steam Game Recommender!").grid(column=0, row=1, sticky=W,
                                                                                 columnspan=3)
        ttk.Label(mainframe, text="Please enter 3 Steam games you like, and rank 3 genres of "
                                  + "video games that you like/want to try.").grid(column=0, row=2, sticky=W,
                                                                                   columnspan=5)
        ttk.Label(mainframe, text="Each entry box has a updating drop down menu, "
                                  + "containing hundreds of available choices.").grid(column=0, row=3, sticky=W,
                                                                                      columnspan=5)
        ttk.Label(mainframe, text="Please also select an algorithm type for calculating your "
                                  + "game recommendations: ").grid(column=0, row=4, sticky=W, columnspan=5)
        ttk.Label(mainframe, text="     -  Other Steam Users: An algorithm that recommends games based on players "
                                  + "that also like your liked games.").grid(column=0, row=5, sticky=W, columnspan=5)
        ttk.Label(mainframe, text="     -  Genres: An algorithm that recommends games based on your genres "
                                  + "of interest and your liked games.").grid(column=0, row=6, sticky=W, columnspan=5)
        ttk.Label(mainframe, text="Please make sure all entries match an valid entry exactly, all inputs are filled, "
                                  + "and there are no duplicates.").grid(column=0, row=7, sticky=W, columnspan=5)

        # Creating more label widgets
        ttk.Label(mainframe, text="Enter your 1st game:").grid(column=0, row=9, sticky=(S, W))
        ttk.Label(mainframe, text="Enter your 2nd game:").grid(column=0, row=12, sticky=(S, W))
        ttk.Label(mainframe, text="Enter your 3rd game:").grid(column=0, row=15, sticky=(S, W))
        ttk.Label(mainframe, text="Rank your 1st genre:").grid(column=2, row=9, sticky=(S, W))
        ttk.Label(mainframe, text="Rank your 2nd genre:").grid(column=2, row=12, sticky=(S, W))
        ttk.Label(mainframe, text="Rank your 3rd genre:").grid(column=2, row=15, sticky=(S, W))
        ttk.Label(mainframe, text="      ").grid(column=1, row=9)
        ttk.Label(mainframe, text="    ").grid(column=3, row=9)
        ttk.Label(mainframe, text="Please select an recommendation algorithm:").grid(column=4, row=11, sticky=(S, W))

        # Creating radiobutton widgets, where users select one of the options
        alg_config = StringVar()    # StringVar(): saves the results of the widget (from user input)
        other_steam_users = ttk.Radiobutton(mainframe, text='Other Steam Users', variable=alg_config,
                                            value='players')
        other_steam_users.grid(column=4, row=12, sticky=(S, W))
        genres = ttk.Radiobutton(mainframe, text='Genres', variable=alg_config, value='genre')
        genres.grid(column=4, row=13, sticky=W)
        steam_users_and_genres = ttk.Radiobutton(mainframe, text='Other Steam Users and Genres', variable=alg_config,
                                                 value='players_genre')
        steam_users_and_genres.grid(column=4, row=14, sticky=(N, W))

        # Saving instances of entry widgets and listbox widgets for function use
        all_ops = []
        all_genre_entries = []
        all_menus = []

        # Create an Entry widget, where users can type to input a custom answer
        op1 = StringVar()
        all_ops.append(op1)
        entry1 = Entry(mainframe, textvariable=op1)
        entry1.grid(column=0, row=10, sticky=W)

        # Create an Entry widget, where users can type to input a custom answer
        op2 = StringVar()
        all_ops.append(op2)
        entry2 = Entry(mainframe, textvariable=op2)
        entry2.grid(column=0, row=13, sticky=W)

        # Create an Entry widget, where users can type to input a custom answer
        op3 = StringVar()
        all_ops.append(op3)
        entry3 = Entry(mainframe, textvariable=op3)
        entry3.grid(column=0, row=16, sticky=W)

        # Create an Entry widget, where users can type to input a custom answer
        op4 = StringVar()
        all_ops.append(op4)
        entry4 = Entry(mainframe, textvariable=op4)
        entry4.bind('<KeyRelease>', lambda e: self.check(all_genre_entries, all_menus))
        entry4.grid(column=2, row=10, sticky=W)
        all_genre_entries.append(entry4)
        # Create a Listbox widget to display the list of items
        menu4 = Listbox(mainframe, height=4)
        menu4.grid(column=2, row=11, sticky=W)
        all_menus.append(menu4)

        # Create an Entry widget, where users can type to input a custom answer
        op5 = StringVar()
        all_ops.append(op5)
        entry5 = Entry(mainframe, textvariable=op5)
        entry5.bind('<KeyRelease>', lambda e: self.check(all_genre_entries, all_menus))
        entry5.grid(column=2, row=13, sticky=W)
        all_genre_entries.append(entry5)
        # Create a Listbox widget to display the list of items
        menu5 = Listbox(mainframe, height=4)
        menu5.grid(column=2, row=14, sticky=W)
        all_menus.append(menu5)

        # Create an Entry widget, where users can type to input a custom answer
        op6 = StringVar()
        all_ops.append(op6)
        entry6 = Entry(mainframe, textvariable=op6)
        entry6.bind('<KeyRelease>', lambda e: self.check(all_genre_entries, all_menus))
        entry6.grid(column=2, row=16, sticky=W)
        all_genre_entries.append(entry6)
        # Create a Listbox widget to display the list of items
        menu6 = Listbox(mainframe, height=4)
        menu6.grid(column=2, row=17, sticky=W)
        all_menus.append(menu6)

        # Initialize values to all genre listboxes
        self.update(self.genre_list, menu4)
        self.update(self.genre_list, menu5)
        self.update(self.genre_list, menu6)

        # Spaces out widgets
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # Creates a label that is updated when the confirm button is pressed (either error message or confirmation)
        invalid_entry = StringVar()
        ttk.Label(mainframe, textvariable=invalid_entry).grid(column=0, row=18, sticky=W, columnspan=5)

        # Creates a button widget that runs a function when clicked on by user
        confirm = ttk.Button(mainframe, text="Confirm", command=lambda: self.compute_recs(all_ops, alg_config,
                                                                                          invalid_entry, confirm))
        confirm.grid(column=4, row=18, sticky=E)

    def check(self, entries: list, menus: list) -> None:
        """
        Function that is called whenever user updates the entry box. Updates the corresponding listbox
        to show the items in self.genre_list that correspond to the user's input so far.
        """
        all_v = [entry.get() for entry in entries]
        all_menus = menus

        for v in range(len(all_v)):
            if all_v[v] == '':
                data = self.genre_list
            else:
                data = []
                [data.append(item) for item in self.genre_list if all_v[v].lower() in item.lower()]
            self.update(data, all_menus[v])

    def update(self, data: list, menu: Listbox) -> None:
        """
        Updates the listboxes under the entry widgets with the items from self.genre_list.
        """
        # Clear the Combobox
        menu.delete(0, END)
        # Add values to the combobox
        for value in data:
            menu.insert(END, value)

    def compute_games_dict(self) -> None:
        """
        Initializes self.games_dict. Opens and formats the json dataset files (initializes self.raw_data),
        creates a SteamGraph from that data (initializes self.steam_graph), and creates a mapping of all game titles
        and their corresponding Game object.
        """
        self.raw_data = steam_game_creator.json_games_and_reviews_formatter('Datasets/australian_user_reviews_v1.json',
                                                                            'Datasets/steam_games_v2.json')
        self.steam_graph = steam_game_creator.steamgraph_creator(self.raw_data)
        self.games_dict = {}
        for key in self.steam_graph.games:
            self.games_dict[self.steam_graph.games[key].game_name] = self.steam_graph.games[key]

    def compute_genre_list(self) -> None:
        """
        Initializes self.genre_list. Opens the cvs file with all genres.
        """
        with open('Datasets/steam_genres.csv') as f:
            self.genre_list = [str.strip(line) for line in f]

    def compute_recs(self, ops: list, alg_config_item: StringVar, invalid_entry_item: StringVar,
                     confirm_item: ttk.Button) -> None:
        """
        Function that is called when the confirm button is pressed. Runs our Steam Game Recommender algorithms
        and produces an output window.
        """
        try:
            get_values = [str(entry.get()) for entry in ops]
            alg_value = str(alg_config_item.get())
            # if all game titles are valid, all genres are valid, all inputted values are unique (no duplicates),
            # and a radiobutton is selected:
            if all([value in self.games_dict for value in get_values[:3]]) and \
                    all([value in self.genre_list for value in get_values[3:]]) and \
                    len(get_values) == len(set(get_values)) and alg_value != '':
                invalid_entry_item.set('Valid Entry. Please wait.')
                # Removes the confirm button widget so users can't press it again after sucessfully inputting
                confirm_item.grid_remove()

                # Retrieving Game objects according to the game titles and all genres to be inputted into our algorithm
                game_objects = [self.games_dict[get_values[0]], self.games_dict[get_values[1]],
                                self.games_dict[get_values[2]]]
                genre_objects = [get_values[3], get_values[4], get_values[5]]
                # Our main algorithm function
                three_recs = self.steam_graph.get_three_games(game_objects, genre_objects, alg_value)
                # Final output function
                self.output_recs(three_recs, get_values)

            else:
                if not get_values[0] in self.games_dict:
                    invalid_entry_item.set('Your 1st game input is not a valid game. Please input a valid game title.')
                elif not get_values[1] in self.games_dict:
                    invalid_entry_item.set('Your 2nd game input is not a valid game. Please input a valid game title.')
                elif not get_values[2] in self.games_dict:
                    invalid_entry_item.set('Your 3rd game input is not a valid game. Please input a valid game title.')
                elif len(get_values) != len(set(get_values)):
                    invalid_entry_item.set('There is a duplicate response. Please make sure all inputs are unique.')
                else:
                    invalid_entry_item.set('At least one non-game input is invalid.')

        except ValueError:
            pass

    def output_recs(self, game_recs: list[Game, Game, Game], input_values: list[str]) -> None:
        """
        Function that is called after our algorithms return 3 games. Wipes the input window and
        creates a new output window.
        """
        game1_raw = [dic for dic in self.raw_data[1] if 'id' in dic and dic['id'] == game_recs[0].game_id][0]
        game2_raw = [dic for dic in self.raw_data[1] if 'id' in dic and dic['id'] == game_recs[1].game_id][0]
        game3_raw = [dic for dic in self.raw_data[1] if 'id' in dic and dic['id'] == game_recs[2].game_id][0]

        self.frame.destroy()

        mainframe2 = ttk.Frame(self.main_root, padding="3 3 12 12")
        mainframe2.grid(column=0, row=0, sticky=(N, W, E, S))  # grid: maps the widget to a certain location on window
        mainframe2['borderwidth'] = 2
        mainframe2['relief'] = 'sunken'

        ttk.Label(mainframe2, text=f"Based on your chosen games: {input_values[0]} , {input_values[1]} , "
                                   + f"{input_values[2]} ,").grid(column=0, row=0, sticky=W, columnspan=5)
        ttk.Label(mainframe2, text=f"and your chosen genres: {input_values[3]} , {input_values[4]} , "
                                   + f"{input_values[5]} ,").grid(column=0, row=1, sticky=W, columnspan=5)
        ttk.Label(mainframe2, text="Here are your recommendations based on your chosen games and genres!"
                  ).grid(column=0, row=2, sticky=W, columnspan=5)

        # Spacers
        ttk.Label(mainframe2, text="      ").grid(column=1, row=4)
        ttk.Label(mainframe2, text="      ").grid(column=3, row=4)

        # GAME 1
        # line_start: counter for what line to place game information (since some are non-existent for certain games)
        line_start1 = 5
        ttk.Label(mainframe2, text='GAME 1').grid(column=0, row=3, sticky=W)
        ttk.Label(mainframe2, text=f'Game title:  {game_recs[0].game_name}').grid(column=0, row=4, sticky=W)

        if game_recs[0].game_tags != []:
            ttk.Label(mainframe2, text='Game genres:').grid(column=0, row=line_start1, sticky=W)
            menu7 = Listbox(mainframe2, height=4)
            menu7.grid(column=0, row=line_start1 + 1, sticky=W)
            self.update(list(game_recs[0].game_tags), menu7)
            line_start1 += 2

        if 'publisher' in game1_raw:
            ttk.Label(mainframe2, text=f'Publisher:  {game1_raw["publisher"]}').grid(column=0, row=line_start1,
                                                                                     sticky=W)
            line_start1 += 1

        if 'developer' in game1_raw:
            ttk.Label(mainframe2, text=f'Developer:  {game1_raw["developer"]}').grid(column=0, row=line_start1,
                                                                                     sticky=W)
            line_start1 += 1

        if 'release_date' in game1_raw:
            ttk.Label(mainframe2, text=f'Release Date:  {game1_raw["release_date"]}').grid(column=0, row=line_start1,
                                                                                           sticky=W)
            line_start1 += 1

        if 'specs' in game1_raw:
            ttk.Label(mainframe2, text='Other Specs:').grid(column=0, row=line_start1, sticky=W)
            menu8 = Listbox(mainframe2, height=4)
            menu8.grid(column=0, row=line_start1 + 1, sticky=W)
            self.update(game1_raw['specs'], menu8)
            line_start1 += 2

        if 'price' in game1_raw:
            ttk.Label(mainframe2, text=f'Price:  {game1_raw["price"]}').grid(column=0, row=line_start1, sticky=W)
            line_start1 += 1

        if 'url' in game1_raw:
            ttk.Label(mainframe2, text='Steam URL:').grid(column=0, row=line_start1, sticky=W)
            url_text = Text(mainframe2, width=15, height=7, wrap='char')
            url_text.grid(column=0, row=line_start1 + 1, columnspan=5, sticky=W)
            url_text.insert('1.0', game1_raw['url'])
            url_text['state'] = 'disabled'

        # GAME 2
        # line_start: counter for what line to place game information (since some are non-existent for certain games)
        line_start2 = 5
        ttk.Label(mainframe2, text='GAME 2').grid(column=2, row=3, sticky=W)
        ttk.Label(mainframe2, text=f'Game title:  {game_recs[1].game_name}').grid(column=2, row=4, sticky=W)

        if game_recs[1].game_tags != []:
            ttk.Label(mainframe2, text='Game genres:').grid(column=2, row=line_start2, sticky=W)
            menu9 = Listbox(mainframe2, height=4)
            menu9.grid(column=2, row=line_start2 + 1, sticky=W)
            self.update(list(game_recs[1].game_tags), menu9)
            line_start2 += 2

        if 'publisher' in game2_raw:
            ttk.Label(mainframe2, text=f'Publisher:  {game2_raw["publisher"]}').grid(column=2, row=line_start2,
                                                                                     sticky=W)
            line_start2 += 1

        if 'developer' in game2_raw:
            ttk.Label(mainframe2, text=f'Developer:  {game2_raw["developer"]}').grid(column=2, row=line_start2,
                                                                                     sticky=W)
            line_start2 += 1

        if 'release_date' in game2_raw:
            ttk.Label(mainframe2, text=f'Release Date:  {game2_raw["release_date"]}').grid(column=2,
                                                                                           row=line_start2, sticky=W)
            line_start2 += 1

        if 'specs' in game2_raw:
            ttk.Label(mainframe2, text='Other Specs:').grid(column=2, row=line_start2, sticky=W)
            menu10 = Listbox(mainframe2, height=4)
            menu10.grid(column=2, row=line_start2 + 1, sticky=W)
            self.update(game2_raw['specs'], menu10)
            line_start2 += 2

        if 'price' in game2_raw:
            ttk.Label(mainframe2, text=f'Price:  {game2_raw["price"]}').grid(column=2, row=line_start2, sticky=W)
            line_start2 += 1

        if 'url' in game2_raw:
            ttk.Label(mainframe2, text='Steam URL:').grid(column=2, row=line_start2, sticky=W)
            url_text = Text(mainframe2, width=15, height=7, wrap='char')
            url_text.grid(column=2, row=line_start2 + 1, columnspan=5, sticky=W)
            url_text.insert('1.0', game2_raw['url'])
            url_text['state'] = 'disabled'

        # GAME 3
        # line_start: counter for what line to place game information (since some are non-existent for certain games)
        line_start3 = 5
        ttk.Label(mainframe2, text='GAME 3').grid(column=4, row=3, sticky=W)
        ttk.Label(mainframe2, text=f'Game title:  {game_recs[2].game_name}').grid(column=4, row=4, sticky=W)

        if game_recs[2].game_tags != []:
            ttk.Label(mainframe2, text='Game genres:').grid(column=4, row=line_start3, sticky=W)
            menu11 = Listbox(mainframe2, height=4)
            menu11.grid(column=4, row=line_start3 + 1, sticky=W)
            self.update(list(game_recs[2].game_tags), menu11)
            line_start3 += 2

        if 'publisher' in game3_raw:
            ttk.Label(mainframe2, text=f'Publisher:  {game3_raw["publisher"]}').grid(column=4, row=line_start3,
                                                                                     sticky=W)
            line_start3 += 1

        if 'developer' in game3_raw:
            ttk.Label(mainframe2, text=f'Developer:  {game3_raw["developer"]}').grid(column=4, row=line_start3,
                                                                                     sticky=W)
            line_start3 += 1

        if 'release_date' in game3_raw:
            ttk.Label(mainframe2, text=f'Release Date:  {game3_raw["release_date"]}').grid(column=4,
                                                                                           row=line_start3,
                                                                                           sticky=W)
            line_start3 += 1

        if 'specs' in game3_raw:
            ttk.Label(mainframe2, text='Other Specs:').grid(column=4, row=line_start3, sticky=W)
            menu12 = Listbox(mainframe2, height=4)
            menu12.grid(column=4, row=line_start3 + 1, sticky=W)
            self.update(game3_raw['specs'], menu12)
            line_start3 += 2

        if 'price' in game3_raw:
            ttk.Label(mainframe2, text=f'Price:  {game3_raw["price"]}').grid(column=4, row=line_start3, sticky=W)
            line_start3 += 1

        if 'url' in game3_raw:
            ttk.Label(mainframe2, text='Steam URL:').grid(column=4, row=line_start3, sticky=W)
            url_text = Text(mainframe2, width=15, height=7, wrap='char')
            url_text.grid(column=4, row=line_start3 + 1, columnspan=5, sticky=W)
            url_text.insert('1.0', game3_raw['url'])
            url_text['state'] = 'disabled'

        # Spaces out widgets
        for child in mainframe2.winfo_children():
            child.grid_configure(padx=5, pady=5)


# if __name__ == '__main__':
#     import python_ta
#     python_ta.check_all(config={
#         'extra-imports': ['tkinter', 'tkk', 'steam_game_creator', 'player_game_classes'],
#         'allowed-io': ['SteamRecRunner.compute_genre_list'],
#         'max-line-length': 120
#     })
