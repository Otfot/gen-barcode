import os

import cv2
import execjs
import numpy as np


class DefectSetMetaclass(type):
    """This metaclass to record the defect function and use it later

    :param type: metaclass
    :type type: class
    :return: class
    :rtype: [type]
    """

    def __new__(cls, name, base, attrs):
        count = 0
        attrs['__DefectSpecies__'] = []
        for k, v in attrs.items():
            if 'add_' in k:
                attrs['__DefectSpecies__'].append(k)
                count += 1
        attrs['__DefectSpeciesCount__'] = count
        return type.__new__(cls, name, base, attrs)


class DefectSet(metaclass=DefectSetMetaclass):
    """This class include all the defect create function

    :param metaclass: to record the defect function for callback, defaults to DefectSetMetaclass
    :type metaclass: [type], optional
    :return: no
    :rtype: None
    """

    def __init__(self, dir_path, path, barcode_option):
        """

        :param path: include all needed path
        :type path: dict
        :param barcode_option: jsbarcode configuration
        :type barcode_option: dict
        """
        self.path = path

        # complie the js file and called by python later
        self.gen_pic = execjs.compile(open(dir_path+'/gencode.js').read())

        # config the barcode style
        self.barcode_option = barcode_option
        self.white_color = [255, 255, 255]
        self.black_color = [0, 0, 0]

    def setenv(self):
        self.raw_name_list = os.listdir(self.path['raw'])
        self.raw_path_list = [self.path['raw'] +
                              raw_name for raw_name in self.raw_name_list]

    def run(self, callback):
        """this function run the defect function by str

        :param callback: the defect function name
        :type callback: function
        :return: the created defect image
        :rtype: cv-8u
        """
        print('Callback', callback)
        return eval("self.{}()".format(callback))

    def add_raw_pic(self, num, bit):
        """create the raw image

        :param num: the number image will be created
        :type num: int
        :param bit: the barcode information bit
        :type bit: int
        """
        self.gen_pic.call("gen", num, bit, self.barcode_option)

    def add_salt_white(self, salt_num=3000):
        """Add the salt to the image

        :param salt_num: the salt number, defaults to 3000
        :type salt_num: int, optional
        :return: the Cv image obj
        :rtype: cv_8u
        """
        img = self.img
        rows, cols, _ = img.shape
        for i in range(salt_num):
            x = np.random.randint(
                self.barcode_option['margin'],
                rows - self.barcode_option['margin'])
            y = np.random.randint(
                self.barcode_option['margin'],
                cols - self.barcode_option['margin'])
            img[x, y] = self.white_color
        # img = Image.fromarray(img)
        return img

    def add_salt_black(self, salt_num=100):
        """add the salt to the image

        :param salt_num: the black salt number, defaults to 100
        :type salt_num: int, optional
        :return: CV image obj
        :rtype: cv_8u
        """
        img = self.img
        rows, cols, _ = img.shape
        for i in range(salt_num):
            # make optimization for different barcode type
            if self.barcode_option['format'] == 'EAN13':
                x = np.random.randint(
                    self.barcode_option['margin'],
                    rows - self.barcode_option['margin'])
                y = np.random.randint(
                    self.barcode_option['margin'] + 10,
                    cols - self.barcode_option['margin'])
            else:
                x = np.random.randint(
                    self.barcode_option['margin'],
                    rows - self.barcode_option['margin'])
                y = np.random.randint(
                    self.barcode_option['margin'],
                    cols - self.barcode_option['margin'])
            img[x, y] = self.black_color
        return img

    def add_white_line(self, white_line_num=14):
        img = self.img
        rows, cols, _ = img.shape
        # do processing only for the barcode section
        for i in range(white_line_num):
            x = np.random.randint(
                self.barcode_option['margin'],
                rows - self.barcode_option['margin'])
            # y=np.random.randint(0,cols)
            img[x, :] = self.white_color
        return img

    def add_cover(self):
        """make cover defect to image

        :return: cv image obj
        :rtype: cv_8u
        """
        # the follow will change the self.img obj , so make a copy
        img = self.img.copy()

        rows, cols, _ = img.shape

        # random create the crop_width and cover_width
        # crop_width = np.random.randint(60, 120)
        crop_y = np.random.randint(
            cols / 4, cols - self.barcode_option['margin'])
        cover_width = np.random.randint(10, 25)

        # random generate the crop location y in a specified range

        crop_img = img[:, -crop_y:]
        crop_img = crop_img.copy()
        img[:, -crop_y:] = self.white_color
        # rows,cols,channels = crop_img.shape
        self.img = crop_img

        # make the crop_img incline
        crop_img = self.add_incline(cover=True)

        # magic methods
        roi = img[:, -crop_y - cover_width:-cover_width]
        crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(crop_img_gray, 200, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        img_bg = cv2.bitwise_and(roi, roi, mask=mask)
        crop_img_fg = cv2.bitwise_and(crop_img, crop_img, mask=mask_inv)

        dst = cv2.add(img_bg, crop_img_fg)
        img[:, -crop_y - cover_width:-cover_width] = dst
        return img

    def add_incline(self, cover=False):
        """make the image incline

        :param cover: for add_cover function, defaults to False
        :type cover: bool, optional
        :return: cv image obj
        :rtype: cv_8u
        """
        img = self.img
        while True:
            # make some optimization for add_cover
            if cover:
                angle = np.random.randint(-3, 3)
            else:
                angle = np.random.randint(-10, 10)
            if angle != 0:
                break
        center_point = (img.shape[1] / 2, img.shape[0] / 2)
        rotate_mat = cv2.getRotationMatrix2D(center_point, angle, 1.0)
        img = cv2.warpAffine(
            img, rotate_mat, (img.shape[1], img.shape[0]), borderValue=(
                255, 255, 255))
        return img

    def add_translate(self):
        """make picture translate

        :return: cv image obj
        :rtype: cv_8u
        """
        img = self.img
        rows, cols, _ = img.shape
        x = np.random.randint(-100, 100)
        y = np.random.randint(-50, 50)
        translate_mat = np.float32([[1, 0, x], [0, 1, y]])
        # 仿射变换
        img = cv2.warpAffine(
            img, translate_mat, (cols, rows), borderValue=(
                255, 255, 255))
        return img
