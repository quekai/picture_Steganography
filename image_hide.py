
import PIL
from PIL import Image
import qrcode

class ImageMessageWriter(object):
    def __init__(self):
        self.image = None
        self.encodedImage = None
        self.image0End = None
        self.stringToEncode = ""
        self.qrimage = None



    def loadImage(self, image_or_path):
        if isinstance(image_or_path,Image.Image):
            self.image = image_or_path
        elif isinstance(image_or_path,str):
            self.image = Image.open(image_or_path)
        else:
            raise TypeError("Invalid parameter.")
        self.image0End = self.__generate_image0End()

    def getqrImage(self,message):
        img = qrcode.make(message)
        img.save('qrcode.png')
        self.qrimage = img



    def encode(self, message):
        if self.image is None or self.image0End is None:
            raise Exception("No image loaded.")
        if message is None:
            raise Exception("No message assigned.")

        self.stringToEncode = message
        messagesToEncode = ''.join(map(self.__char_to_bin, bytearray(message, 'utf-8')))
        if len(messagesToEncode) + 32 > len(self.image.getdata()) *8:
            raise Exception("Error: Can't encode more than" + len(self.image.getdata()) * 8 - 32 + "bits in current image.")
        encodedPixels = [];
        messageLength = ''.join(self.__char_to_bin(len(messagesToEncode)))
        messageLength = "0" * (32 - len(messageLength)) + messageLength
        lastIndex = 0

        for index, (r, g, b, t) in enumerate(list(self.image0End.getdata())):
            if(index < 8):
                encodedPixels.append((r + int(messageLength[index * 4]),
                                     g + int(messageLength[index * 4 + 1]),
                                      b + int(messageLength[index * 4 + 2]),
                                      t + int(messageLength[index *4 + 3])))
                continue
            if index * 4 -32 <len(messagesToEncode):
                encodedPixels.append((r + int(messagesToEncode[index * 4 - 32]),
                                     g + int(messagesToEncode[index * 4 + 1 - 32]),
                                      b + int(messagesToEncode[index * 4 + 2 - 32]),
                                      t + int(messagesToEncode[index * 4 + 3 - 32])))
            else:
                lastIndex = index
                break

        for index, (r, g, b, t) in enumerate(list(self.image.getdata())):
            if index >= lastIndex:
                encodedPixels.append((r, g, b, t))

        self.encodedImage = Image.new(self.image0End.mode, self.image0End.size)
        self.encodedImage.putdata(encodedPixels)

    def saveImage(self,filepath):
        if self.encodedImage is None:
            raise Warning("You didn't encode any message into this image.")
        else:
            self.encodedImage.save(filepath)


    def __generate_image0End(self):
        pixels = list(self.image.getdata())
        pixels0End = [(r>>1<<1, g>>1<<1, b>>1<<1, t>>1<<1) for (r, g, b, t) in pixels]
        image0End = Image.new(self.image.mode, self.image.size)
        image0End.putdata(pixels0End)
        return image0End

    @staticmethod
    def __char_to_bin(ch):
        ans = "0" * (10 - (len (bin(ch))))
        ans += bin(ch).replace('0b','')
        return ans

    def getTxtMessage(self,path):
        message = ''
        with open(path,encoding='utf8') as file_to_read:
            for line in file_to_read.readlines():
                message+=line
        return message

class ImageMessageReader(object):
    def __init__(self):
        self.image = None
        self.decodedMessage = None

    def loadImage(self, image_or_path):
        if isinstance(image_or_path,Image.Image):
            self.image = image_or_path
        elif isinstance(image_or_path,str):
            self.image = Image.open(image_or_path)
        else:
            raise TypeError("Invalid parameter.")

    def decode(self):
        pixels = list(self.image.getdata())
        bins = ''.join([str(int(r>>1<<1!=r))+str(int(g>>1<<1!=g))+str(int(b>>1<<1!=b))+str(int(t>>1<<1!=t)) for (r, g, b, t) in pixels])
        length = int(bins[:32], 2)
        self.decodedMessage = self.__utf2str_(bins[32:length+32])
        return self.decodedMessage

    def getMessage(self):
        if self.decodedMessage is None:
            raise Exception("Message is None. Check whether you have decoded.")
        return self.decodedMessage

    @staticmethod
    def __utf2str_(utf):
        i = 0
        ans = []
        _utf16rec8_ = lambda x, i: x[2:8] + (_utf16rec8_(x[8:], i - 1) if i > 1 else '') if x else ''
        _utf16rec16_ = lambda x, i: x[i + 1:8] + _utf16rec8_(x[8:], i - 1)
        while i + 1 < len(utf):
            chartype = utf[i:].index('0')
            length = chartype * 8 if chartype else 8
            ans.append(chr(int(_utf16rec16_(utf[i:i + length], chartype), 2)))
            i += length
        return ''.join(ans)




if __name__ == '__main__':
    textpath = 'testdata.txt'
    imgWriter = ImageMessageWriter()
    imgWriter.loadImage('testpicture.png')
    message = imgWriter.getTxtMessage(textpath)
    imgWriter.encode(message)
    imgWriter.saveImage('encodedPicture.png')
    imgReader = ImageMessageReader()
    imgReader.loadImage('encodedPicture.png')
    print(imgReader.decode())











