from tkinter import *
from game_play_functions import *
from player_area_class import Player, Area


MAX_PLAYERS = 4
PLAYER_NAMES = []


def game_play():
    areas = generate_areas()
    add_player_window()
    players = []
    for player_name in PLAYER_NAMES:
        players += [Player(player_name)]
    start_game(players, areas)
    player_turn(players[0], areas, players)


def add_player_window():
    root = Tk()
    root.title = ""

    title = Label(root, text='Justice Board Game')
    title.grid(row=0, column=0, columnspan=2)

    message = Label(root, text='Add Player')
    message.grid(row=1, column=0, columnspan=2)

    input_field = Entry(root, width=50, font=('Helvetica', 8))
    input_field.grid(row=2, column=0)

    def add_player(PLAYER_NAMES):
        if len(PLAYER_NAMES) < MAX_PLAYERS:
            message = "Added " + input_field.get()
            Label(root, text=message).grid(row=4, column=0)
            PLAYER_NAMES += [input_field.get()]
            input_field.delete(0, 'end')
        else:
            message = 'Max amount of players has been reached'
            Label(root, text=message).grid(row=4, column=0)
            input_field.delete(0, 'end')

    my_button = Button(root, text="Add", command=lambda: add_player(PLAYER_NAMES))
    my_button.grid(row=2, column=1)

    move_on_button = Button(root, text='Continue', command=root.quit)
    move_on_button.grid(row=3, column=1)

    root.mainloop()


if __name__ == '__main__':
    game_play()
