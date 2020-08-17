#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from random import randrange, sample, shuffle
from collections import Counter, defaultdict
from itertools import combinations

# Constants that can be changed when investigating players.
NUMBER_OF_GAMES = 100
OUTPUT_ALL_POSITIONS = False

# Constants that probably shouldn't be changed.
DIRS = [(1,1),(1,0),(1,-1),(0,1),(0,-1),(-1,1),(-1,0),(-1,-1)]
PIECES = ['A', 'B']
OPPONENT = 'O'
EMPTY = ' '
MAX_HEIGHT = 4

### AI Helper Methods ###

class IllegalState(Exception):
    pass

def unoccupiedSpaces(pieces):
    """Return a list of the coordinates of unoccupied spaces."""
    return [(x,y) for x in range(5) for y in range(5) if pieces[y][x] == EMPTY]

def findPiecePos(pieces, pieceName):
    """Return the coordinates of a piece by name. If 'O' is given then just one of the two opponenets will be returned."""
    for y in range(5):
        for x in range(5):
            if pieces[y][x] == pieceName:
                return x, y
    print(pieces)
    print(pieceName)
    raise IllegalState('Can\'t find piece on board.')

def getOpponentCoordinates(pieces):
    """Return a list containing the coordinates of the opponent's pieces."""
    opponentsCoordinates = []
    for y in range(5):
        for x in range(5):
            if pieces[y][x] == OPPONENT:
                opponentsCoordinates.append((x, y))
    return opponentsCoordinates

def validMoves(heights, pieces, x, y):
    """Return a list of the directions that are valid for moving."""
    options = []
    for moveDir in DIRS:
        destX, destY = x + moveDir[0], y + moveDir[1]
        if destX < 0 or destX > 4 or destY < 0 or destY > 4:
            continue
        if pieces[destY][destX] != EMPTY:
            continue
        if heights[destY][destX] > heights[y][x] + 2:
            continue
        options.append(moveDir)
    return options

def validBuilds(heights, pieces, x, y, pieceName):
    """Return a list of the directions that are valid for building."""
    options = []
    for buildDir in DIRS:
        destX, destY = x + buildDir[0], y + buildDir[1]
        if destX < 0 or destX > 4 or destY < 0 or destY > 4:
            continue
        if pieces[destY][destX] not in [EMPTY, pieceName]:
            continue
        if heights[destY][destX] == MAX_HEIGHT:
            continue
        options.append(buildDir)
    return options

def adjacentPieces(pieces, x, y):
    """Return a list of coordinates adjacent to a location that contain pieces."""
    out = []
    for moveDir in DIRS:
        destX, destY = x + moveDir[0], y + moveDir[1]
        if destX < 0 or destX > 4 or destY < 0 or destY > 4:
            continue
        if pieces[destY][destX] != EMPTY:
            out.append((destX, destY))
    return out

def validMovesByHeight(heights, pieces, x, y):
    """Return a map from a height to a list of the options to get to that height.
    
    Each entry in the return list will have the direction and the coordinates - for example:
        {
            # height: [(direction, destination), ...]
            0: [((1,0), (2,3)), ((1,1), (2,4))],
            2: [(-1, 0), (0,3)]
        }"""
    out = defaultdict(list)
    for targetHeight in reversed(range(MAX_HEIGHT)):
        if heights[y][x] < targetHeight - 1:
            continue
        moveDirs = validMoves(heights, pieces, x, y)
        for moveDir in moveDirs:
            destX, destY = x + moveDir[0], y + moveDir[1]
            if heights[destY][destX] == targetHeight:
                out[targetHeight].append((moveDir, (destX, destY)))
    return out

### AI Algorithms ###

def randomPlayer(heights, pieces, setUp):
    """A player that tries to make all moves at random, without even check they are valid."""
    if setUp:
        return randrange(5), randrange(5)
    return sample(PIECES, 1)[0], sample(DIRS, 1)[0], sample(DIRS, 1)[0]

def randomPlayerWithValidation(heights, pieces, setUp):
    """A player that tries to move at random, but which only picks from valid moves."""
    if setUp:
        return sample(unoccupiedSpaces(pieces), 1)[0]
    pieceNames = list(PIECES)
    shuffle(pieceNames)
    for pieceName in pieceNames:
        x, y = findPiecePos(pieces, pieceName)
        moveDirs = validMoves(heights, pieces, x, y)
        shuffle(moveDirs)
        for moveDir in moveDirs:
            buildDirs = validBuilds(heights, pieces, x + moveDir[0], y + moveDir[1], pieceName)
            if len(buildDirs) > 0:
                return pieceName, moveDir, sample(buildDirs, 1)[0]
    # No valid moves.
    return None, None, None

def tryToClimb(heights, pieces, setUp):
    """A player that tries to move to the highest space available. It also tries to start near the middle of the board."""
    if setUp:
        if pieces[2][2] == EMPTY:
            return 2, 2
        dest = (0, 0)
        while dest[0] in [0, 4] or dest[1] in [0, 4]:
            dest = sample(unoccupiedSpaces(pieces), 1)[0]
        return dest
    for targetHeight in reversed(range(MAX_HEIGHT)):
        for pieceName in PIECES:
            x, y = findPiecePos(pieces, pieceName)
            if heights[y][x] < targetHeight - 1:
                continue
            moveDirs = validMoves(heights, pieces, x, y)
            for moveDir in moveDirs:
                destX, destY = x + moveDir[0], y + moveDir[1]
                if heights[destY][destX] == targetHeight:
                    buildDirs = validBuilds(heights, pieces, x + moveDir[0], y + moveDir[1], pieceName)
                    if len(buildDirs) == 0:
                        # Ignore situations with no valid builds if we've won.
                        if heights[destY][destX] == MAX_HEIGHT - 1:
                            return pieceName, moveDir, DIRS[0]
                        continue
                    return pieceName, moveDir, buildDirs[0]
    return randomPlayerWithValidation(heights, pieces, setUp)

def buildAway(heights, pieces, setUp):
    """A player that tries to climb and that tries to build where the opponent can't climb to."""
    if setUp:
        return tryToClimb(heights, pieces, setUp)
    for targetHeight in reversed(range(MAX_HEIGHT)):
        for pieceName in PIECES:
            x, y = findPiecePos(pieces, pieceName)
            movesByHeight = validMovesByHeight(heights, pieces, x, y)
            for moveDir, dest in movesByHeight[targetHeight]:
                buildDirs = validBuilds(heights, pieces, dest[0], dest[1], pieceName)
                # Don't worry about the build direction if we've won.
                if heights[dest[1]][dest[0]] == MAX_HEIGHT - 1:
                    return pieceName, moveDir, DIRS[0]
                for buildDir in buildDirs:
                    buildDestX, buildDestY = dest[0] + buildDir[0], dest[1] + buildDir[1]
                    if 'O' not in adjacentPieces(pieces, buildDestX, buildDestY):
                        return pieceName, moveDir, buildDir
    return tryToClimb(heights, pieces, setUp)

def defensivePlayer(heights, pieces, setUp):
    """A defensive player that tries to stop the opponent winning."""
    if setUp:
        return tryToClimb(heights, pieces, setUp)
    movesByHeight = {}
    for pieceName in PIECES:
        x, y = findPiecePos(pieces, pieceName)
        movesByHeight[pieceName] = validMovesByHeight(heights, pieces, x, y)
        # Check for any winning move.
        for moveDir, dest in movesByHeight[pieceName][MAX_HEIGHT - 1]:
            return pieceName, moveDir, DIRS[0]
    # Check for opponent's winning move.
    opponentCoordinates = getOpponentCoordinates(pieces)
    for x, y in opponentCoordinates:
        opponentsMoves = validMovesByHeight(heights, pieces, x, y)
        # Try to prevent any winning move.
        for _, opponentWinDest in opponentsMoves[MAX_HEIGHT - 1]:
            for pieceName in PIECES:
                x, y = findPiecePos(pieces, pieceName)
                moveDirs = validMoves(heights, pieces, x, y)
                for moveDir in moveDirs:
                    buildDirs = validBuilds(heights, pieces, x + moveDir[0], y + moveDir[1], pieceName)
                    for buildDir in buildDirs:
                        if (x + moveDir[0] + buildDir[0], y + moveDir[1] + buildDir[1]) == opponentWinDest:
                            return pieceName, moveDir, buildDir
    return buildAway(heights, pieces, setUp)

ALL_PLAYERS = [randomPlayer, randomPlayerWithValidation, tryToClimb, buildAway, defensivePlayer]

### Game Simulator Code ###

class IllegalMove(Exception):
    pass

def displayBoard(heights, pieces):
    print('+-0--1--2--3--4-+')
    for y in range(5):
        lines = defaultdict(str)
        for x in range(5):
            heightChar = ' .+#@'[heights[y][x]]
            pieceChar = {EMPTY: EMPTY, (0,0): 'a', (0,1): 'b', (1,0): 'y', (1,1): 'z'}[pieces[y][x]]
            lines[0] += heightChar * 3
            lines[1] += heightChar  + pieceChar + heightChar
            lines[2] += heightChar * 3
        borders = '|{}|'.format(y)
        for i in range(3):
            borderChar = borders[i]
            print(borderChar + lines[i] + borderChar)
    print('+-0--1--2--3--4-+')
            

def convertPieces(playerIndex, pieces):
    outPieces = [[] for i in range(5)]
    for y in range(5):
        for x in range(5):
            piece = pieces[y][x]
            if piece == EMPTY:
                outPieces[y].append(EMPTY)
            elif piece[0] == playerIndex:
                outPieces[y].append(PIECES[piece[1]])
            else:
                outPieces[y].append(OPPONENT)
    return outPieces

def findPiece(pieces, playerIndex, pieceName):
    pieceIndex = PIECES.index(pieceName)
    for y in range(5):
        for x in range(5):
            if pieces[y][x] == (playerIndex, pieceIndex):
                return (x, y)
    raise IllegalMove('Piece not found')

def move(heights, pieces, x, y, moveDir):
    piece = pieces[y][x]
    destX, destY = x + moveDir[0], y + moveDir[1]
    if destX < 0 or destX > 4 or destY < 0 or destY > 4:
        raise IllegalMove('Trying to move off board. {} tried to move to {}'.format((x, y), (destX, destY)))
    if pieces[destY][destX] != EMPTY:
        raise IllegalMove('Destination not empty. {} tried to move to {}'.format((x, y), (destX, destY)))
    if heights[destY][destX] > heights[y][x] + 2:
        raise IllegalMove('Trying to jump too high. {} tried to move to {}'.format((x, y), (destX, destY)))
    pieces[y][x] = EMPTY
    pieces[destY][destX] = piece
    return destX, destY

def build(heights, pieces, x, y, buildDir):
    destX, destY = x + buildDir[0], y + buildDir[1]
    if destX < 0 or destX > 4 or destY < 0 or destY > 4:
        raise IllegalMove('Trying to build off board')
    if pieces[destY][destX] != EMPTY:
        raise IllegalMove('Need empty destination to build. Actually ({}, {}) had {}'.format(destX, destY, pieces[destY][destX]))
    if heights[destY][destX] == MAX_HEIGHT:
        raise IllegalMove('Space already at max height')
    heights[destY][destX] += 1

def playGame(players):
    heights = [[0] * 5 for i in range(5)]
    pieces = [[EMPTY] * 5 for i in range(5)]
    
    winner = None
    try:
        # Place pieces on the board.
        for playerIndex, player in enumerate(players):
            for pieceNumber in range(2):
                x, y = player(heights, convertPieces(playerIndex, pieces), True)
                if pieces[y][x] != EMPTY:
                    winner = 1 - playerIndex
                    return winner
                pieces[y][x] = (playerIndex, pieceNumber)
        
        # Play the game (the AI player can pick a piece to move, a move direction and a build direction).
        turnNumber = 0
        while True:
            for playerIndex, player in enumerate(players):
                if OUTPUT_ALL_POSITIONS:
                    print('Turn {}, {} ({}) to move:'.format(turnNumber, players[playerIndex].__name__, ['ab', 'yz'][playerIndex]))
                    displayBoard(heights, pieces)
                    pass
                pieceName, moveDir, buildDir = player(heights, convertPieces(playerIndex, pieces), False)
                try:
                    x, y = findPiece(pieces, playerIndex, pieceName)
                    x, y = move(heights, pieces, x, y, moveDir)
                    if heights[y][x] == MAX_HEIGHT - 1:
                        winner = playerIndex
                        return winner
                    build(heights, pieces, x, y, buildDir)
                except IllegalMove as e:
                    print(e.args[0])
                    winner = 1 - playerIndex
                    return winner
            turnNumber += 1
        return 0
    finally:
        # Print end game position.
        loser = 1 - winner
        print('{} ({}) beats {} ({})'.format(players[winner].__name__, ['ab', 'yz'][winner], players[loser].__name__, ['ab', 'yz'][loser]))
        displayBoard(heights, pieces)
        print('\n')
        pass

score = Counter()

for playerPairing in combinations(range(len(ALL_PLAYERS)), 2):
    playerIndexes = list(playerPairing)
    for gameIndex in range(NUMBER_OF_GAMES):
        shuffle(playerIndexes)
        players = [ALL_PLAYERS[playerIndexes[0]], ALL_PLAYERS[playerIndexes[1]]]
        
        winner = playGame(players)
        loser = 1 - winner
        score[(playerIndexes[winner], playerIndexes[loser])] += 1

for playerIndexes, score in score.most_common():
    print('{:5d} {} beats {}'.format(score, ALL_PLAYERS[playerIndexes[0]].__name__, ALL_PLAYERS[playerIndexes[1]].__name__))
