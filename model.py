import random
import json
from json.decoder import JSONDecodeError
import hashlib
from copy import deepcopy

class GameController:
    def __init__(self, GameClass):
        self.games = {} # dict of <id, GameObject>
        self.game_class = GameClass
        self.games_counter = 0

    def _get_new_id(self):
        """
        For memory reasons in scalability we should probably reset the games counter at some point.
        But as we do not expect to ever create more than 1000 games and also due to the fact that
        python integers do not have an upper bound such solution is adequate until our site gets
        bought by google.
        """
        new_id = self.games_counter

        self.games_counter += 1
        
        return new_id

    def new_game(self, user, game_ai_method=0, starting_player=1):
        # For staring player 1=P1, 2=CPU

        game_id = self._get_new_id()
        game = self.game_class(user, game_ai_method)

        self.games[game_id] = game
        
        if starting_player == 2:
            # If starting player is computer make the first move

            game.ai() # No need to check for winner on the first move
        
        return game_id

    def player_play(self, game_id, *args):
        """
        Makes the player move in the game with game_id.
        If the player move does not result in victory it makes the ai move.
        If neither player nor ai move results in victory it returns None.

        If the game with game_id has alredy concluded it returns its winner.
        If the player move is invalid it returns None
        """


        # If the game has already ended return winner
        if self.games[game_id].winner is not None:
            return self.games[game_id].winner

        # If move is invalid return None
        if not self.games[game_id].is_valid_move(*args):
            return None

        # If player makes a winning move return a winner
        if (winner := self.games[game_id].play(1, *args)): # 1=P1, 2=CPU
            self._update_player_score(self.games[game_id])
            return winner
        
        # If there is no winner after player move make AI move
        else:

            # If AI make a winning move return a winner
            if (winner := self.games[game_id].ai()):
                self._update_player_score(self.games[game_id])
                return winner
        
        # Check if game ended in a draw
        if self.games[game_id].winner == 3:
            self._update_player_score(self.games[game_id])
            return self.games[game_id].winner

        # If neither player or AI wins return None
        return None
    
    def _update_player_score(self, game):
        """
        Update the score in player files.
        """
        player = game.P1

        user = User.load_user_from_file(player)

        try:
            game_ai_dict = user.data[game.__class__.__name__]

        except KeyError: # If game hasn't been played before
            game_ai_dict = dict()
            user.data[game.__class__.__name__] = game_ai_dict

        try:
            score_vs_ai = user.data[game.__class__.__name__][game.get_ai_name_text()]
            
        except KeyError: # If game ai hasn't been played before
            score_vs_ai = {'player' : 0, 'cpu' : 0, 'draw' : 0}
            user.data[game.__class__.__name__][game.get_ai_name_text()] = score_vs_ai
            

        translator = {1 : 'player', 2 : 'cpu', 3 : 'draw'}
        score_vs_ai[translator[game.winner]] += 1

        user.save_user_to_file()

    def fix_memory_leak(self):
        """
        Deletes all games that have finished in self.games

        This has linear time complexity but as we do not expect our usercount to exceed 1000
        we can pretend that it's trivial

        NOTE: If user leaves the website when he hasn't finished the game the game will still stay in memory and cause a memory leak.
        A possible solution for this would be to save the time a game was started and remove all games that have been active for a
        certain time.
        """
        games_to_delete = []

        for ID in self.games.keys():
            if self.games[ID].winner:
                games_to_delete.append(ID)

        for ID in games_to_delete:
            del(self.games[ID])

class GameTemplate:
    """
    Template object for Game inheritance that contains all functions needed in GameController.
    """
    def __init__(self, user, computer_ai):
        self.winner = None
        self.ai = computer_ai
        self.P1 = user
        self.ai_translator = dict() # Used to convert ai method to nice text format
    
    def is_valid_move(self, *args):
        # If game does not have this function it means that it has no need to check whether moves are valid and therefore all moves are valid.
        return True
    
    def play(self):
        return self.winner

    def get_ai_name_text(self):
        # Returns a nice text representation of the ai method
        # e.g.: 
        # get_ai_name_text of game class that is using the function _choose_random or _random_AI would return "Random AI"

        try:
            return self.ai_translator[self.ai]
        except KeyError:
            return "AI name not defined."

class RPS(GameTemplate):
    def __init__(self, user, computer_ai=0):
        ai_translator = {0 : self._choose_random, 1 : self._greedy, 2 : self._calculate_percentage}

        super().__init__(user, ai_translator[computer_ai])

        # For internal logic numbers are used to represent rock, paper and scissors
        #
        # As it may be usefull to have rps mapped to numbers in the future a dictionary is used along with getter methods to
        # return player_choice and computer_choice in string if neded 

        self.translator = {'rock' : 0, 'paper' : 1, 'scissors' : 2}
        self.reverse_translator = {0 : 'rock', 1 : 'paper', 2 : 'scissors'}

        self.ai_translator = {self._choose_random : "Random AI", self._greedy : "Greedy AI", self._calculate_percentage : "Average AI"}

        self.player_choice = None
        self.computer_choice = None

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

    def _choose_random(self):
        self.computer_choice = random.randint(0,2)

    def _calculate_percentage(self):
        """
        This mehod works by calculating the percentage of oponent's last chosen actions and assuming the percentages hold true for the future.
        """
        # Index 0=Rock, 1=Paper, 2=Scissors
        weights = [0, 0, 0]

        user = User.load_user_from_file(self.P1)

        try:
            history = user.data[self.__class__.__name__]['History']

            for player_choice, winner in history:
                weights[player_choice] += 1
            
            predicted_player_choice = random.choices([0,1,2], weights)[0]
            self.computer_choice = (predicted_player_choice + 1) % 3

            
        except KeyError: # If game hasn't been played before
            self._choose_random()

    def _greedy(self):
        user = User.load_user_from_file(self.P1)

        try:
            history = user.data[self.__class__.__name__]['History']

            last_player_choice, last_player_score = history[-1]

            if last_player_score == 1: # If player has won we predict he will chose the same
                self.computer_choice = (last_player_choice + 1) % 3
            
            elif last_player_score == 2:
                self.computer_choice = (last_player_choice - 1) % 3

            else:
                self._choose_random()

        
        except KeyError:
            self._choose_random()

    def _eval_winner(self):
        if self.player_choice is None: # Only check player_choice because computer choice is always evaluated immediatelly after player choice
            raise ValueError('Player_choice is of type None in eval_winner; 0, 1, 2 expected')

        else:
            if self.player_choice == self.computer_choice:
                self.winner = 3 # Draw

            elif self.player_choice == (self.computer_choice + 1) % 3:
                self.winner = 1 # Player
            
            else:
                self.winner = 2 # Computer

class RPS_controller(GameController):
    """
    A class that enables and handles running of multiple RPS game instances.
    """

    def __init__(self):
        super().__init__(RPS)

    def player_play(self, game_id, player_choice):
        self.games[game_id].play(player_choice)
        self._update_player_score(self.games[game_id])

    def fix_memory_leak(self):
        """
        As RPS game object spends most of it's time in a finished state
        and it supports replaying from the finished state we need another way
        of clearing its saved games 
        """
        pass

    def _update_player_score(self, game):
        """
        For RPS we also want to save what players chose in the past.
        """
        # Super()._update_player_score()
        player = game.P1

        user = User.load_user_from_file(player)

        try:
            game_ai_dict = user.data[game.__class__.__name__]

        except KeyError: # If game hasn't been played before
            game_ai_dict = dict()
            user.data[game.__class__.__name__] = game_ai_dict

        try:
            score_vs_ai = user.data[game.__class__.__name__][game.get_ai_name_text()]
            
        except KeyError: # If game ai hasn't been played before
            score_vs_ai = {'player' : 0, 'cpu' : 0, 'draw' : 0}
            user.data[game.__class__.__name__][game.get_ai_name_text()] = score_vs_ai
            

        translator = {1 : 'player', 2 : 'cpu', 3 : 'draw'}
        score_vs_ai[translator[game.winner]] += 1
        # End of Super()._update_player_score()

        # Update player choice history
        try:
            history = user.data[game.__class__.__name__]['History']
            history.append((game.player_choice, game.winner))
        except KeyError:
            user.data[game.__class__.__name__]['History'] = [(game.player_choice, game.winner)]

        user.save_user_to_file()

class User:
    def __init__(self, username, password, data=None):
        self.username = username
        self.password = password # Hashed
        self.data = data or dict() # Will save win and loss data for all games

    @staticmethod
    def get_user_data_file(username):
        return f"{username}.json"
    
    def toDict(self):
        return {'username' : self.username, 'password' : self.password, 'data' : self.data}

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
                data = data_dict['data']

                return User(uname, passwd, data)
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

class TIAR(GameTemplate): #Three In A Row
    def __init__(self, user, computer_ai=0):
        ai_translator = {0 : self._random_AI, 1 : self._minmax_AI}

        super().__init__(user, ai_translator[computer_ai])

        self.ai_translator = {self._random_AI : "Random AI", self._minmax_AI : "Minmax AI"}

        self.board = [[0 for i in range(3)] for j in range(3)] # 3x3 board 0=empty, 1=player, 2=CPU

    def play(self, player, x, y):

        # If the game has already ended return winner
        if self.winner is not None:
            self.winner
        
        # Make move
        self.board[x][y] = player
        
        # Update winner
        self.winner = self._check_game_end() # If there is no winner _check_game_end returns None
        return self.winner

    def is_valid_move(self, x, y):
        return not self.board[x][y]

    def _check_game_end(self, board=None):
        """
        Check current board state if the game is over.
        returns:
            1 : if P1 won
            2 : if CPU won
            3 : if game is a draw
            None : if no winner and game is not over
        """

        board = board or self.board

        # Check all rows
        for row in board:
            if len(set(row)) == 1 and row[0] != 0:
                winner = row[0]
                return winner

        # Check all columns
        for i in range(3):
            if len({board[j][i] for j in range(3)}) == 1 and board[0][i] != 0:
                winner = board[0][i]
                return winner

        # Check both diagonals
        if len({board[i][i] for i in range(3)}) == 1 and board[0][0] != 0:
            winner = board[0][0]
            return winner

        if len({board[i][-(i+1)] for i in range(3)}) == 1 and board[0][-1] != 0:
            winner = board[0][-1]
            return winner

        # Check if board is not full
        for row in board:
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

        return self.play(2, x, y) # Return winner
    
    def _minmax_AI(self):
        best_move = self._find_best_move(deepcopy(self.board), 2)

        x, y, _ = best_move

        print(best_move)

        self.play(2, x, y)

    def _board_to_str(self, board):
        s = ""
        for row in board:
            for value in row:
                s += str(value)
        return s

    def _find_best_move(self, board, player, depth=3):
        print(f"We got the board {board}")
        
        try:
            with open('tiar_ai.json') as File:
                data_dict = json.load(File)

                best_move = data_dict[self._board_to_str(board)]

                return best_move

        except (KeyError, FileNotFoundError, JSONDecodeError):

            # +9 and -9 are practically +inf and -inf
            if player == 2:
                best_move = [None, None, -9]
            else:
                best_move = [None, None, +9]


            if self._check_game_end(board) == 1:
                return [None, None, -1]
            elif self._check_game_end(board) == 2:
                return [None, None, 1]
            elif depth == 0 or self._check_game_end(board) == 3:
                return [None, None, 0]


            for x in range(3):
                for y in range(3):
                    if self.is_valid_move(x, y):
                        board[x][y] = player

                        next_player = 1 if player == 2 else 2
                        
                        score = self._find_best_move(board, next_player, depth - 1)
                        
                        board[x][y] = 0

                        score[0], score[1] = x, y

                        if player == 2:
                            if score[2] > best_move[2]:
                                best_move = score  # max value
                        else:
                            if score[2] < best_move[2]:
                                best_move = score  # min value
            
            if best_move[2]:
                try:
                    data_dict = dict()
                    with open('tiar_ai.json') as File:
                        data_dict = json.load(File)

                        data_dict[self._board_to_str(board)] = best_move

                except (FileNotFoundError, JSONDecodeError):
                    pass
                
                with open('tiar_ai.json', 'w') as File:
                    json.dump(data_dict, File, ensure_ascii=False, indent=4)                        
            
            print(f"Evaluated that the best move for {player} is {best_move}")
            return best_move

class FIAR(GameTemplate):
    def __init__(self, user, computer_ai=0):
        ai_translator = {0 : self._random_AI, 1 : self._alpha_beta_pruning_AI}

        super().__init__(user, ai_translator[computer_ai])

        self.ai_translator = {self._random_AI : "Random AI", self._alpha_beta_pruning_AI : "Alpha-Beta Pruning"}

        # The board is represented as such [[column1], [column2], ... , [column7]] each column having 6 rows
        # The left most number in a column represents the bottom most space
        self.board = [[0 for i in range(6)] for j in range(7)]

    def _random_AI(self):
        column = random.randint(0, 6) # Randint is inclusive
        
        while not self.is_valid_move(column):
            column = random.randint(0, 6) # Randint is inclusive
        
        return self.play(2, column)
    
    def _alpha_beta_pruning_AI(self):
        board = deepcopy(self.board)
        column, _ = self._maximize(board, -100, 100, 6)

        return self.play(2, column)

    # CPU maximizes
    def _maximize(self, board, alpha, beta, depth=3):
        print(f"Maximize b:{board}, a:{alpha}, b:{beta}, d:{depth}")

        # If player has won return -infinity
        if self._check_game_end(board) == 1:
            print('-infinity')
            return -1, -100
        # If cpu has won return +infinity
        elif self._check_game_end(board) == 2:
            print('+infinity')
            return -1, 100

        if depth == 0:
            return -1, self._eval_board_heuristic(2, board)

        best_move_column = -1
        value = -100

        for col in range(7):
            if self._is_valid_move_on_board(board, col):
                branch_board = deepcopy(board)
                self._make_move(2, col, branch_board)
                _, branch_value = self._minimize(branch_board, max(alpha, value), beta, depth-1)
                
                del branch_board
                
                if branch_value > value:
                    value = branch_value
                    best_move_column = col

                    # Check to prune
                    if value > beta:
                        return best_move_column, value

        return best_move_column, value

    # P1 minimizes
    def _minimize(self, board, alpha, beta, depth=3):
        # If player has won return -infinity
        if self._check_game_end(board) == 1:
            return -1, -100
        # If cpu has won return +infinity
        elif self._check_game_end(board) == 2:
            return -1, 100

        if depth == 0:
            return -1, self._eval_board_heuristic(1,board)

        best_move_column = -1
        value = 100

        for col in range(7):
            if self._is_valid_move_on_board(board, col):
                branch_board = deepcopy(board)
                self._make_move(1, col, branch_board)
                _, branch_value = self._maximize(branch_board, alpha, min(beta, value), depth-1)
                
                del branch_board
                
                if branch_value < value:
                    value = branch_value
                    best_move_column = col

                    # Check to prune
                    if value < alpha:
                        return best_move_column, value

        return best_move_column, value

    def _eval_board_heuristic(self, player, board):
        """
        Board evaluation works by counting the number of possible four in a rows each player can still make

        Should only be used on boards that haven't yet ended.
        """

        possible_wins = 0
        not_player = 1 if player == 2 else 2

        # Check all vertical possibilities
        for column in board:
            for i in range(3):
                s = {column[i], column[i+1], column[i+2], column[i+3]}
                
                if not_player in s:
                    continue
                else:
                    possible_wins += 1

        # Check all horizontal possibilities
        for row in range(6):
            for col in range(4):
                s = {board[col][row], board[col+1][row], board[col+2][row], board[col+3][row]}

                if not_player in s:
                    continue
                else:
                    possible_wins += 1

        # Check all L-diagonals
        for col in range(4):
            for row in range(3):
                s = {board[col][row], board[col+1][row+1], board[col+2][row+2], board[col+3][row+3]}
                
                if not_player in s:
                    continue
                else:
                    possible_wins += 1

        # Check all R-diagonals
        for col in range(4):
            for row in range(3,6):
                s = {board[col][row], board[col+1][row-1], board[col+2][row-2], board[col+3][row-3]}

                if not_player in s:
                    continue
                else:
                    possible_wins += 1

        if player == 1:
            return -possible_wins # Player minimizes
        else:
            return possible_wins # Cpu maximizes

    def play(self, player, col):
        if player == 1: print("IAAAAAAAAAAAAAAAAAAAAAAAAAAA")

        # If the game is already finished return winner
        if self.winner is not None:
            return self.winner

        # Make the move
        column, row = self._make_move(player, col, self.board)
                
        # Update winner
        self.winner = self._check_game_end(self.board) # If there is no winner _check_game_end returns None
        return self.winner
    
    def _make_move(self, player, col, board):
        column = board[col]
        for row in range(len(column)):
            if column[row] == 0:
                column[row] = player # column is a reference so this will mutate board

                return (col, row)

    def _check_game_end(self, board):

        # Check all vertical possibilities
        for column in board:
            for i in range(3):
                s = {column[i], column[i+1], column[i+2], column[i+3]}
                
                if len(s) == 1 and (player := s.pop()):
                    return player

        # Check all horizontal possibilities
        for row in range(6):
            for col in range(4):
                s = {board[col][row], board[col+1][row], board[col+2][row], board[col+3][row]}
                
                if len(s) == 1 and (player := s.pop()):
                    return player

        # Check all L-diagonals
        for col in range(4):
            for row in range(3):
                s = {board[col][row], board[col+1][row+1], board[col+2][row+2], board[col+3][row+3]}
                
                if len(s) == 1 and (player := s.pop()):
                    return player

        # Check all R-diagonals
        for col in range(4):
            for row in range(3,6):
                s = {board[col][row], board[col+1][row-1], board[col+2][row-2], board[col+3][row-3]}

                if len(s) == 1 and (player := s.pop()):
                    return player

        # If there is no victor
        return None


    def is_valid_move(self, column):
        return 0 in self.board[column]
    
    def _is_valid_move_on_board(self, board, column):
        return 0 in board[column]