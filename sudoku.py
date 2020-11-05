from itertools import count
import random


class Sudoku:
    #default subgrid layout, is used if no other layout is specified
    defaultSubgrid = [0, 0, 0, 1, 1, 1, 2, 2, 2,
                      0, 0, 0, 1, 1, 1, 2, 2, 2,
                      0, 0, 0, 1, 1, 1, 2, 2, 2,
                      3, 3, 3, 4, 4, 4, 5, 5, 5,
                      3, 3, 3, 4, 4, 4, 5, 5, 5,
                      3, 3, 3, 4, 4, 4, 5, 5, 5,
                      6, 6, 6, 7, 7, 7, 8, 8, 8,
                      6, 6, 6, 7, 7, 7, 8, 8, 8,
                      6, 6, 6, 7, 7, 7, 8, 8, 8]

    #simple 9x9 list of
    initialSetValues = [] #initial input set values, 0 if not set

    #solving
    setValues = [] #set values, 0 if not set
    possibleValues = [[True if k>0 else 9 for k in range(10)] for j in range(81)] #possible values for each cell, each cell has 10 values, one bool if each 1 to 9 values is possible, and one number keeping track of how many possibilities there are for this cell
    emptyCells = 81 # how many cells dont have a value
    #guessing forks

    forkSnapshot = [None] * 81 #snapshot of values saved at guessing forks: guesses left, cell index of guess, possible values, empty cells, set values
    lastForkIndex = -1
    maxSolutions = 10
    solutions = [None] * maxSolutions

    #list with sublist of all indices that intersect
    subcellIndices = []
    rowIndeces = [[0, 1, 2, 3, 4, 5, 6, 7, 8],
                  [9, 10, 11, 12, 13, 14, 15, 16, 17],
                  [18, 19, 20, 21, 22, 23, 24, 25, 26],
                  [27, 28, 29, 30, 31, 32, 33, 34, 35],
                  [36, 37, 38, 39, 40, 41, 42, 43, 44],
                  [45, 46, 47, 48, 49, 50, 51, 52, 53],
                  [54, 55, 56, 57, 58, 59, 60, 61, 62],
                  [63, 64, 65, 66, 67, 68, 69, 70, 71],
                  [72, 73, 74, 75, 76, 77, 78, 79, 80]]
    colIndices = [[0, 9, 18, 27, 36, 45, 54, 63, 72],
                [1, 10, 19, 28, 37, 46, 55, 64, 73],
                [2, 11, 20, 29, 38, 47, 56, 65, 74],
                [3, 12, 21, 30, 39, 48, 57, 66, 75],
                [4, 13, 22, 31, 40, 49, 58, 67, 76],
                [5, 14, 23, 32, 41, 50, 59, 68, 77],
                [6, 15, 24, 33, 42, 51, 60, 69, 78],
                [7, 16, 25, 34, 43, 52, 61, 70, 79],
                [8, 17, 26, 35, 44, 53, 62, 71, 80]]
    miscIndices = []

    IntersectionsIndices = [subcellIndices, rowIndeces, colIndices, miscIndices]

    #region set Sudoku

    #parse values as string from top left row first and subgrid layout
    def setSudoku(self, sudoku, subgrid=defaultSubgrid):
        self.parseValues(sudoku)
        self.praseSubgridIntersections(subgrid)
        self.setupPossibilities()

    def parseValues(self, values):
        # raise exception if the parsed sudoku does not have 81 cells
        if len(values) != 81:
            raise Exception("The Sudoku has to have exactly 81 cells")

        for i in values:
            self.initialSetValues.append(int(i))

            if int(i) != 0:
                self.emptyCells -= 1

        self.setValues = self.initialSetValues.copy()
        return

    def praseSubgridIntersections(self, subgrid):
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

            self.subcellIndices.append(cellIndices)
        return

    def setupPossibilities(self):
        for index, value in enumerate(self.possibleValues):
            if self.setValues[index] != 0:
                value[0] = 0
                for i in range(1, 10):
                    value[i] = False
        return

    #endregion

    #region print Sudoku

    def initialToString(self):
        return "Initial Values: \n" + Sudoku.setvaluesToString(self.initialSetValues)

    def solvedToString(self):
        return "Solved Sudoku: \n" + Sudoku.setvaluesToString(self.setValues)

    def totalPossibilitiesToString(self):

        sudokuString = "How many Numbers are possible each field: \n"
        for rows in range(0, 9):
            for columnns in range(0, 9):
                if (columnns) % 3 == 0:
                    sudokuString += " "
                sudokuString += str(self.possibleValues[rows * 9 + columnns][0])
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
                valuePossibilityBool = self.possibleValues[rows * 9 + columnns][value]
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

    #region Solving algorithm

    def solve(self):

        while self.emptyCells > 0:
            #

            #eliminate possibilities
            self.eliminatePossibilities()

            # set cell values that are determined by possibility elimination
            if self.setDeterminedCellValues():
                continue

            # take a guess if no value is determined
            self.guess()


    #region Possibility elimination

    def eliminatePossibilities(self):
        self.intersectionElimination()

    def intersectionElimination(self):
        for currentCell in range(81):
            if self.setValues[currentCell] != 0: #if the cell is not empty
                for type in self.IntersectionsIndices:
                    for intersectionBlock in type:
                        if currentCell in intersectionBlock:#if the current cell is part of the intersection block
                            for cell in intersectionBlock:
                                if self.possibleValues[cell][self.setValues[currentCell]]:
                                    self.possibleValues[cell][0] -= 1
                                    self.possibleValues[cell][self.setValues[currentCell]] = False
        return

    #endregion

    #region determine cell values

    def setDeterminedCellValues(self):
        if self.loneSingles():
            return True
        if self.hiddenSingles():
            return True

    def loneSingles(self):
        for cell, cellPossibilities in enumerate(self.possibleValues):
            if cellPossibilities[0] == 1:
                for value in range(1, 10):
                    if cellPossibilities[value]:
                        self.setCell(cell, value)
                        #print("\nlone", value, " in ", cell)
                        return True
        return False

    def hiddenSingles(self):
        for type in self.IntersectionsIndices:
            for intersectionBlock in type:
                #every value that is a possibility in the intersection block gets checked if its a hidden Single
                possibilityCounter = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #counter for each value, one extra value so the value can be used as the index

                #remove cells with values in them from consideration
                consideredCells = intersectionBlock.copy()
                consideredValues = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                for cell in intersectionBlock:
                    if self.setValues[cell] != 0:
                        consideredCells.remove(cell)
                        consideredValues.remove(self.setValues[cell])

                # count number occurrences of considered values in considered cells
                for cell in consideredCells:
                    for value in consideredValues:
                        if self.possibleValues[cell][value]:
                            possibilityCounter[value] += 1

                # check if there is a hidden single
                if 1 in possibilityCounter:
                    value = possibilityCounter.index(1)
                    for cell in consideredCells:
                        if self.possibleValues[cell][value]:
                            self.setCell(cell, value)
                            #print("\nhidden", value, " in ", cell)
                            return True
        return False

    def setCell(self, index, value):
        if self.setValues[index] == 0: #only if the cell is empty
            self.setValues[index] = value #set the cell to spcified value

            # no values can now be possible in this cell
            self.possibleValues[index][0] = 0
            for i in range(1, 10):
                self.possibleValues[index][i] = False

            #one less remaining empty cell
            self.emptyCells -= 1
            return True
        return False

    #endregion

    #region guess

    def guess(self):
        #find cell with lowest number of possibilities, if there are multiple lowest index is used
        minPossible = 10
        minIndex = -1

        for index, possibilities in enumerate(self.possibleValues):
            if possibilities[0] != 0 and possibilities[0] < minPossible:
                minPossible = possibilities[0]
                minIndex = index

        #wrong guess revert to old
        if minIndex == -1:#if there are empty cells with 0 possibilities a wrong guess has occurred
            self.nextGuess()
            return

        #new guess
        self.newFork(minIndex)

    def nextGuess(self):
        for i in range(self.lastForkIndex, -1, -1):
            if self.forkSnapshot[i][0] != 0:
                self.lastForkIndex = i
                self.loadSnapshot(self.forkSnapshot[i])
                self.forkSnapshot[i][0] -= 1
                self.setCell(self.forkSnapshot[i][1], self.forkSnapshot[self.lastForkIndex][2][self.forkSnapshot[self.lastForkIndex][0]])
                print("WRONG GUESS!! guessed", self.forkSnapshot[self.lastForkIndex][2][self.forkSnapshot[self.lastForkIndex][0]], "in cell:", self.forkSnapshot[i][1])
                return True
        return False #if no fork where possible guesses exist, return False (invalid sudoku)


    def newFork(self, index):
        self.lastForkIndex += 1
        self.forkSnapshot[self.lastForkIndex] = self.createSnapshot(index)

        self.forkSnapshot[self.lastForkIndex][0] -= 1
        self.setCell(index, self.forkSnapshot[self.lastForkIndex][2][self.forkSnapshot[self.lastForkIndex][0]])
        print("guessed", self.forkSnapshot[self.lastForkIndex][2][self.forkSnapshot[self.lastForkIndex][0]], "in cell:", index)

    #always taken before value is set
    def createSnapshot(self, guessIndex):
        possibleValues = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for i in range(1, 10):
            if not self.possibleValues[guessIndex][i]:
                possibleValues.remove(i)
        random.shuffle(possibleValues)
        valueSnapshot = [len(possibleValues), guessIndex, possibleValues, self.emptyCells, self.setValues.copy()]
        return valueSnapshot

    def loadSnapshot(self, snapshot):
        self.emptyCells = snapshot[3]
        self.setValues = snapshot[4].copy()

        #todo : better possibility
        self.possibleValues = [[True if k > 0 else 9 for k in range(10)] for j in range(81)]
        self.setupPossibilities()
        return

    #endregion

    #endregion


medium = "009750000000000000005382000010000003002000908406000000900040130700006549000200000"
extreme = "950010087430000091008000400000807000500040003000603000004000700890000052710090048"
multiplePossibilities = "950010087430000091008000400000807000500040003000603000004000700890000050710090048" #9 possible solutions

sudoku1 = Sudoku()

sudoku1.setSudoku(multiplePossibilities)

sudoku1.solve()

print(sudoku1.totalPossibilitiesToString())
print(sudoku1.initialToString())
print(sudoku1.solvedToString())




#solving functions sorted by priority

#possibility elimination

#intersection elimination
#Omission
#Naked Pairs
#Naked Triplets & Quads
#Hidden Pairs Triplets & Quads
#X-Wing
#Swordfish
#XY Wing





