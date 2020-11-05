defaultSubgrid = [1,1,1,2,2,2,3,3,3]

firstcol = 0
stringsud=""
for i in range(0, 9):

    stringsud += "["
    for j in range(0, 9):

        stringsud += str(i+j*9) + ","
    stringsud += "],\n                     "


print("rowIntersections = [", stringsud, "]")