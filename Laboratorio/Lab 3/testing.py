import numpy as np
positions = [1, 3, 4]
p1,p2     = np.array(['A', 'B', 'C', 'D', 'F', 'E', 'G']), np.array(['C', 'E', 'G', 'A', 'D', 'F', 'B'])


# val1 = p1[positions]
# val2 = p2[positions]
# pos2 = []
# for i in val1:
#     pos2.append(np.where(p2 == i)[0][0])
# pos2 = np.sort(pos2)
# pos1 = []
# for i in val2:
#     pos1.append(np.where(p1 == i)[0][0])
# pos1 = np.sort(pos1)
#
# for i in range(0,len(pos2)):
#     p1[ positions[i] ] = p2[ pos2[i] ]
#
# for i in range(0,len(pos1)):
#     p2[ positions[i] ] = p1[ pos1[i] ]
#
#
# child1 = "".join(p1)
# child2 = "".join(p2)


def OBX(p1,p2,positions):
    val = p1[positions]
    pos = []
    for i in val:
        pos.append(np.where(p2 == i)[0][0])
    pos = np.sort(pos)
    for i in range(0,len(pos)):
        p1[ positions[i] ] = p2[ pos[i] ]
    return p1


print(OBX(p1,p2,positions))
print(OBX(p2,p1,positions))
