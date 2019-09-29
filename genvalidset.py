import os

import fire

defect_one = "python barcode.py gen '[1]'"
defect_two = "python barcode.py gen '[2]'"
defect_three = "python barcode.py gen '[3]'"
defect_four = "python barcode.py gen '[4]'"
defect_five = "python barcode.py gen '[5]'"
defect_six = "python barcode.py gen '[6]'"
defect_raw = "python barcode.py genraw"
clean = "python barcode.py clean"
clean_raw = "python barcode.py clean raw"
tar = "python barcode.py tar code128"
resize = 'python barcode.py resraw'
task = [defect_one, defect_two, defect_three,defect_four,defect_five, defect_six]

def gen(num):
    os.system(clean)   
    for t in task:
        # 生成原始图片
        os.system(defect_raw+ ' '+ str(num))
        print("已生成原始图片"+ str(num)+'张')
        # 生成特定缺陷图片
        os.system(t+ ' '+ str(num))
        print("已生成缺陷图片"+ str(num)+'张')
        # 清理原始图片
        os.system(clean_raw)
        
    # 生成原始图片样本
    os.system(defect_raw + ' '+ str(num))
    # os.system(resize)

    # #     # // 打包图片
    os.system(tar)
    # cmd = 'cd tar && tar -xf data.tar.gz'

    # os.system(cmd)
    print('数据集已打包完成')

if __name__ == '__main__':
    fire.Fire(gen)