import unittest
from santorini import *

class SantoriniTest(unittest.TestCase):
    def setUpPieces(self, a, b, o0, o1):
        pieces = [[EMPTY] * 5 for i in range(5)]
        pieces[a[1]][a[0]] = PIECES[0]
        pieces[b[1]][b[0]] = PIECES[1]
        pieces[o0[1]][o0[0]] = OPPONENT
        pieces[o1[1]][o1[0]] = OPPONENT
        return pieces

    def setUpPieces(self, piecesStrs):
        pieces = [[] for i in range(5)]
        for y in range(5):
            for x in range(5):
                pieces[y].append(piecesStrs[y][x])
        return pieces
    
    def setUpHeights(self, heightsStrs):
        heights = [[] for i in range(5)]
        for y in range(5):
            for x in range(5):
                heights[y].append(int(heightsStrs[y][x]))
        return heights

    def testUnoccupiedSpaces(self):
        pieces = self.setUpPieces(['  O  ', ' A   ', ' O   ', '     ', '   B '])
        # Call the method under test.
        unoccupied = unoccupiedSpaces(pieces)
        
        expected = set([(0, 0), (1, 0),         (3, 0), (4, 0),
                        (0, 1),         (2, 1), (3, 1), (4, 1),
                        (0, 2),         (2, 2), (3, 2), (4, 2),
                        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
                        (0, 4), (1, 4), (2, 4),         (4, 4)])
        self.assertEqual(set(unoccupied), expected)

    def testFindPiecePos(self):
        pieces = self.setUpPieces(['  O  ', ' A   ', ' O   ', '     ', '   B '])
        self.assertEqual(findPiecePos(pieces, PIECES[1]), (3,4))
        
    def testGetOpponentCoordinates(self):
        pieces = self.setUpPieces(['  O  ', ' A   ', ' O   ', '     ', '   B '])
        opponentPieces = getOpponentCoordinates(pieces)
        self.assertEqual(set(opponentPieces), set([(2,0), (1,2)]))
    
    def testValidMovesDifferentHeights(self):
        """Test the valid moves function near the edge of the board with some squares blocked by height."""
        pieces = self.setUpPieces(['  O  ', ' A   ', ' O   ', '     ', '   B '])
        heights = self.setUpHeights(['00000', '00000', '00000', '00012', '00314'])
        # Call the method under test.
        moves = validMoves(heights, pieces, 3, 4)
        
        self.assertEqual(set(moves), set([(-1, -1), (0, -1), (1, -1)]))

    def testValidMovesBlockingPieces(self):
        """Test the valid moves function when some squares are blocked by other pieces."""
        pieces = self.setUpPieces([' BO  ', ' A   ', ' O   ', '     ', '     '])
        heights = self.setUpHeights(['00000', '00000', '00000', '00000', '00000'])
        # Call the method under test.
        moves = validMoves(heights, pieces, 1, 1)
        
        self.assertEqual(set(moves), set([(-1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]))

    def testValidBuildsDifferentHeights(self):
        """Test how heights affect where the player can build."""
        pieces = self.setUpPieces(['  O  ', ' A   ', ' O   ', '     ', '   B '])
        heights = self.setUpHeights(['00000', '00000', '00000', '00012', '00314'])
        # Call the method under test.
        builds = validBuilds(heights, pieces, 3, 4, 'B')
        
        self.assertEqual(set(builds), set([(-1, -1), (0, -1), (1, -1), (-1, 0)]))

    def testValidBuildsBlockingPieces(self):
        """Test how other pieces affect where the player can build (in particular B should be able to build where B was)."""
        pieces = self.setUpPieces(['OB   ', ' A   ', 'O    ', '     ', '     '])
        heights = self.setUpHeights(['00000', '00000', '00000', '00000', '00000'])
        # Call the method under test.
        builds = validBuilds(heights, pieces, 0, 1, 'B')
        
        self.assertEqual(set(builds), set([(1, -1), (1, 1)]))

    def DtestNegamaxPlayerDepth0Win(self):
        pieces = self.setUpPieces(['OBO  ', ' A   ', '     ', '     ', '     '])
        heights = self.setUpHeights(['02200', '30100', '33333', '33333', '33333'])
        pieceName, moveDir, buildDir = negamaxPlayer(heights, pieces, False, startDepth=4)
        self.assertEqual(pieceName, 'B')
        self.assertEqual(moveDir, (-1, 1))

    def DtestNegamaxPlayerDepth0PreventLoss(self):
        pieces = self.setUpPieces(  ['AO   ', ' OB  ', '     ', '     ', '     '])
        heights = self.setUpHeights(['02200', '30100', '30333', '33333', '33333'])
        pieceName, moveDir, buildDir = negamaxPlayer(heights, pieces, False, startDepth=4)
        self.assertEqual(pieceName, 'B')
        self.assertEqual(moveDir, (-1, 1))
        self.assertEqual(buildDir, (-1, -1))

    def testNegamaxScoringWinInOne(self):
        node = ([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 2, 0, 2, 4], [0, 2, 3, 0, 4]],
                [['B', ' ', ' ', ' ', ' '],
                 [' ', ' ', ' ', ' ', ' '], 
                 [' ', ' ', ' ', ' ', ' '], 
                 [' ', ' ', ' ', 'O', ' '], 
                 [' ', 'A', ' ', 'O', ' ']], -1)
    
        self.assertEqual(negamax(node, 0, -1000, 1000, -1), -2)
        for depth in range(1, 5):
            self.assertEqual(negamax(node, depth, -1000, 1000, -1), 1000)

    def testNegamaxScoringLoseInTwo(self):
        node = ([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 2, 0, 3, 4], [0, 2, 2, 0, 4]], 
                [['B', ' ', ' ', ' ', ' '], 
                 [' ', ' ', ' ', ' ', ' '], 
                 [' ', ' ', ' ', ' ', ' '], 
                 [' ', ' ', 'O', ' ', ' '], 
                 [' ', 'A', 'O', ' ', ' ']], -1)
        
        self.assertEqual(negamax(node, 0, -1000, 1000, -1), -4)
        self.assertEqual(negamax(node, 1, -1000, 1000, -1), -2)
        self.assertEqual(negamax(node, 2, -1000, 1000, -1), -1000)
        self.assertEqual(negamax(node, 3, -1000, 1000, -1), -1000)
        self.assertEqual(negamax(node, 4, -1000, 1000, -1), -1000)
        
    def testNegamaxPlayerDepth1Win(self):
        pieces = self.setUpPieces(['O    ', 
                                   '     ', 
                                   '     ', 
                                   '     ', 
                                   ' OAB '])
        heights = self.setUpHeights(['00000', 
                                     '00000', 
                                     '00000', 
                                     '02024', 
                                     '02204'])
        pieceName, moveDir, buildDir = negamaxPlayer(heights, pieces, False, startDepth=2)

        self.assertEqual(pieceName, 'B')
        self.assertEqual(moveDir, (-1, -1))
        self.assertEqual(buildDir, (1, 0))

if __name__ == '__main__':
    unittest.main()
