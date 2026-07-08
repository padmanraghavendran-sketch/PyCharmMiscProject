import qrcode
url = "https://www.youtube.com/watch?v=QDia3e12czc"
file_path = "qrcode.png"
qr = qrcode.QRCode()
qr.add_data(url)
img = qr.make_image()
img.save(file_path)

