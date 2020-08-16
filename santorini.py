#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from random import randrange, sample, shuffle
from collections import Counter, defaultdict

DIRS = [(1,1),(1,0),(1,-1),(0,1),(0,-1),(-1,1),(-1,0),(-1,-1)]
PIECES = ['A', 'B']
OPPONENT = 'O'
EMPTY = ' '
MAX_HEIGHT = 4

### AI Helper Methods ###

class IllegalState(Exception):
    pass

def unoccupiedSpaces(pieces):
    return [(x,y) for x in range(5) for y in range(5) if pieces[y][x] == EMPTY]

def findPiecePos(pieces, pieceName):
    for y in range(5):
        for x in range(5):
            if pieces[y][x] == pieceName:
                return x, y
    print(pieces)
    print(pieceName)
    raise IllegalState('Can\'t find piece on board.')

def validMoves(heights, pieces, x, y):
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

### AI Algorithms ###

def randomPlayer(heights, pieces, setUp):
    if setUp:
        return randrange(5), randrange(5)
    return sample(PIECES, 1)[0], sample(DIRS, 1)[0], sample(DIRS, 1)[0]

def randomPlayerWithValidation(heights, pieces, setUp):
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

def myGreatPlayer(heights, pieces, setUp):
    if setUp:
        if pieces[2][2] == EMPTY:
            return 2, 2
        return sample(unoccupiedSpaces(pieces), 1)[0]
    pieceNames = list(PIECES)
    for pieceName in pieceNames:
        x, y = findPiecePos(pieces, pieceName)
        moveDirs = validMoves(heights, pieces, x, y)
        for moveDir in moveDirs:
            destX, destY = x + moveDir[0], y + moveDir[1]
            if heights[destY][destX] == MAX_HEIGHT - 1:
                return pieceName, moveDir, DIRS[0]
    return randomPlayerWithValidation(heights, pieces, setUp)

ALL_PLAYERS = [randomPlayer, randomPlayerWithValidation, myGreatPlayer]

### Game Simulator Code ###

class IllegalMove(Exception):
    pass

def displayBoard(heights, pieces):
    print('+' + '-'*15 + '+')
    for y in range(5):
        lines = defaultdict(str)
        for x in range(5):
            heightChar = ' .+#@'[heights[y][x]]
            pieceChar = {EMPTY: EMPTY, (0,0): 'a', (0,1): 'b', (1,0): 'y', (1,1): 'z'}[pieces[y][x]]
            lines[0] += heightChar * 3
            lines[1] += heightChar  + pieceChar + heightChar
            lines[2] += heightChar * 3
        for i in range(3):
            print('|' + lines[i] + '|')
    print('+' + '-'*15 + '+\n')
            

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
    pieces[y][x] = EMPTY
    destX, destY = x + moveDir[0], y + moveDir[1]
    if destX < 0 or destX > 4 or destY < 0 or destY > 4:
        raise IllegalMove('Trying to move off board')
    if pieces[destY][destX] != EMPTY:
        raise IllegalMove('Destination not empty')
    if heights[destY][destX] > heights[y][x] + 2:
        raise IllegalMove('Trying to jump too high')
    pieces[destY][destX] = piece
    return destX, destY

def build(heights, pieces, x, y, buildDir):
    destX, destY = x + buildDir[0], y + buildDir[1]
    if destX < 0 or destX > 4 or destY < 0 or destY > 4:
        raise IllegalMove('Trying to build off board')
    if pieces[destY][destX] != EMPTY:
        raise IllegalMove('Need empty destination to build')
    if heights[destY][destX] == MAX_HEIGHT:
        raise IllegalMove('Space already at max height')
    heights[destY][destX] += 1

def playGame(players):
    heights = [[0] * 5 for i in range(5)]
    pieces = [[EMPTY] * 5 for i in range(5)]
    
    try:
        # Place pieces on the board.
        for playerIndex, player in enumerate(players):
            for pieceNumber in range(2):
                x, y = player(heights, convertPieces(playerIndex, pieces), True)
                if pieces[y][x] != EMPTY:
                    return 1 - playerIndex
                pieces[y][x] = (playerIndex, pieceNumber)
        
        # Play the game (the AI player can pick a piece to move, a move direction and a build direction).
        turnNumber = 0
        while True:
            for playerIndex, player in enumerate(players):
                pieceName, moveDir, buildDir = player(heights, convertPieces(playerIndex, pieces), False)
                try:
                    x, y = findPiece(pieces, playerIndex, pieceName)
                    x, y = move(heights, pieces, x, y, moveDir)
                    if heights[y][x] == MAX_HEIGHT - 1:
                        return playerIndex
                    build(heights, pieces, x, y, buildDir)
                except IllegalMove:
                    return 1 - playerIndex
            turnNumber += 1
        return 0
    finally:
        # Print end game position.
        displayBoard(heights, pieces)
        pass

score = Counter()

for gameIndex in range(100):
    playerIndexes = [randrange(len(ALL_PLAYERS)), randrange(len(ALL_PLAYERS))]
    players = [ALL_PLAYERS[playerIndexes[0]], ALL_PLAYERS[playerIndexes[1]]]
    
    winner = playGame(players)
    score[playerIndexes[winner]] += 1
for playerIndex, score in score.most_common():
    print('{:5d} {}'.format(score, ALL_PLAYERS[playerIndex].__name__))
