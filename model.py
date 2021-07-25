import random
import json
import hashlib

class RPS:
    def __init__(self, computer_ai=None):
        # For internal logic numbers are used to represent rock, paper and scissors
        #
        # As it may be usefull to have rps mapped to numbers in the future a dictionary is used along with getter methods to
        # return player_choice and computer_choice in string if neded 

        self.translator = {'rock' : 0, 'paper' : 1, 'scissors' : 2}
        self.reverse_translator = {0 : 'rock', 1 : 'paper', 2 : 'scissors'}

        # Set function to be used as AI, default is random.
        self.ai = computer_ai or self._choose_random
        
        self.player_choice = None
        self.computer_choice = None

        # One of 'player', 'computer', 'draw'
        self.winner = None 

    def get_player_choice(self):
        # Player choice getter. Returns str
        if self.player_choice is not None:
            return self.reverse_translator[self.player_choice]
        else:
            return None

    def get_computer_choice(self):
        # Computer choice getter. Returns str
        if self.player_choice is not None:
            return self.reverse_translator[self.computer_choice]
        else:
            return None
            
    def play(self, player_choice):
        if player_choice in ('rock', 'paper', 'scissors'):
            player_choice = self.translator[player_choice]
        
        if player_choice not in (0,1,2):
            raise ValueError('Unuspported value for player_choice in RPS.play')

        self.player_choice = player_choice

        # Choose computer response and eval winner
        self.ai()
        self._eval_winner()
        self._save_data()

    def _choose_random(self):
        self.computer_choice = random.randint(0,2)

    def _eval_winner(self):
        if self.player_choice is None: # Only check player_choice because computer choice is always evaluated immediatelly after player choice
            raise ValueError('Player_choice is of type None in eval_winner; 0, 1, 2 expected')

        else:
            if self.player_choice == self.computer_choice:
                self.winner = 'draw'

            elif self.player_choice == (self.computer_choice + 1) % 3:
                self.winner = 'player'
            
            else:
                self.winner = 'computer'
    
    def _save_data(self):
        # Will open file and update the winner
        pass

class RPS_controller:
    """
    A class that enables and handles running of multiple RPS game instances.
    """

    def __init__(self):
        self.games = {} # dict of <id, RPS>

    def new_game(self):
        game_id = self._get_new_id()
        game = RPS()
        self.games[game_id] = game
        return game_id

    def _get_new_id(self):
        if not self.games:
            new_id = 0
        else:
            new_id = max(self.games.keys()) + 1
        
        return new_id

    def play(self, game_id, player_choice):
        self.games[game_id].play(player_choice)

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password # Hashed 

    @staticmethod
    def get_user_data_file(username):
        return f"{username}.json"
    
    def toDict(self):
        return {'username' : self.username, 'password' : self.password}

    def save_user_to_file(self):
        with open(User.get_user_data_file(self.username), 'w') as File:
            json.dump(self.toDict(), File, ensure_ascii=False, indent=4)
        
    @staticmethod
    def load_user_from_file(username):
        try:
            with open(User.get_user_data_file(username)) as File:
                data_dict = json.load(File)

                uname = data_dict['username']
                passwd = data_dict['password']

                return User(uname, passwd)
        except FileNotFoundError:
            print(f'File for user {username} not found.')
            return None
    
    @staticmethod
    def register(username, password_cleartext):
        if User.load_user_from_file(username) is not None:
            raise ValueError('Username already taken.')
        else:
            password = User._hash_password(password_cleartext)
            user = User(username, password)
            user.save_user_to_file()
            return user
    @staticmethod
    def login(username, password_cleartext):
        try:
            user = User.load_user_from_file(username)

            if user.check_password(password_cleartext):
                return user
            else:
                # For security reasons we don't want to give feedback as to whether the user or the password was incorect
                # as it prevents people from finding out all the usernames on our website
                raise ValueError("Username or password do not match.")
        
        except AttributeError: # If User.load_user_from_file returns None
           # For security reasons we don't want to give feedback as to whether the user or the password was incorect
           # as it prevents people from finding out all the usernames on our website
            raise ValueError("Username or password do not match.")
    
    @staticmethod
    def _hash_password(password_cleartext, salt=None):
        if salt is None:
            salt = str(random.getrandbits(32))
        salted_pswd = salt + password_cleartext
        h = hashlib.blake2b()
        h.update(salted_pswd.encode(encoding='utf-8'))
        return f"{salt}${h.hexdigest()}"
    
    def check_password(self, password_cleartext):
        salt, _ = self.password.split('$')
        return self.password == User._hash_password(password_cleartext, salt)

class TIAR: #Three In A Row
    def __init__(self, computer_ai = None):
        self.board = [[0 for i in range(3)] for j in range(3)] # 3x3 board 0=empty, 1=player, 2=CPU
        
        self.winner = None

        self.ai = computer_ai or self._random_AI

    def play(self, x, y, player):

        # If the game has already ended return winner
        if self.winner is not None:
            self.winner
        
        # Make move
        self.board[x][y] = player
        
        # Check if the move results in game ending
        if (winner := self._check_game_end()):
            self.winner = winner
            return winner

    def is_valid_move(self, x, y):
        return not self.board[x][y]

    def _check_game_end(self):

        # Check all rows
        for row in self.board:
            if len(set(row)) == 1 and row[0] != 0:
                winner = row[0]
                return winner

        # Check all columns
        for i in range(3):
            print(i)
            print([self.board[j][i] for j in range(3)])
            if len({self.board[j][i] for j in range(3)}) == 1 and self.board[0][i] != 0:
                winner = self.board[0][i]
                return winner

        # Check both diagonals
        if len({self.board[i][i] for i in range(3)}) == 1 and self.board[0][0] != 0:
            winner = self.board[0][0]
            return winner

        if len({self.board[i][-(i+1)] for i in range(3)}) == 1 and self.board[0][-1] != 0:
            winner = self.board[0][-1]
            return winner

        # Check if board is not full
        for row in self.board:
            if 0 in row:
                return None

        # If board is full
        return 3 # 3=draw

    def _random_AI(self):
        x = random.randint(0,2)
        y = random.randint(0,2)

        # Randomize untill the move is valid.
        # As there are only 9 possible moves and it takes 0.0010001659393310547s to calculate 1000 randomizations there is approximately 3.6 * 10^-954242508 percent chance of not finding a valid move after 1s
        while not self.is_valid_move(x,y):
            x = random.randint(0,2)
            y = random.randint(0,2)


        if (winner := self.play(x, y, 2)): # self.play checks if game is over
            return winner


class TIAR_controller:
    def __init__(self):
        self.games = {} # dict of <id, TIAR>

    def new_game(self, starting_player=1):
        # For staring player 1=P1, 2=CPU

        game_id = self._get_new_id()
        game = TIAR()
        self.games[game_id] = game
        
        if starting_player == 2:
            # If starting player is computer make the first move

            game.ai() # No need to check for winner on the first move
        
        return game_id

    def player_play(self, game_id, x, y):
        """
        Makes the player move in the game with game_id.
        If the player move does not result in victory it makes the ai move.
        If neither player nor ai move results in victory it returns None.

        If the game with game_id has alredy concluded it returns its winner.
        """


        # If the game has already ended return winner
        if self.games[game_id].winner is not None:
            return self.games[game_id].winner

        # If move is invalid return None
        if not self.games[game_id].is_valid_move(x,y):
            return None

        # If player makes a winning move return a winner
        if (winner := self.games[game_id].play(x, y, 1)): # 1=P1, 2=CPU
            return winner
        
        # If there is no winner after player move make AI move
        else:

            # If AI make a winning move return a winner
            if (winner := self.games[game_id].ai()):
                return winner
        
        # If neither player or AI wins return None
        return None

    def _get_new_id(self):
        if not self.games:
            new_id = 0
        else:
            new_id = max(self.games.keys()) + 1
        
        return new_id