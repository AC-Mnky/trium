import math


def k_means(coords):
    num = len(coords)
    center = [coords[int(num / 4) - 1], coords[int(3 * num / 4) - 1]]
    class_num = 2

    if num >= 3:
        while True:
            classes = [[], []]
            center_past = center
            for i in range(0, num):
                dist = []
                for j in range(0, class_num):
                    dist.append(math.sqrt((coords[i][0] - center[j][0]) ** 2 + (coords[i][1] - center[j][1]) ** 2))
                center_belong = dist.index(min(dist))
                classes[center_belong].append(coords[i])

            center = [[0, 0], [0, 0]]
            for i in range(0, class_num):
                for j in range(0, len(classes[i])):
                    center[i][0] = center[i][0] + classes[i][j][0]
                    center[i][1] = center[i][1] + classes[i][j][1]
                center[i][0] /= len(classes[i])
                center[i][1] /= len(classes[i])

            if center_past == center:
                break
    return center, classes
