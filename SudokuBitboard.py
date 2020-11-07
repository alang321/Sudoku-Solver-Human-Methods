import numpy as np

class SudokuBitboard:

    zeroMask = np.uint32(0b00000111111111111111111111111111)

    def __init__(self, indexList=None, bitboardArgument=None):
        self.bitboard = np.uint32([0, 0, 0])
        if bitboardArgument is not None:
            self.bitboard=bitboardArgument
        if indexList is not None:
            self.bitboard_from_indexList(indexList)

    def set_bit(self, pos):
        self.bitboard[pos // 27] |= (1 << (pos % 27))

    def clear_bit(self, pos):
        self.bitboard[pos // 27] &= ~(1 << (pos % 27))

    def get_bit(self, pos):
        return self.bitboard[pos // 27] & (1 << (pos % 27))

    def bitboard_from_indexList(self, indexList):
        for index in indexList:
            self.set_bit(index)

    def is_zero(self):
        for i in self.bitboard:
            if (i & self.zeroMask) != 0:
                return False
        return True

    def is_exactly_one_bit_set(self):
        powerOf2found = False
        for i in self.bitboard:
            if i == 0:
                continue
            elif not powerOf2found and SudokuBitboard.is_power_of_two(i):
                powerOf2found = True
            else:
                return False

        return powerOf2found

    @staticmethod
    def is_power_of_two(int32):
        return int32 and not (int32 & (int32 - 1))

    def to_string(self):
        sudokuString = ""
        for rows in range(0, 9):
            for columnns in range(0, 9):
                if (columnns) % 3 == 0:
                    sudokuString += " "
                if self.get_bit(rows*9+columnns):
                    sudokuString += "1"
                else:
                    sudokuString += "0"
            sudokuString += "\n"

            if (rows+1)%3 == 0:
                sudokuString += "\n"

        return sudokuString.replace("0", "-")

    def __or__(self, other):
        return SudokuBitboard(bitboardArgument=np.uint32([self.bitboard[0] | other.bitboard[0], self.bitboard[1] | other.bitboard[1], self.bitboard[2] | other.bitboard[2]]))

    def __and__(self, other):
        return SudokuBitboard(bitboardArgument=np.uint32([self.bitboard[0] & other.bitboard[0], self.bitboard[1] & other.bitboard[1], self.bitboard[2] & other.bitboard[2]]))

    def __xor__(self, other):
        return SudokuBitboard(bitboardArgument=np.uint32([self.bitboard[0] ^ other.bitboard[0], self.bitboard[1] ^ other.bitboard[1], self.bitboard[2] ^ other.bitboard[2]]))

    def __invert__(self):
        return SudokuBitboard(bitboardArgument=np.uint32([~self.bitboard[0], ~self.bitboard[1], ~self.bitboard[2]]))


