import math


def k_means(cords, n):
    num = len(cords)
    class_num = int(n / 2)
    center = []
    for i in range(0, class_num):
        center.append(cords[i])

    classes = []
    if num >= class_num:
        while True:
            classes = []
            for i in range(0, class_num):
                classes.append([])

            center_past = center
            for i in range(0, num):
                dist = []
                for j in range(0, class_num):
                    dist.append(math.sqrt((cords[i][0] - center[j][0]) ** 2 + (cords[i][1] - center[j][1]) ** 2))
                center_belong = dist.index(min(dist))
                classes[center_belong].append(cords[i])

            center = []
            for i in range(0, class_num):
                center.append([0, 0])

            for i in range(0, class_num):
                for j in range(0, len(classes[i])):
                    center[i][0] = center[i][0] + classes[i][j][0]
                    center[i][1] = center[i][1] + classes[i][j][1]
                center[i][0] /= len(classes[i])
                center[i][1] /= len(classes[i])

            if center_past == center:
                break

    return center, classes


def loop_check(cords):
    center = []

    for i in range(0, len(cords)):
        center.append(cords[i])

    while True:
        i = 0
        while i < len(center):
            j = i
            while j < len(center):
                dist_between_centers = math.sqrt(
                    (center[i][0] - center[j][0]) ** 2 + (center[i][1] - center[j][1]) ** 2)
                if dist_between_centers < 100 and dist_between_centers != 0:
                    new_center = [(center[i][0] + center[j][0]) / 2, (center[i][1] + center[j][1]) / 2]
                    a = center[i]
                    b = center[j]
                    center.remove(a)
                    center.remove(b)
                    center.append(new_center)

                    j = len(center)
                    i = len(center)
                j = j + 1
            i = i + 1
        if center == cords:
            break
        else:
            cords = []
            for i in range(0, len(center)):
                cords.append(center[i])
    return center
