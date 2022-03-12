import qrcode
from PIL import Image
from random import sample
import os

def normal_gen_code():
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    code = sample(numbers, 20)
    return ''.join(code)

logo = Image.open('qrcode_logo.png')

basewidth = 50
wpercent = (basewidth/float(logo.size[0]))
hsize = int((float(logo.size[1])*float(wpercent)))

qr_big = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_H, border=1, box_size=60)

qr_big.add_data('https://nawaf.cf/')
qr_big.make()
img_qr_big = qr_big.make_image(fill_color='black', back_color='white')

pos = ((img_qr_big.size[0] - logo.size[0]) // 2, (img_qr_big.size[1] - logo.size[1]) // 2)

img_qr_big.paste(logo, pos, mask=logo)

filename = f'{normal_gen_code()}.png'

img_qr_big.save(filename)

a = open('qrcode1.png', 'rb')
print(a.read())

if os.path.exists(filename):
  os.remove(filename)