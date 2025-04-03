import unittest
import numpy as np
from board import Board

#make some example boards. Then run tests on them with the methods I have coded up.
#maybe I can make the example boards using the methods.
#I think being able to test the methods separately may be better.

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
    
    def test_check_in_bounds(self):
        self.assertTrue(self.board.check_in_bounds(0, 0))
        self.assertTrue(self.board.check_in_bounds(18, 18))

        self.assertFalse(self.board.check_in_bounds(-1, 0))
        self.assertFalse(self.board.check_in_bounds(19, 19))
         
    def test_place_stone(self):
        self.assertTrue(self.board.place_stone(0, 0, 1))
        self.assertEqual(self.board.board[0, 0], 1)
        self.assertFalse(self.board.place_stone(0, 0, 2))

        with self.assertRaises(ValueError):
            self.board.place_stone(-1, 0, 1)
        with self.assertRaises(ValueError):
            self.board.place_stone(19, 19, 1)
        with self.assertRaises(ValueError):
            self.board.place_stone(0, 0, 3)
        with self.assertRaises(ValueError):
            self.board.place_stone(0, 0, 0)

    def test_remove_stone(self):
        self.board.place_stone(0, 0, 1)
        self.assertTrue(self.board.remove_stone(0, 0))
        self.assertEqual(self.board.board[0, 0], 0)
        self.assertFalse(self.board.remove_stone(0, 0))

        with self.assertRaises(ValueError):
            self.board.remove_stone(-1, 0)
        with self.assertRaises(ValueError):
            self.board.remove_stone(19, 19)

    def test_liberties_check(self):
        self.board.place_stone(0, 0, 1)
        self.assertEqual(self.board.liberties_check(0, 0), 2)

        self.board.place_stone(10, 0, 1)
        self.assertEqual(self.board.liberties_check(10, 0), 3)

        self.board.place_stone(10, 10, 1)
        self.assertEqual(self.board.liberties_check(10, 10), 4)

        self.board.place_stone(10,11,1)
        self.board.place_stone(10,12,1)
        self.board.place_stone(11,11,1)
        self.assertEqual(self.board.liberties_check(10, 12), 8)
        self.board.place_stone(10,9,2)
        self.board.place_stone(9,10,2)
        self.board.place_stone(9,11,2)
        self.board.place_stone(9,12,2)
        self.board.place_stone(10,13,2)
        self.assertEqual(self.board.liberties_check(10, 12), 3)
        self.assertEqual(self.board.liberties_check(9, 10), 5)

        with self.assertRaises(ValueError):
            self.board.liberties_check(-1, 0)
        with self.assertRaises(ValueError):
            self.board.liberties_check(19, 19)

    def test_opposite_colour(self):
        self.assertEqual(self.board.opposite_colour(1), 2)
        self.assertEqual(self.board.opposite_colour(2), 1)
        self.assertEqual(self.board.opposite_colour(0), 0)

if __name__ == '__main__':
    unittest.main()