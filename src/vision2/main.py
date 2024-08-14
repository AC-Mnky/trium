import cv2
import os.path

from find_color import find_red
import camera_convert

mode = 'file'
# mode = 'camera'
read_version = '0'
write_version = '1'

if mode == 'camera':
    from camera import Camera


def process(img, show: bool = False):
    points = find_red(img, show)

    draw_grid((255, 255, 255, 255), 0, 1500, 50, -1000, 1000, 50)

    print()
    for p in points:
        s, x, y = camera_convert.img2space(camera_state, p[0], p[1], -12.5)
        if s:
            cv2.circle(img, p, 10, (255, 255, 255, 255), 2)
            print((x, y))
        else:
            cv2.circle(img, p, 10, (128, 128, 128, 255), 1)
    if show:
        cv2.imshow('image', img)


def draw_grid(color, x_start, x_stop, x_step, y_start, y_stop, y_step):
    for x in range(x_start, x_stop + x_step, x_step):
        for y in range(y_start, y_stop, y_step):
            s1, i1, j1 = camera_convert.space2img(camera_state, x, y)
            s2, i2, j2 = camera_convert.space2img(camera_state, x, y + y_step)
            if s1 or s2:
                cv2.line(image, (i1, j1), (i2, j2), color, 1)
    for y in range(y_start, y_stop + y_step, y_step):
        for x in range(x_start, x_stop, x_step):
            s1, i1, j1 = camera_convert.space2img(camera_state, x, y)
            s2, i2, j2 = camera_convert.space2img(camera_state, x + x_step, y)
            if s1 or s2:
                cv2.line(image, (i1, j1), (i2, j2), color, 1)


if __name__ == "__main__":

    camera_state = camera_convert.CameraState((100, 0, -90), (70, 0), (64, 50), (640, 480))

    repository_path = os.path.dirname(os.path.realpath(__file__)) + '/../..'
    if mode == 'file':
        for image_index in range(100):
            filename = repository_path + '/assets/openCV_pic/version' + read_version + '/' + str(
                image_index) + '.jpg'
            if not os.path.isfile(filename):
                print('cannot open ' + filename)
                continue
            image = cv2.imread(filename)

            process(image, True)
            cv2.waitKey()
    if mode == 'camera':
        c = Camera()
        for image_index in range(100):
            image = c.capture()
            filename = repository_path + '/assets/openCV_pic/version' + write_version + '/' + str(
                image_index) + '.jpg'
            cv2.imwrite(filename, image)
            process(image, True)
            cv2.waitKey(500)
