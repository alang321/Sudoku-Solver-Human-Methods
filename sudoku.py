from itertools import count
import random
import time
from SudokuBitboard import SudokuBitboard
import numpy as np

class Sudoku:
    #region variables

    #region default values

    defaultSubgrid = [0, 0, 0, 1, 1, 1, 2, 2, 2,
                      0, 0, 0, 1, 1, 1, 2, 2, 2,
                      0, 0, 0, 1, 1, 1, 2, 2, 2,
                      3, 3, 3, 4, 4, 4, 5, 5, 5,
                      3, 3, 3, 4, 4, 4, 5, 5, 5,
                      3, 3, 3, 4, 4, 4, 5, 5, 5,
                      6, 6, 6, 7, 7, 7, 8, 8, 8,
                      6, 6, 6, 7, 7, 7, 8, 8, 8,
                      6, 6, 6, 7, 7, 7, 8, 8, 8]

    defaultRowIndeces = [[0, 1, 2, 3, 4, 5, 6, 7, 8],
                  [9, 10, 11, 12, 13, 14, 15, 16, 17],
                  [18, 19, 20, 21, 22, 23, 24, 25, 26],
                  [27, 28, 29, 30, 31, 32, 33, 34, 35],
                  [36, 37, 38, 39, 40, 41, 42, 43, 44],
                  [45, 46, 47, 48, 49, 50, 51, 52, 53],
                  [54, 55, 56, 57, 58, 59, 60, 61, 62],
                  [63, 64, 65, 66, 67, 68, 69, 70, 71],
                  [72, 73, 74, 75, 76, 77, 78, 79, 80]]

    defaultColIndices = [[0, 9, 18, 27, 36, 45, 54, 63, 72],
                  [1, 10, 19, 28, 37, 46, 55, 64, 73],
                  [2, 11, 20, 29, 38, 47, 56, 65, 74],
                  [3, 12, 21, 30, 39, 48, 57, 66, 75],
                  [4, 13, 22, 31, 40, 49, 58, 67, 76],
                  [5, 14, 23, 32, 41, 50, 59, 68, 77],
                  [6, 15, 24, 33, 42, 51, 60, 69, 78],
                  [7, 16, 25, 34, 43, 52, 61, 70, 79],
                  [8, 17, 26, 35, 44, 53, 62, 71, 80]]

    defaultMaxSolutions = 100

    #endregion

    #region solving variables
    currentSetCellValues = [] #all the values currently set in the sudoku grid, 0 if not set
    possibleValuesCell = [] #possible values for each cell, each cell has 10 values, one bool if each 1 to 9 values is possible, extra field so value can be used as index
    cellPossibilityCounter = [] #counts how many values are possible in each cell
    intersectionBlockPossibilityCounter = []
    emptyCells = 81 # how many cells dont have a value
    #endregion


    #endregion

    def __init__(self, maxSolutions=defaultMaxSolutions):
        #intersection Block variables
        self.intersectionBlocksBitboards = []

        self.subgridIndices = []
        self.rowIndices = self.defaultRowIndeces
        self.colIndices = self.defaultColIndices
        self.miscIndices = []

        #solution variables
        self.maxSolutions = maxSolutions
        self.numberOfSolutions = 0  # number of solutions that have been determined
        self.sudokuSolutions = [None] * self.maxSolutions

        # guessing forks
        self.forkSnapshot = [None] * 81  # snapshot of values saved at guessing forks: guesses left, cell index of guess, possible values, empty cells, set values
        self.lastForkIndex = -1

        # simple 9x9 list of initial set values for display purposes
        self.initialSetValues = []  # initial input set values, 0 if not set

        #current set cell values
        self.isCellSetBitboard = SudokuBitboard()
        self.currentSetValuesBitboards = [SudokuBitboard() for _ in range(9)]  # all the values currently set in the sudoku grid in bitboards
        self.possibleValuesBitboards = [SudokuBitboard(bitboardArgument=np.uint32([0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF])) for _ in range(9)]


    #region set Sudoku

    #parse values as string from top left row first and subgrid layout
    def setSudoku(self, sudoku, subgrid=defaultSubgrid, miscIntersections=[]):
        self.parseValues(sudoku)
        self.miscIndices = miscIntersections
        self.setupIntersections(subgrid)

    def parseValues(self, values):
        # raise exception if the parsed sudoku does not have 81 cells
        if len(values) != 81:
            raise Exception("The Sudoku has to have exactly 81 cells")

        for index, valueStr in enumerate(values):
            value = int(valueStr)
            self.initialSetValues.append(value)

            if value != 0:
                self.currentSetValuesBitboards[value - 1].set_bit(index)

        for value in range(9):
            self.isCellSetBitboard |= self.currentSetValuesBitboards[value]

        return

    def setupIntersections(self, subgrid):
        # subgrid Indices
        for cellIndex in count(0):
            # gets the intersections of
            cellIndices = [i for i, x in enumerate(subgrid) if x == cellIndex]

            # if no more subgrids are found return
            if len(cellIndices) == 0:
                break

            # raise exception if subgrid does not have exactly nine cells
            if len(cellIndices) != 9:
                raise Exception("Each subcell has to contain exactly nine fields")

            self.subgridIndices.append(cellIndices)

        self.intersectionBlocks = [self.subgridIndices, self.rowIndices, self.colIndices, self.miscIndices]

        #all bitboards of intersection blocks
        for intersectionBlockType in self.intersectionBlocks:
            for block in intersectionBlockType:
                self.intersectionBlocksBitboards.append(SudokuBitboard(indexList=block))
        return

    #endregion

    #region Solving algorithm

    def solve(self):
        start = time.time()
        while not (~self.isCellSetBitboard).is_zero():
            #eliminate possibilities
            self.eliminatePossibilities()

            # set cell values that are determined by possibility elimination
            self.setDeterminedCellValues()

                #if sudoku solved, add solution to table and check for more solutions
                #if self.emptyCells == 0 and self.numberOfSolutions < self.maxSolutions:
                    #self.sudokuSolutions[self.numberOfSolutions] = self.currentSetCellValues.copy()
                    #self.numberOfSolutions += 1
                    #if not self.nextGuess():
                        #break

            # take a guess if no value is determined
            #if not self.guess():
                #break

        for i in range(9):
            print(self.currentSetValuesBitboards[i].to_string() )
        print(self.isCellSetBitboard.to_string())
        end = time.time()
        print("Runtime", (end - start))

    #region Possibility elimination

    def eliminatePossibilities(self):
        self.intersectionElimination()

    def intersectionElimination(self):
        for value in range(9):
            self.possibleValuesBitboards[value] &= (self.isCellSetBitboard ^ self.possibleValuesBitboards[value])

        for block in self.intersectionBlocksBitboards:
            for value in range(9):
                if not (block & self.currentSetValuesBitboards[value]).is_zero():
                    self.possibleValuesBitboards[value] = (block ^ self.possibleValuesBitboards[value]) & self.possibleValuesBitboards[value]
        return

    # possibility elimination

    # intersection elimination
    # Omission
    # Naked Pairs
    # Naked Triplets & Quads
    # Hidden Pairs Triplets & Quads
    # X-Wing
    # Swordfish
    # XY Wing

    #endregion

    #region determine cell values

    def setDeterminedCellValues(self):
        self.loneSingles()
        self.hiddenSingles()

    def loneSingles(self):
        loneSingleMask = SudokuBitboard()
        for i in range(9):
           temp = self.possibleValuesBitboards[i]
           for j in range(9):
               if j != i:
                   temp &= ~self.possibleValuesBitboards[j]

           loneSingleMask |= temp

        if not loneSingleMask.is_zero():
            for value in range(9):
                self.currentSetValuesBitboards[value] |= self.possibleValuesBitboards[value] & loneSingleMask
            self.isCellSetBitboard |= loneSingleMask
        else:
            return False

    def hiddenSingles(self):
        for block in self.intersectionBlocksBitboards:
            for value in range(9):
                mask = block & self.possibleValuesBitboards[value]
                if mask.is_exactly_one_bit_set() and (mask & self.isCellSetBitboard).is_zero():
                    self.isCellSetBitboard |= mask
                    self.currentSetValuesBitboards[value] |= mask
                    #print("Hidden Single for Value:", value+1)
                    #print('With possible Cells:\n{}'.format(self.possibleValuesBitboards[value].to_string()))
                    #print('In Intersection Block:\n{}'.format(block.to_string()))

    #endregion

    #region guess

    def guess(self):
        #find cell with lowest number of possibilities, if there are multiple lowest index is used
        minPossible = 10
        minIndex = -1

        for index, possibilityCount in enumerate(self.cellPossibilityCounter):
            if possibilityCount != 0 and possibilityCount < minPossible:
                minPossible = possibilityCount
                minIndex = index

        #wrong guess revert to old
        if minIndex == -1:#if there are empty cells with 0 possibilities a wrong guess has occurred
            if self.nextGuess():
                return True
            else:
                return False

        #new guess
        self.newFork(minIndex)
        return True

    def nextGuess(self):
        for i in range(self.lastForkIndex, -1, -1):
            if self.forkSnapshot[i][0] != 0:
                self.lastForkIndex = i
                self.loadSnapshot(self.forkSnapshot[i])
                self.forkSnapshot[i][0] -= 1
                self.setCell(self.forkSnapshot[i][1], self.forkSnapshot[self.lastForkIndex][2][self.forkSnapshot[self.lastForkIndex][0]])
                #print("WRONG GUESS!! guessed", self.forkSnapshot[self.lastForkIndex][2][self.forkSnapshot[self.lastForkIndex][0]], "in cell:", self.forkSnapshot[i][1], ", now ", self.emptyCells, "empty cells left")
                return True
        return False #if no fork where possible guesses exist, return False (invalid sudoku)


    def newFork(self, index):
        self.lastForkIndex += 1
        self.forkSnapshot[self.lastForkIndex] = self.createSnapshot(index)

        self.forkSnapshot[self.lastForkIndex][0] -= 1
        self.setCell(index, self.forkSnapshot[self.lastForkIndex][2][self.forkSnapshot[self.lastForkIndex][0]])
        #print("guessed", self.forkSnapshot[self.lastForkIndex][2][self.forkSnapshot[self.lastForkIndex][0]], "in cell:", index)

    #always taken before value is set
    def createSnapshot(self, guessIndex):
        possibleValues = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for i in range(1, 10):
            if not self.possibleValuesCell[guessIndex][i]:
                possibleValues.remove(i)
        random.shuffle(possibleValues)
        valueSnapshot = [len(possibleValues), guessIndex, possibleValues, self.emptyCells, self.currentSetCellValues.copy()]
        return valueSnapshot

    def loadSnapshot(self, snapshot):
        self.emptyCells = snapshot[3]
        self.currentSetCellValues = snapshot[4].copy()

        self.resetPossibilities()
        return

    #endregion

    #endregion



    #region print Sudoku

    def initialToString(self):
        return "Initial Values: \n" + Sudoku.setvaluesToString(self.initialSetValues)

    def solvedToString(self):
        if self.numberOfSolutions == 0:
            return "No solutions have been found yet"

        returnString = str(self.numberOfSolutions) + " Solutions have been determined (Limit of " + str(self.maxSolutions) + "):\n"
        for i in range(0, self.numberOfSolutions):
            returnString += "Solution " + str(i+1) + ":\n"
            returnString += Sudoku.setvaluesToString(self.sudokuSolutions[i])
            returnString += "\n"
        return returnString

    def totalPossibilitiesToString(self):

        sudokuString = "How many Numbers are possible each field: \n"
        for rows in range(0, 9):
            for columnns in range(0, 9):
                if (columnns) % 3 == 0:
                    sudokuString += " "
                sudokuString += str(self.cellPossibilityCounter[rows * 9 + columnns])
            sudokuString += "\n"

            if (rows + 1) % 3 == 0:
                sudokuString += "\n"

        return sudokuString.replace("0", "-")

    def specificPossibilitiesToString(self, value):
        sudokuString = "If " + str(value) + " is possible this shows 1: \n"
        for rows in range(0, 9):
            for columnns in range(0, 9):
                if (columnns) % 3 == 0:
                    sudokuString += " "
                valuePossibilityBool = self.possibleValuesCell[rows * 9 + columnns][value]
                if valuePossibilityBool:
                    sudokuString += "1"
                else:
                    sudokuString += "0"
            sudokuString += "\n"

            if (rows + 1) % 3 == 0:
                sudokuString += "\n"

        return sudokuString.replace("0", "-")

    @staticmethod
    def setvaluesToString(setValues):
        sudokuString = ""
        for rows in range(0, 9):
            for columnns in range(0, 9):
                if (columnns) % 3 == 0:
                    sudokuString += " "
                sudokuString += str(setValues[rows*9+columnns])
            sudokuString += "\n"

            if (rows+1)%3 == 0:
                sudokuString += "\n"

        return sudokuString.replace("0", "-")

    #endregion






#testing

medium = "009750000000000000005382000010000003002000908406000000900040130700006549000200000"
extreme = "950010087430000091008000400000807000500040003000603000004000700890000052710090048"
multiplePossibilities = "950010087430000091008000400000807000500040003000603000004000700890000050710090048" #9 possible solutions
onlyonenumber = "100000000000000000000000000000000000000000000000000000000000000000000000000000000"
impossible = "950010087430000091008000408000807000500040003000603000004000700890000052710090048" #8 column intersection on column 9

squiggly1 = "500603027900000000000900000200000501000000000109000002000001000000000008820305006"
squiggly1Subgrid =   [0, 0, 0, 0, 1, 1, 1, 1, 1,
                      2, 0, 1, 1, 1, 3, 1, 3, 3,
                      2, 0, 0, 0, 3, 3, 3, 3, 4,
                      2, 0, 2, 3, 3, 4, 4, 4, 4,
                      2, 2, 2, 2, 4, 4, 5, 5, 5,
                      6, 2, 6, 4, 4, 5, 5, 7, 5,
                      6, 6, 6, 8, 8, 8, 7, 7, 5,
                      6, 8, 8, 8, 7, 7, 7, 5, 5,
                      6, 6, 6, 8, 8, 8, 7, 7, 7]

squiggly4439b = "000900800800005790030700908000000070097506430040000000302004010076100004009007000"
squiggly4439bSubgrid =   [0, 0, 0, 0, 1, 1, 1, 2, 2,
                          0, 0, 0, 0, 1, 1, 1, 2, 2,
                          0, 3, 3, 3, 1, 1, 1, 2, 2,
                          3, 3, 3, 3, 4, 4, 2, 2, 2,
                          3, 3, 4, 4, 4, 4, 4, 5, 5,
                          6, 6, 6, 4, 4, 5, 5, 5, 5,
                          6, 6, 7, 7, 7, 5, 5, 5, 8,
                          6, 6, 7, 7, 7, 8, 8, 8, 8,
                          6, 6, 7, 7, 7, 8, 8, 8, 8]

#https://puzzlephil.com/resources/non-standard-raetsel/sudoku-varianten/pdf/ExtraRegions-Sudoku.pdf
#https://puzzlephil.com/resources/non-standard-raetsel/sudoku-varianten/pdf/ExtraRegions-Sudoku_loesung.pdf
extraregions = "100040008000080000009060700000070000027000640004000300000000000000010000040906020"
extraregionsmisc =   [[1, 2, 3, 12, 21, 30, 29, 28, 19],
                      [17, 26, 35, 34, 33, 32, 23, 14, 15],
                      [63, 54, 45, 46, 47, 48, 57, 66, 65],
                      [79, 78, 77, 68, 59, 50, 51, 52, 61]]
#sudoku1.setSudoku(extraregions, miscIntersections=extraregionsmisc)

#https://sudokuschwer.com/x-sudoku/answer.php?id=NGTuA1wXNiznEY1uO1QO0O0OO0O0O
diagonal = "040000200500007000981003040009000700000500000300002000000085002700001050000694070"
diagonalmisc =   [[0, 10, 20, 30, 40, 50, 60, 70, 80],
                  [8, 16, 24, 32, 40, 48, 56, 64, 72]]
#sudoku1.setSudoku(diagonal, miscIntersections=diagonalmisc)



sudoku1 = Sudoku()

sudoku1.setSudoku(medium)

sudoku1.solve()
#sudoku1.eliminatePossibilities()
#sudoku1.hiddenSingles()

print(sudoku1.isCellSetBitboard.to_string())
print(sudoku1.initialToString())
#print(sudoku1.solvedToString())










