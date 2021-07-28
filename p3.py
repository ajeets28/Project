import hashlib
import os
from Crypto.Cipher import AES
from PIL import Image
import math
from random import randrange, seed

def aes_encrypt_message(u,key,f):
    fin = open(f,'rb') 
    image = fin.read() 
    fin.close() 
    key=hashlib.sha256((str(key)).encode("utf-8")).digest()
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext,tag= cipher.encrypt_and_digest(image)

    path=os.path.join(u,"encrypt")
    file1=open(os.path.join(path,"out.png"),"wb")
    file2=open(os.path.join(path,"n.txt"),"wb")
    file2.write(nonce)
    file1.write(ciphertext)
    file1.close()
    file2.close()

def aes_decrypt_message(u,key,f):
    key=hashlib.sha256((str(key)).encode("utf-8")).digest()
    path=os.path.join(u,"encrypt")

    file1 = open(f,'rb') 
    file3=open(os.path.join(path,"n.txt"),"rb")
    image = file1.read() 
    nonce=file3.read()
    file1.close() 
    file3.close()

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(image)

    path=os.path.join(u,"decrypt")
    file1=open(os.path.join(path,"out.png"),"wb")
    file1.write(plaintext)
    file1.close()

def block1_encrypt_message(u,blksz,f):
    image = Image.open(f,"r")
    arr = image.load()

    def rot(A, n, x1, y1): 
        temple = []
        for i in range(n):
            temple.append([])
            for j in range(n):
                temple[i].append(arr[x1+i, y1+j])
        for i in range(n):
            for j in range(n):
                arr[x1+i,y1+j] = temple[n-1-i][n-1-j]

    
    xres,yres =image.size
    for i in range(2, blksz+1):
        for j in range(int(math.floor(float(xres)/float(i)))):
            for k in range(int(math.floor(float(yres)/float(i)))):
                rot(arr, i, j*i, k*i)
    for i in range(3, blksz+1):
        for j in range(int(math.floor(float(xres)/float(blksz+2-i)))):
            for k in range(int(math.floor(float(yres)/float(blksz+2-i)))):
                rot(arr, blksz+2-i, j*(blksz+2-i), k*(blksz+2-i))

    image.save(u)

def block2_encrypt_message(u,f):
    
    def number_of_colours(image):
        return len(set(list(image.getdata())))

    def create_region_lists(input_image, key_image, number_of_regions):
        template = create_template(input_image, key_image, number_of_regions)
        number_of_regions_created = len(set(template))
        region_lists = [[] for i in range(number_of_regions_created)]
        for i in range(len(template)):
            region = template[i]
            region_lists[region].append(i)
        odd_region_lists = [region_list for region_list in region_lists if len(region_list) % 2]
        for i in range(len(odd_region_lists) - 1):
            odd_region_lists[i].append(odd_region_lists[i + 1].pop())
        return region_lists

    def create_template(input_image, key_image, number_of_regions):
        if number_of_regions == 1:
            width, height = input_image.size
            return [0] * (width * height)
        else:
            resized_key_image = key_image.resize(input_image.size, Image.NEAREST)
            pixels = list(resized_key_image.getdata())
            pixel_measures = [measure(pixel) for pixel in pixels]
            distinct_values = list(set(pixel_measures))
            number_of_distinct_values = len(distinct_values)
            number_of_regions_created = min(number_of_regions, number_of_distinct_values)
            sorted_distinct_values = sorted(distinct_values)
            while True:
                values_per_region = (number_of_distinct_values / number_of_regions_created)
                value_to_region = {sorted_distinct_values[i]:int(i // values_per_region)for i in range(len(sorted_distinct_values))}
                pixel_regions = [value_to_region[pixel_measure]for pixel_measure in pixel_measures]
                if no_small_pixel_regions(pixel_regions,number_of_regions_created):
                    break
                else:
                    number_of_regions_created //= 2
            return pixel_regions

    def no_small_pixel_regions(pixel_regions, number_of_regions_created):
        counts = [0 for i in range(number_of_regions_created)]
        for value in pixel_regions:
            counts[value] += 1
        if all(counts[i] >= 256 for i in range(number_of_regions_created)):
            return True

    def shuffle(region_lists):
        for region_list in region_lists:
            length = len(region_list)
            for i in range(length):
                j = randrange(length)
                region_list[i], region_list[j] = region_list[j], region_list[i]


    def measure(pixel):
        if type(pixel) is int:
            return pixel
        else:
            r, g, b = pixel[:3]
            return r * 2999 + g * 5869 + b * 1151

    def swap_pixels(input_image, region_lists):
        pixels = list(input_image.getdata())
        for region in region_lists:
            for i in range(0, len(region) - 1, 2):
                pixels[region[i]], pixels[region[i+1]] = (pixels[region[i+1]],
                                                        pixels[region[i]])
        scrambled_image = Image.new(input_image.mode, input_image.size)
        scrambled_image.putdata(pixels)
        return scrambled_image
        
    key_image_filename=None
    number_of_regions=16777216
    input_image = Image.open(f)
    number_of_regions = min(int(number_of_regions),number_of_colours(input_image))
    if key_image_filename:
        key_image_path = os.path.abspath(key_image_filename)
        key_image = Image.open(key_image_path)
    else:
        key_image = None
        number_of_regions = 1
    region_lists = create_region_lists(input_image, key_image,number_of_regions)
    seed(0)
    shuffle(region_lists)
    output_image = swap_pixels(input_image, region_lists)
    output_image.save(u)
