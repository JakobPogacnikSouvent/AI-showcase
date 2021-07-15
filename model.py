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
        game = self.games[game_id]
        game.play(player_choice)

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