import sys
import random
import copy
import more_itertools
import time

#Shamlessly taken from simpletilegame.py
def parse_input_file(input_file):
    board = []  # 2D array
    pieces = {} # hashmap of 2D arrays
    key_count = -1
    with open(input_file, 'r') as f:
        line = f.readline().strip('\n')
        #print(line)
        while line:
            key_count += 1
            curr_fig = []
            while line != "":
                curr_fig.append(list(line))
                line = f.readline().strip('\n')
            #print(curr_fig)
            line = f.readline().strip('\n')
            pieces[key_count] = curr_fig
        board = pieces.pop(key_count)
        #print(board)
    f.close()
    return board, pieces

# Prints board. Mainly for debugging purposes
def print_board(board):
    for line in board:
        for char in line:
            print(char, end="")
        print()
    print()

# Prints piece. Mainly for debugging purposes
def print_piece(piece):
    for line in piece:
        for char in line:
            print(char, end="")
        print()
    print()

# Takes in a piece and a number of iterations. 
# Returns the piece rotated 90 degrees to the right iteration times.
def rotate_piece(piece, times):
    finalPiece = piece
    for i in range(times%4):
        newPiece = []
        height = len(finalPiece)
        length = len(finalPiece[0])
        for i in range(length):
            newPieceLine = []
            for j in range(height):
                newPieceLine.append(finalPiece[height-j-1][i])
            newPiece.append(newPieceLine)
        finalPiece = newPiece
    return finalPiece

def flip_piece(piece):
    flipped_piece = copy.deepcopy(piece)
    flipped_piece.reverse()
    return flipped_piece

# Takes in a board, piece, x and y location. Returns if piece will fit at 
# location (x,y)
def will_piece_fit(board, piece, loc_X, loc_Y):
    # print(len(piece[0])+loc_Y)
    # print(len(piece)+loc_X)
    # print(len(board[0]))
    # print(len(board))
    if len(piece[0])+loc_Y > len(board[0]) or len(piece)+loc_X > len(board):
        return False
    for x in range(len(piece)):
        for y in range(len(piece[x])):
                #print(piece[x][y], "?=", board[loc_X+x][loc_Y+y])
                if piece[x][y]!=board[loc_X+x][loc_Y+y] and piece[x][y]!=" ":
                    return False
    return True
# Takes in a board, piece, x and y location. Puts piece in place on board.
# Represents spaces that are taken with " "
def put_piece_in_place(board, piece, loc_X, loc_Y):
    new_board = board
    for x in range(len(piece)):
        for y in range(len(piece[x])):
            if piece[x][y]!=" ":
                new_board[loc_X+x][loc_Y+y]=" "
    return new_board

# Takes in a board. Returns if it is filled
def is_board_full(board):
    for line in board:
        for spot in line:
            if spot != " ":
                return False
    return True

# Takes in a piece. Returns a
def find_spot_for_piece(board, piece):
    for x in range(len(board)):
        for y in range(len(board[0])):
            for rotation in range(3):
                working_piece = rotate_piece(piece, rotation)
                if will_piece_fit(board, working_piece, x, y):
                    return x,y,rotation,True
    return None, None, None, False

#This brute force solution is deprecated
def brute_force(board, pieces):
    while True:
        available_pieces = []
        for piece in pieces:
            available_pieces.append(pieces[piece])
        working_board = board
        solution = []    
        for piece in pieces:
            currPiece = available_pieces[random.randint(0, len(available_pieces)-1)]
            x_placement, y_placement, rotation, is_placable = find_spot_for_piece(working_board, currPiece)
            print(x_placement, y_placement, rotation, is_placable)
            if is_placable:
                solution.append([currPiece,x_placement, y_placement, rotation])
                working_board = put_piece_in_place(working_board, rotate_piece(currPiece, rotation), x_placement, y_placement)
                available_pieces.remove(currPiece)
            else:
                break
        
        return solution

# This is a helper function that finds how spots are in a piece
# It returns a dictionary where the keys are the type of piece and the values
# are the number of that type of piece. So for the piece "XOX", it would return
# {"X":2, "O":1}
def num_spots_in_piece(piece):
    num_spots={}
    for line in piece:
        for spot in line:
            if spot != " ":
                if spot not in num_spots:
                    num_spots[spot] = 1
                else:
                    num_spots[spot]+=1
    return num_spots

# This is a helper function that checks if a set of pieces has the correct
# number of each type of piece to fill a board. If a board has 20 "X"s and 
# 15 "Y"s, a valid solution must have pieces that have 15 "Y"s and 20 "X"s
def has_necessary_num_pieces(board, num_spots_in_pieces):
    num_spots={}
    for line in board:
        for spot in line:
            if spot != " ":
                if spot not in num_spots:
                    num_spots[spot] = 1
                else:
                    num_spots[spot]+=1
    
    return num_spots_in_pieces == num_spots

# This function takes in the board and the given pieces and returns which set
# of pieces may be a viable solution set.
# Using the library more_itertools, we get the powerset of pieces. This allows
# us to find which set of pieces has the correct number of types of spots.
# For each set in the powerset, it checks if the pieces meet this condition.
# If they do, they are added to the set of plausible sets. The set of plausible
# sets are then returned
def get_plausible_sets(board, pieces):
    piece_power_set = more_itertools.powerset(pieces)
    
    plausibleSets=[]
    for aSet in piece_power_set:
        sum_of_set = {}
        for item in aSet:
            this_pieces_spots = num_spots_in_piece(pieces[item])
            for piece_type in this_pieces_spots:
                if piece_type in sum_of_set:
                    sum_of_set[piece_type]+=this_pieces_spots[piece_type]
                else:
                    sum_of_set[piece_type]=this_pieces_spots[piece_type]
        if has_necessary_num_pieces(board, sum_of_set):
            plausibleSet = {}
            myIter = 0
            for item in aSet:
                plausibleSet[myIter] = pieces[item]
                myIter+=1
            plausibleSets.append(plausibleSet)  
    return plausibleSets  

# This is the function that calls the correct type of depth first search
# (I.E. includes rotations or flips of pieces)
# It returns whatever solutions it finds
def dfs(board, pieces, choice):
    solutions = []
    if choice == 0:
        dfs_helper(board, pieces, 0, [], solutions)
    elif choice == 1:
        dfs_helper_with_rotation(board, pieces, 0, [], solutions)
    elif choice == 2:
        dfs_helper_with_flip(board, pieces, 0, [], solutions)
    elif choice == 3:
        dfs_helper_with_rotation_and_flip(board, pieces, 0, [], solutions)
    return solutions

# Base DFS helper. It takes in a board, a set of pieces, the depth in the DFS
# tree it is at, the current solution that is being built, and the set of solutions.
# If the board it is given has been solved, then it returns adds the current solution 
# it was given to the set of solutions. 
# If the board hasn't been solved and the depth is less thanthe number of pieces, then 
# there are still pieces to be placed. For each spot on the board, it attempts to place
# the next piece. If it will fit at that spot, it places it in a copy of the board, adds
# to the current solution, and finally calls itself with the new board, the pieces, a depth
# one higher, the newly made current solution, and the solution set.
def dfs_helper(board, pieces, depth, currSolution, solutions):
    #print(is_board_full(board))
    if is_board_full(board):
        solutions.append(currSolution) 
    if depth < len(pieces):
        for x in range(len(board)):
            for y in range(len(board[0])):
                currPiece = pieces[depth]
                #print("At depth:", depth)
                #print(x,y)
                #print_piece(currPiece)
                new_board = copy.deepcopy(board)
                #print_board(new_board)
                if will_piece_fit(new_board, currPiece, x, y):
                    new_board = put_piece_in_place(new_board, currPiece, x, y)
                    new_curr_solution = currSolution+[[x,y,pieces[depth],0,0]]
                    dfs_helper(new_board, pieces, depth+1, new_curr_solution, solutions)

# DFS helper that includes piece rotations. This is very similar to the base helper.
# It now also attempts to place a piece in a board after rotating it 0, 90, 180, and 270
# degrees.  
def dfs_helper_with_rotation(board, pieces, depth, currSolution, solutions):
    #print("new search started")
    if is_board_full(board):
        solutions.append(currSolution) 
    if depth < len(pieces):
        for x in range(len(board)):
            for y in range(len(board[0])):
                for rotation in range(4):
                    currPiece = rotate_piece(pieces[depth],rotation)
                    #print("At depth:", depth)
                    #print(x,y)
                    #print_piece(currPiece)
                    new_board = copy.deepcopy(board)
                    #print_board(new_board)
                    #print(will_piece_fit(new_board, currPiece, x, y))
                    if will_piece_fit(new_board, currPiece, x, y):
                        #print("Making new board")
                        new_board = put_piece_in_place(new_board, currPiece, x, y)
                        #print_board(new_board)
                        #print("Making new_curr_solution")
                        new_curr_solution = currSolution+[[x,y,pieces[depth],rotation,0]]
                        #print("Starting new search")
                        dfs_helper_with_rotation(new_board, pieces, depth+1, new_curr_solution, solutions)

# DFS helper that includes piece flips. This is very similar to the base helper.
# It now also attempts to place a piece in a board after flipping it. So a piece
# X                             XX
# X   would be flipped to be    X
# XX                            X
def dfs_helper_with_flip(board, pieces, depth, currSolution, solutions):
    #print(is_board_full(board))
    if is_board_full(board):
        solutions.append(currSolution) 
    if depth < len(pieces):
        for x in range(len(board)):
            for y in range(len(board[0])):
                for flip in range(2):
                    if flip:
                        currPiece = flip_piece(pieces[depth])
                    else:
                        currPiece = pieces[depth]
                    #print("At depth:", depth)
                    #print(x,y)
                    #print_piece(currPiece)
                    new_board = copy.deepcopy(board)
                    #print_board(new_board)
                    if will_piece_fit(new_board, currPiece, x, y):
                        new_board = put_piece_in_place(new_board, currPiece, x, y)
                        new_curr_solution = currSolution+[[x,y,pieces[depth],0, flip]]
                        dfs_helper_with_flip(new_board, pieces, depth+1, new_curr_solution, solutions)

# This DFS helper combines the previous two by allowing both flips and rotations.
def dfs_helper_with_rotation_and_flip(board, pieces, depth, currSolution, solutions):
    #print(is_board_full(board))
    if is_board_full(board):
        solutions.append(currSolution) 
    if depth < len(pieces):
        for x in range(len(board)):
            for y in range(len(board[0])):
                for rotation in range(4):
                    for flip in range(2):
                        if flip:
                            currPiece = rotate_piece(flip_piece(pieces[depth]),rotation)
                        else:
                            currPiece = rotate_piece(pieces[depth],rotation)
                        #print("At depth:", depth)
                        #print(x,y)
                        #print_piece(currPiece)
                        new_board = copy.deepcopy(board)
                        #print_board(new_board)
                        if will_piece_fit(new_board, currPiece, x, y):
                            new_board = put_piece_in_place(new_board, currPiece, x, y)
                            new_curr_solution = currSolution+[[x,y,pieces[depth],0, flip]]
                            dfs_helper_with_rotation_and_flip(new_board, pieces, depth+1, new_curr_solution, solutions)

def merges_sides(l_arr, r_arr, l, m, r):
    #l_arr = arr[l:m]
    #r_arr = arr[m + 1:r]
    arr = [0] * (len(l_arr) + len(r_arr))
    i = 0; j = 0; k=l
    while i < len(l_arr) and j < len(r_arr):
        # judging size based on number of tiles in 2D array
        print("len(l_arr)={}, len(r_arr)={}, len(arr)={}".format(len(l_arr), len(r_arr), len(arr)))
        print("i={}, j={}, k={}".format(i, j, k))
        if(len(l_arr[i]) * len(l_arr[i][0]) <= len(r_arr[j]) * len(r_arr[j][0])):
            arr[k] = l_arr[i]
            i += 1
        else:
            arr[k] = r_arr[j]
            j += 1
        k += 1
    while i < len(l_arr):
        arr[k] = l_arr[i]
        i += 1; k += 1
    while j < len(r_arr):
        print("l_arr = {}, r_arr={}, arr={}".format(l_arr, r_arr, arr))
        arr[k] = r_arr[j]
        j += 1; k += 1
    return arr

def mergesort(arr, l, r):
    if l < r:
        m = int((l + r -1)/2)
        l_arr = mergesort(arr, l, m)
        r_arr = mergesort(arr, m+1, r)
        arr = merges_sides(l_arr, r_arr, l, m, r)
    return arr

def order_pieces_by_size(myPieces):
    myPieces = mergesort(myPieces, 0, len(myPieces))
    return myPieces

def main():
    myBoard, myPieces = parse_input_file(sys.argv[1])
    sorted_pieces = order_pieces_by_size(myPieces)
    print(sorted_pieces)
    exit()
    # print_board(myBoard)
    # for piece in myPieces:
    #     print_piece(myPieces[piece])

    # print(brute_force(myBoard, myPieces))
    print_board(myBoard)
    #print(myPieces)
    for piece in myPieces:
        print_piece(myPieces[piece])
    #    print_piece(flip_piece(myPieces[piece]))

    plausibleSets = get_plausible_sets(myBoard, myPieces)

    allSolutions = []
    start = time.time()
    if plausibleSets:
        for plausibleSet in plausibleSets:
            print(plausibleSet)
            some_solutions = (dfs(myBoard, plausibleSet, 0))
            if some_solutions!=[]:
                allSolutions.append(some_solutions)
    else:
        print("There are no plausible sets")
    print(time.time()-start)

    if allSolutions!=[]:
        print(allSolutions)
        print("There are",len(allSolutions[0]), "solutions.")
    else:
        print("There are no solutions!")

main()