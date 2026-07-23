import unittest
import numpy as np
from game_logic.game import Game

#make some example boards. Then run tests on them with the methods I have coded up.
#maybe I can make the example boards using the methods.
#I think being able to test the methods separately may be better.

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Game()
    
    def test_check_in_bounds(self):
        self.assertTrue(self.board.check_in_bounds((0, 0)))
        self.assertTrue(self.board.check_in_bounds((18, 18)))

        self.assertFalse(self.board.check_in_bounds((-1, 0)))
        self.assertFalse(self.board.check_in_bounds((19, 19)))
         
    def test_place_stone(self):
        self.assertTrue(self.board.place_stone((0, 0), 1))
        self.assertEqual(self.board.board[0, 0], 1)
        self.assertFalse(self.board.place_stone((0, 0), 2))

        with self.assertRaises(ValueError):
            self.board.place_stone((-1, 0), 1)
        with self.assertRaises(ValueError):
            self.board.place_stone((19, 19), 1)
        with self.assertRaises(ValueError):
            self.board.place_stone((0, 0), 3)
        with self.assertRaises(ValueError):
            self.board.place_stone((0, 0), 0)

    def test_remove_stone(self):
        self.board.place_stone((0, 0), 1)
        self.assertTrue(self.board.remove_stones((0, 0)))
        self.assertEqual(self.board.board[0, 0], 0)
        self.assertFalse(self.board.remove_stones((0, 0)))

        with self.assertRaises(ValueError):
            self.board.remove_stones((-1, 0))
        with self.assertRaises(ValueError):
            self.board.remove_stones((19, 19))

if __name__ == '__main__':
    unittest.main()