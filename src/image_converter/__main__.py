from PIL import Image
from os import listdir

def convert_image_to_webp(file):
    image = Image.open("img_input/{filename}".format(filename=file))
    image.save("img_output/{filename}.webp".format(filename=file), 'webp', optimize = True, quality = 60)

def main():
    for file in listdir('img_input'):
        print(str(file))
        convert_image_to_webp(file)

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print("Error")
        raise err
