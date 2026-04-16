import numpy as np
import copy
import warnings
import random
import time
import rclpy  # Changed from rospy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Vector3

# == CONSTANTS =================================================================
V  = np.array([[1],[1],[1]], dtype = 'int')
VT = V.T
STATES = ['ERROR', 'idling', 'going to target', 'going to idling', 'ready to write', 'writing', 'done writing']
IDLE_POS = (-1,-1)
VIS2PHYS = {'.':0, 'X':1, 'O':2}
GAME_OUTCOMES = {'normal': 0.0, 'draw': 1.0, 'X win': 2.0, 'O win': 3.0, 'ERROR': 4.0}
GRID_POSITION = {
    '0' : {'0': 0.0, '1': 1.0, '2': 2.0},
    '1' : {'0': 3.0, '1': 4.0, '2': 5.0},
    '2' : {'0': 6.0, '1': 7.0, '2': 8.0},
    'rest' : 9.0
}
DEBUGGING = True
VERBOSITY = True

# == CLASSES ===================================================================
class BoardManager:
    def __init__(self):
        self.NAME = "board"
        self.current_board = np.zeros([3,3], dtype="int64")
        self.propose_board = np.zeros([3,3], dtype="int64")
        if VERBOSITY:
            print(f"{self.NAME}: board instantiated!")

    def _there_is_a_line(self, single_chip_board):
        B = single_chip_board.astype('int')
        rows = (B @ V).flatten()
        cols = (VT @ B).flatten()
        diag = [np.trace(B)]
        adig = [np.trace(np.fliplr(B))]
        res = [rows, cols, diag, adig]
        results = [item for arr in res for item in arr]
        return True if 3 in results else False

    def _propose_board_is_valid(self, X_move=False, O_move=False):
        identical_cells_bool = (self.current_board == self.propose_board)
        if np.sum(identical_cells_bool) == 8:
            curr_empties = int(np.sum(self.current_board == 0))
            prop_empties = int(np.sum(self.propose_board == 0))
            if prop_empties - curr_empties == -1:
                curr_sum = int(np.sum(self.current_board))
                prop_sum = int(np.sum(self.propose_board))
                if X_move:
                    return prop_sum - curr_sum == 1
                else:
                    return prop_sum - curr_sum == 2
        return False

    def _num_2_char(self, num):
        match int(num):
            case 0: return '•'
            case 1: return 'X'
            case 2: return 'O'
            case _: raise ValueError(f"{self.NAME}: _num_2_char() got confused...")

    def O_has_won(self): return self._there_is_a_line(self.current_board == 2)

    def X_has_won(self): return self._there_is_a_line(self.current_board == 1)

    def its_a_draw(self): return not 0 in self.current_board

    def update_propose_board(self, new_board):
        self.propose_board = np.array(new_board, dtype="int64")

    def valid_propose_board_X_move(self):
        if self._propose_board_is_valid(X_move=True):
            self.current_board = np.copy(self.propose_board)
            self.propose_board = np.zeros([3,3], dtype="int64")
            return True
        self.propose_board = np.zeros([3,3], dtype="int64")
        return False

    def valid_propose_board_O_move(self):
        if self._propose_board_is_valid(O_move=True):
            self.current_board = np.copy(self.propose_board)
            self.propose_board = np.zeros([3,3], dtype="int64")
            return True
        self.propose_board = np.zeros([3,3], dtype="int64")
        return False

    def managed_to_rebuild_broken_board(self, newest_move_is_O=True):
        cb_10 = self.current_board.astype('bool').astype('int')
        pb_10 = self.propose_board.astype('bool').astype('int')
        diff_10 = pb_10 - cb_10
        has_8_zeros = len([i for i in list(diff_10.flatten()) if i == 0]) == 8
        if not has_8_zeros: return False
        mult = 2 if newest_move_is_O else 1
        self.current_board += mult * diff_10
        self.propose_board = np.zeros([3,3], dtype="int64")
        return True

    def display_current_board(self):
        output_full = ""
        output_snippets = ["+-+-+-+"]
        for row in self.current_board:
            output_line = "|"
            for col in row:
                output_line += self._num_2_char(col) + "|"
            output_snippets.append(output_line)
            output_snippets.append("+-+-+-+")
        for snippet in output_snippets: output_full += "    " + snippet + "\n"
        print("\n" + output_full + "\n")

    def retrieve_X_only_string(self):
        X_list = ['X' if i else ' ' for i in list((self.current_board == 1).flatten())]
        return ''.join(X_list)

class EndEffector:
    def __init__(self):
        self.NAME = "end-effector"
        self.position = IDLE_POS
        self.target = IDLE_POS
        self.state = 1 # Idling
    def initialize_self(self):
        print(f"{self.NAME}: initialized.")

class GameEngine(Node): # Now inherits from Node
    def __init__(self, board_manager):
        super().__init__("game_engine_node")
        self.board_manager = board_manager
        self.visual_game_state = "         "
        # ROS 2 Publisher & Subscriber
        self.pub_grid_position = self.create_publisher(Vector3, "/grid_position", 10)
        self.sub_state = self.create_subscription(String, "/tictactoe/state", self.changed_cells, 10)
        self.physical_board = np.zeros([3,3], dtype="int64")
        self.grid_position_staging = Vector3()
        self.grid_position_staging.x = GRID_POSITION['rest']
        self.grid_position_staging.y = GAME_OUTCOMES['normal']
        self.grid_position_staging.z = 0.0
        self._initial_move()

    def _initial_move(self):
        valid_move_committed = False
        while not valid_move_committed:
            next_board, next_move = selectNextMove(self.board_manager)
            examineBoard(self.board_manager, next_board)
            if self.board_manager.valid_propose_board_X_move(): 
                valid_move_committed = True
                self.grid_position_staging.x = GRID_POSITION[str(next_move[0])][str(next_move[1])]
                print("Robot will make the first move:")
                self.board_manager.display_current_board()
        self.pub_grid_position.publish(self.grid_position_staging)

    def changed_cells(self, msg):
        self.grid_position_staging.x = GRID_POSITION['rest']
        self.grid_position_staging.y = GAME_OUTCOMES['normal']
        only_Xs = self.board_manager.retrieve_X_only_string()
        visual_raw = msg.data
        visual_Os_str = ''.join(['O' if i == 'O' else ' ' for i in visual_raw])
        self.visual_game_state = ''
        for x, o in zip(only_Xs, visual_Os_str):
            if x == 'X': self.visual_game_state += 'X'
            elif o == 'O': self.visual_game_state += 'O'
            else: self.visual_game_state += '.'
        self.physical_board = np.array([VIS2PHYS[i] for i in self.visual_game_state], dtype="int64").reshape(3,3)
        examineBoard(self.board_manager, self.physical_board)
        if not self.board_manager.valid_propose_board_O_move():
            if not rebuildBrokenBoard(self.board_manager, self.physical_board, True):
                self.grid_position_staging.y = GAME_OUTCOMES['ERROR']
                self.pub_grid_position.publish(self.grid_position_staging)
                return
        if self.board_manager.O_has_won():
            self.grid_position_staging.y = GAME_OUTCOMES['O win']
        elif self.board_manager.its_a_draw():
            self.grid_position_staging.y = GAME_OUTCOMES['draw']
        else:
            # Plan X Move
            next_board, next_move = selectNextMove(self.board_manager)
            examineBoard(self.board_manager, next_board)
            if self.board_manager.valid_propose_board_X_move():
                self.grid_position_staging.x = GRID_POSITION[str(next_move[0])][str(next_move[1])]
                if self.board_manager.X_has_won(): self.grid_position_staging.y = GAME_OUTCOMES['X win']
                #elif self.board_manager.its_a_draw(): self.grid_position_staging.y = GAME_OUTCOMES['draw']
        self.pub_grid_position.publish(self.grid_position_staging)

# == FUNCTIONS =================================================================
def examineBoard(board_manager, physical_board):
    board_manager.update_propose_board(physical_board)

def rebuildBrokenBoard(board_manager, physical_board, newest_move_is_O=True):
    examineBoard(board_manager, physical_board)
    return board_manager.managed_to_rebuild_broken_board(newest_move_is_O)

def selectNextMove(board_manager):
    out_board = np.copy(board_manager.current_board)
    empties = list(zip(*np.where(out_board == 0)))
    next_move = empties[random.randint(0, len(empties)-1)]
    out_board[next_move] = 1
    return (out_board, next_move)

# == MAIN LOOP =================================================================
def main(args=None):
    rclpy.init(args=args)
    board_manager = BoardManager()
    end_effector = EndEffector()
    end_effector.initialize_self()
    print("Tic Tac Toe Engine Started!")
    board_manager.display_current_board()
    node = GameEngine(board_manager)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
