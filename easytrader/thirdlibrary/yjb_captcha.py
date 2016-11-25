from PIL import Image,ImageEnhance,ImageFilter,ImageDraw
import json,requests
#
# function of calcThreshold, binaryzation copy from
# this function copy from https://github.com/StandOpen/python_certify
def calcThreshold(im):
    L = im.convert('L').histogram()
    sum = 0
    threshold = 0
    for i in range(len(L)):
        sum += L[i]
        if sum >= 260:
            threshold = i
            break
    return threshold

def binaryzation(im,threshold = 90):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    imgry = im.convert('L')
    imout = imgry.point(table,'1')
    return imout

class YJBCaptcha(object):
    startPoint=(7,3)
    fontSize=(9,13)
    spaceWidth=4

    def __init__(self, imagePath):
        img=Image.open(imagePath)
        threshold = calcThreshold(img)
        if len(imagePath)>0:
            self.img= binaryzation(img, threshold)
        else:
            raise EOFError("captcha image file not found")

        self.count=4

    def pos(self, id):
        fontWidth, fontHeight = self.fontSize
        startX, startY = self.startPoint
        x=startX + (id - 1) * (self.spaceWidth + fontWidth)
        return (x, startY)

    def region(self, id):
        fontWidth, fontHeight = self.fontSize
        x,y=self.pos(id)
        return (x,y, x+fontWidth, y+fontHeight)

    def crop(self, id):
        return self.img.crop(self.region(id))

    def string(self):
        retNumber=""
        for id in range(4):
            maxValue=0
            maxNumber=0

            d = json.loads(YJBCaptcha.captchaTemplate())
            for number in range(10):
                matchedPoint = 0
                totalPoint = 0
                for y in range(13):
                    lineMatchedCount=0
                    line = d[str(number)][str(y+1)]
                    for x in range(len(line)):
                        ## sum total blackcount
                        if line[x] == 1:
                            totalPoint+=1

                        ## if image's point is black
                        picColor=1-self.crop(id+1).getpixel((x,y))
                        if picColor == line[x] and picColor==1:
                            lineMatchedCount+=1

                    ## if match rate > 0.5 then this line score will be fully added
                    if float(lineMatchedCount)/float(totalPoint) > 0.5:
                        matchedPoint += lineMatchedCount
                    else:
                        matchedPoint += lineMatchedCount*0.5

                if float(matchedPoint)/float(totalPoint) > maxValue:
                    maxValue = float(matchedPoint)/float(totalPoint)
                    maxNumber=number

            retNumber+=str(maxNumber)

        if len(retNumber)!=4:
            retNumber=""

        return retNumber

    def show(self):
        self.img.show()

    @staticmethod
    def captchaTemplate():
        return """{
        "0": {
            "1":  [0, 0, 0, 1, 1, 1, 0, 0, 0],
            "2":  [0, 1, 1, 1, 0, 0, 1, 1, 0],
            "3":  [0, 1, 1, 1, 0, 0, 1, 1, 0],
            "4":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "5":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "6":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "7":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "8":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "9":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "10": [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "11": [0, 1, 1, 1, 0, 0, 1, 1, 0],
            "12": [0, 1, 1, 1, 0, 0, 1, 1, 0],
            "13": [0, 0, 0, 1, 1, 1, 0, 0, 0]
        },
        "1": {
            "1":  [0, 0, 0, 1, 1, 1, 0, 0, 0],
            "2":  [0, 1, 1, 1, 1, 1, 0, 0, 0],
            "3":  [0, 1, 1, 1, 1, 1, 0, 0, 0],
            "4":  [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "5":  [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "6":  [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "7":  [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "8":  [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "9":  [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "10": [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "11": [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "12": [0, 1, 1, 1, 1, 1, 1, 1, 1],
            "13": [0, 1, 1, 1, 1, 1, 1, 1, 1]
        },
        "2": {
            "1":  [0, 1, 1, 1, 1, 0, 0, 0, 0],
            "2":  [1, 1, 1, 1, 1, 1, 1, 0, 0],
            "3":  [1, 0, 0, 0, 0, 0, 1, 1, 0],
            "4":  [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "5":  [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "6":  [0, 0, 0, 0, 0, 1, 1, 0, 0],
            "7":  [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "8":  [0, 0, 0, 1, 1, 0, 0, 0, 0],
            "9":  [0, 0, 1, 1, 0, 0, 0, 0, 0],
            "10": [0, 1, 1, 0, 0, 0, 0, 0, 0],
            "11": [1, 1, 0, 0, 0, 0, 0, 0, 0],
            "12": [1, 1, 1, 1, 1, 1, 1, 1, 0],
            "13": [1, 1, 1, 1, 1, 1, 1, 1, 0]
        },
        "3": {
            "1":  [0, 1, 1, 1, 1, 1, 0, 0, 0],
            "2":  [1, 1, 1, 1, 1, 1, 0, 0, 0],
            "3":  [1, 0, 0, 0, 0, 0, 1, 1, 0],
            "4":  [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "5":  [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "6":  [0, 0, 0, 0, 0, 1, 1, 0, 0],
            "7":  [0, 1, 1, 1, 1, 1, 0, 0, 0],
            "8":  [0, 1, 1, 1, 1, 1, 0, 0, 0],
            "9":  [0, 0, 0, 0, 0, 1, 1, 1, 0],
            "10": [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "11": [1, 0, 0, 0, 0, 0, 1, 1, 0],
            "12": [1, 1, 1, 1, 1, 1, 1, 0, 0],
            "13": [0, 1, 1, 1, 1, 1, 0, 0, 0]
        },
        "4": {
            "1":  [0, 0, 0, 0, 0, 1, 1, 0, 0],
            "2":  [0, 0, 0, 0, 1, 1, 1, 0, 0],
            "3":  [0, 0, 0, 0, 1, 1, 1, 0, 0],
            "4":  [0, 0, 0, 1, 1, 1, 1, 0, 0],
            "5":  [0, 0, 1, 1, 0, 1, 1, 0, 0],
            "6":  [0, 0, 1, 1, 0, 1, 1, 0, 0],
            "7":  [0, 1, 1, 0, 0, 1, 1, 0, 0],
            "8":  [0, 1, 1, 0, 0, 1, 1, 0, 0],
            "9":  [1, 1, 1, 1, 1, 1, 1, 1, 1],
            "10": [1, 1, 1, 1, 1, 1, 1, 1, 1],
            "11": [0, 0, 0, 0, 0, 1, 1, 0, 0],
            "12": [0, 0, 0, 0, 0, 1, 1, 0, 0],
            "13": [0, 0, 0, 0, 0, 1, 1, 0, 0]
        },
        "5": {
            "1":  [1, 1, 1, 1, 1, 1, 1, 1, 0],
            "2":  [1, 1, 1, 1, 1, 1, 1, 1, 0],
            "3":  [1, 1, 0, 0, 0, 0, 0, 0, 0],
            "4":  [1, 1, 0, 0, 0, 0, 0, 0, 0],
            "5":  [1, 1, 0, 0, 0, 0, 0, 0, 0],
            "6":  [1, 1, 1, 1, 1, 0, 0, 0, 0],
            "7":  [1, 1, 1, 1, 1, 1, 1, 0, 0],
            "8":  [0, 0, 0, 0, 0, 1, 1, 1, 0],
            "9":  [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "10": [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "11": [1, 0, 0, 0, 0, 1, 1, 1, 0],
            "12": [1, 1, 1, 1, 1, 1, 1, 0, 0],
            "13": [0, 1, 1, 1, 1, 1, 0, 0, 0]
        },
        "6": {
            "1":  [0, 0, 0, 1, 1, 1, 1, 0, 0],
            "2":  [0, 0, 1, 1, 1, 1, 1, 1, 0],
            "3":  [0, 1, 1, 0, 0, 0, 0, 0, 0],
            "4":  [0, 1, 1, 0, 0, 0, 0, 0, 0],
            "5":  [1, 1, 0, 0, 0, 0, 0, 0, 0],
            "6":  [1, 1, 0, 1, 1, 1, 1, 0, 0],
            "7":  [1, 1, 1, 1, 1, 1, 1, 1, 0],
            "8":  [1, 1, 1, 0, 0, 0, 1, 1, 1],
            "9":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "10": [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "11": [0, 1, 1, 0, 0, 0, 0, 1, 1],
            "12": [0, 1, 1, 1, 1, 1, 1, 1, 0],
            "13": [0, 0, 0, 1, 1, 1, 1, 0, 0]
        },
        "7": {
            "1":  [0, 1, 1, 1, 1, 1, 1, 1, 1],
            "2":  [0, 1, 1, 1, 1, 1, 1, 1, 1],
            "3":  [0, 0, 0, 0, 0, 0, 0, 1, 1],
            "4":  [0, 0, 0, 0, 0, 0, 0, 1, 0],
            "5":  [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "6":  [0, 0, 0, 0, 0, 1, 1, 0, 0],
            "7":  [0, 0, 0, 0, 0, 1, 0, 0, 0],
            "8":  [0, 0, 0, 0, 1, 1, 0, 0, 0],
            "9":  [0, 0, 0, 0, 1, 0, 0, 0, 0],
            "10": [0, 0, 0, 1, 1, 0, 0, 0, 0],
            "11": [0, 0, 0, 1, 1, 0, 0, 0, 0],
            "12": [0, 0, 1, 1, 0, 0, 0, 0, 0],
            "13": [0, 0, 1, 1, 0, 0, 0, 0, 0]
        },
        "8": {
            "1":  [0, 0, 1, 1, 1, 1, 1, 0, 0],
            "2":  [1, 1, 1, 1, 1, 1, 1, 1, 0],
            "3":  [1, 1, 0, 0, 0, 0, 1, 1, 0],
            "4":  [1, 1, 0, 0, 0, 0, 1, 1, 0],
            "5":  [1, 1, 1, 0, 0, 0, 1, 0, 0],
            "6":  [0, 0, 1, 1, 1, 1, 1, 0, 0],
            "7":  [0, 0, 1, 1, 1, 1, 1, 0, 0],
            "8":  [0, 1, 1, 0, 0, 1, 1, 1, 0],
            "9":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "10": [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "11": [1, 1, 0, 0, 0, 0, 1, 1, 1],
            "12": [0, 1, 1, 1, 1, 1, 1, 1, 0],
            "13": [0, 0, 1, 1, 1, 1, 1, 0, 0]
        },
        "9": {
            "1":  [0, 0, 1, 1, 1, 1, 0, 0, 0],
            "2":  [0, 1, 1, 1, 1, 1, 1, 1, 0],
            "3":  [1, 1, 1, 0, 0, 0, 1, 1, 0],
            "4":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "5":  [1, 1, 0, 0, 0, 0, 0, 1, 1],
            "6":  [1, 1, 1, 0, 0, 1, 1, 1, 1],
            "7":  [0, 1, 1, 1, 1, 1, 1, 1, 1],
            "8":  [0, 0, 1, 1, 1, 1, 0, 1, 1],
            "9":  [0, 0, 0, 0, 0, 0, 0, 1, 1],
            "10": [0, 0, 0, 0, 0, 0, 1, 1, 0],
            "11": [0, 1, 0, 0, 0, 0, 1, 1, 0],
            "12": [0, 1, 1, 1, 1, 1, 1, 0, 0],
            "13": [0, 0, 1, 1, 1, 1, 0, 0, 0]
        }
    }"""

