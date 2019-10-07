import os
import shutil
import datetime
import zipfile

import cv2
import fire

from defect_class import DefectSet

os.environ["NODE_PATH"] = os.getcwd() + "/node_modules"

dir_path = os.path.dirname(os.path.abspath(__file__))

path = {
    'raw': dir_path + '/raw/',
    'cooked': dir_path + '/cooked/',
    'salt_black': dir_path + '/cooked/salt_black/',
    'salt_white': dir_path + '/cooked/salt_white/',
    'white_line': dir_path + '/cooked/white_line/',
    'incline': dir_path + '/cooked/incline/',
    'translate': dir_path + '/cooked/translate/',
    'cover': dir_path + '/cooked/cover/',
    'mix': dir_path + '/cooked/mix/',
    'tar': dir_path + '/tar/'
}


barcode_option = {
    "margin": 0,
    "marginLeft": 68,
    "marginRight": 68,
    "marginTop": 174,
    "marginBottom": 174,
    # 加数字减11
    "displayValue": "false",
    "format": ''
}


class GenDefect:
    """is class define some useful commands
    to generate the raw and defect barcode picture
    """

    def __init__(self, dir_path, path, barcode_option):
        """

        :param path: the project root path
        :type path: str
        :param barcode_option: the jsbarcode framwork configuration
        :type barcode_option: dict
        :param num2cmd: the table from number to the corresponding defect barcode
        :type num2cmd: dict
        """

        # the raw and defect barcode class
        self._defect_set = DefectSet(dir_path, path, barcode_option)

        self.num2cmd = ['raw', 'salt_white', 'salt_black', 'white_line',
                        'cover', 'incline', 'translate']
        # self.num2cmd = {
        #     '0': 'raw',
        #     '1': 'salt_white',
        #     '2': 'salt_black',
        #     '3': 'white_line',
        #     '4': 'incline',
        #     '5': 'translate',
        #     '6': 'cover'
        # }

    def show(self):
        """This function display all the defect barcode function
        """

        for i in range(self._defect_set.__DefectSpeciesCount__):
            print(self._defect_set.__DefectSpecies__[i])

    def genraw(self, num, bit=22, type='code128'):
        """
        This function is to generate the raw picture with kinds of barcode type

        :param num: the number of picture to create
        :type num: int
        :param bit: the number of the barcode information bit, defaults to None
        :type bit: int, optional
        :param type: the barcode type, defaults to 'code128'
        :type type: str, optional
        """
        # add the raw path and ran name list
        self._defect_set.setenv()
        # change the barcode type
        self._defect_set.barcode_option['format'] = type

        # create the barcode picture
        self._defect_set.add_raw_pic(num, bit)
        print(str(num) + ' raw picture was created.')

    def gen(self, types, num=None):
        """This function create the defect barcode image

        :param type: the defect type you want to create
        :type type: list, such as[1,2,3] or [2,3,4]
        :param num: the number image you want to create, defaults to None means create from all raw image
        :type num: int, optional
        """
        self._defect_set.setenv()
        # create different defect image by the specific type
        if len(self._defect_set.raw_path_list) == 0:
            self.genraw(10)
            self._defect_set.setenv()
        # print(type(types))
        for t in types:
            for index, raw_path in enumerate(
                    self._defect_set.raw_path_list[:num]):
                img = cv2.imread(raw_path)

                # the DefectSet class depends on the img obj to create
                # different defect image
                self._defect_set.img = img
                # run the defect function
                img = self._defect_set.run(
                    self._defect_set.__DefectSpecies__[int(t)])
                cv2.imwrite(
                    self._defect_set.path[self.num2cmd[int(t)]]
                    + self._defect_set.raw_name_list[index], img)

    def clean(self, target='all'):
        """clean all the created image

        :param target: different target means to clean different portion, defaults to 'all'
        :type target: str, optional
        """

        # clean all image include raw and cooked
        if target == 'all':
            shutil.rmtree(self._defect_set.path['cooked'])
            shutil.rmtree(self._defect_set.path['raw'])
            shutil.rmtree(self._defect_set.path['tar'])
            for k, v in self._defect_set.path.items():
                os.makedirs(v)

        # only clean cooked
        elif target == 'cooked':
            shutil.rmtree(self._defect_set.path['cooked'])
            for k, v in self._defect_set.path.items():
                if k == 'raw' or k == 'tar':
                    continue
                os.makedirs(v)

        # clean specific portion
        else:
            shutil.rmtree(self._defect_set.path[target])
            os.makedirs(self._defect_set.path[target])
    
    def create(self, target='all'):
        """create the directory

        :param target: different target means to create different portion, defaults to 'all'
        :type target: str, optional
        """

        #  create all dir
        if target == 'all':
            for k, v in self._defect_set.path.items():
                if not os.path.exists(v):
                    os.makedirs(v)

        # only create cooked
        elif target == 'cooked':
            for k, v in self._defect_set.path.items():
                if k == 'raw':
                    continue
                if not os.path.exists(v):
                    os.makedirs(v)

        # create specific portion
        else:
            if not os.path.exists(self._defect_set.path[target]):
                os.makedirs(self._defect_set.path[target])
            

    def genmix(self, types, num=None):
        """create the mix defect image

        :param types: defect type
        :type types: list
        :param num: the number to create image, defaults to None means to create from all the raw image
        :type num: int, optional
        """
        self._defect_set.setenv()
        # print(types, num)
        if len(self._defect_set.raw_path_list) == 0:
            self.genraw(10)
        for index, raw_path in enumerate(self._defect_set.raw_path_list[:num]):
            img = cv2.imread(raw_path)
            types.sort()
            # print(types)
            name = 'mix'
            for t in types:
                self._defect_set.img = img
                img = self._defect_set.run(
                    self._defect_set.__DefectSpecies__[t])
                name += '=' + self.num2cmd[t]

            name += '='
            cv2.imwrite(
                self._defect_set.path['mix']
                + name + self._defect_set.raw_name_list[index], img)
            print('The ' + str(index + 1) + ' image was created!')

    def tar(self, type):
        """compress the created raw and defect image to tar directory

        :param type: barcode tyep
        :type type: str
        """
        # cooked_name = './tar/' + type + '_cooked_' + \
        #     datetime.datetime.now().strftime('%Y_%b_%d_%H:%M')
        # raw_name = './tar/' + type + '_raw_' + \
        #     datetime.datetime.now().strftime('%Y_%b_%d_%H:%M')
        # cooked_name = './tar/'+type+'_cooked_'
        # raw_name = './tar/'+type+'_raw_'
        # shutil.make_archive(raw_name, 'gztar', '.', 'raw')
        # shutil.make_archive(cooked_name, 'gztar', '.', 'cooked')
        cmd = 'tar -zcf tar/data.tar.gz cooked/ raw/'
        os.system(cmd)

    def resraw(self):
        self._defect_set.setenv()
        for index, raw_path in enumerate(self._defect_set.raw_path_list[:]):
            img = cv2.imread(raw_path)
            img = self._defect_set.resize(img)
            img = self._defect_set.projection(img)
            img = self._defect_set.resize(img)
            
            cv2.imwrite(
                    self._defect_set.path[self.num2cmd[0]]
                    + self._defect_set.raw_name_list[index], img)




    def imginfo(self):
        self._defect_set.setenv()
        raw_path = self._defect_set.raw_path_list[0]
        img = cv2.imread(raw_path)
        rows, cols, _ = img.shape 
        print("rows=", rows, " cols=", cols)   

if __name__ == '__main__':

    gen_defect = GenDefect(dir_path, path, barcode_option)
    # use fire framework to create command line
    fire.Fire(gen_defect)
