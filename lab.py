#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 21:00:25 2023

@author: snehasriram
"""

"""
6.101 Lab 2:
Image Processing 2
"""

#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image
import random

# Lab 1 stuff


def get_index(image, row, col):
    return ((row) * image["width"]) + (col)


def get_pixel(image, row, col):
    return image["pixels"][get_index(image, row, col)]


def set_pixel(image, row, col, color):
    image["pixels"][get_index(image, row, col)] = color


def apply_per_pixel(image, func):
    """
    applies specified function to each pixel in pixel_list

    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * (image["height"] * image["width"]),
    }

    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result

    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [],
    }
    for col in range(image["height"]):
        for row in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
        set_pixel(result, row, col, new_color)
    return result


def get_pixel_k(image, row, col, boundary):
    """
    implementation of get_pixel with an additional parameter: boundary_behavior
    If row/col is out of bounds, this function will return pixel value according
    to that boundary behavior(it will wrap it around, extend the last pixel, or
    just return zero)

    """
    if 0 < row < image["height"] and 0 < col < image["width"]:
        return get_pixel(image, row, col)
    elif boundary == "extend":
        row1 = max(0, row)
        row2 = min(row1, image["height"] - 1)

        col1 = max(0, col)
        col2 = min(col1, image["width"] - 1)
        return get_pixel(image, row2, col2)
    elif boundary == "wrap":
        row1 = row % image["height"]
        col1 = col % image["width"]
        return get_pixel(image, row1, col1)
    else:
        if boundary == "zero":
            return 0


def inverted(image):
    return apply_per_pixel(image, lambda color: (255 - color))


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    kernel: 2d array
    """
    if boundary_behavior not in ["zero", "extend", "wrap"]:
        return None
    # kernel is a 2d array representation, as this will math most closely with the
    # matrix representation shown in the lab writeup, and it is easiest to iterate
    # through and keep track of
    corr_pixels = []
    for xrow in range(image["height"]):
        for xcol in range(image["width"]):
            # calc index and initialize correlation var
            corr = 0
            for k_row in range(len(kernel)):
                for k_col in range(len(kernel[0])):
                    # iterates over each pixel, then each kernel and performs linear correlation
                    x = xrow + k_row - len(kernel) // 2
                    y = xcol + k_col - len(kernel[0]) // 2
                    corr += kernel[k_row][k_col] * get_pixel_k(
                        image, x, y, boundary_behavior
                    )
            corr_pixels.append(corr)
    new_im = {"height": image["height"], "width": image["width"], "pixels": corr_pixels}

    # round_and_clip_image(new_im)
    return new_im


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """

    # checks if pixels in range, and if they are valid ints
    # if not, reassigns or rounds values
    for i in range(len(image["pixels"])):
        if image["pixels"][i] > 255:
            image["pixels"][i] = 255
        elif image["pixels"][i] < 0:
            image["pixels"][i] = 0
        else:
            image["pixels"][i] = round(image["pixels"][i])


# FILTERS
def n_kernel(n):
    """

    Takes in an int in and creates an n by n kernel, with each cell containing
    the same value, all of which sum to one

    """
    arr = [[0] * n for _ in range(n)]  # Create independent rows
    for row in range(len(arr)):
        for col in range(len(arr[0])):
            arr[row][col] = 1 / (n**2)
    return arr


def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    # then compute the correlation of the input image with that kernel

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    kernel = n_kernel(kernel_size)
    new_im = correlate(image, kernel, "extend")
    round_and_clip_image(new_im)
    return new_im


def sharpened(image, n):
    """
    Parameters
    ----------
    image : input image dictionary
    n : int n, height and width of kernel

    Returns
    -------
    sharp_im : returns a new image

    Return a new image representing the result of using the given formula(2I-B)
    applied to every pixel in the given input image

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    """
    blur_im = blurred(image, n)
    blur_pix = blur_im["pixels"][:]
    pix = image["pixels"][:]
    sharp_pix = []
    for i in range(len(pix)):
        # use given formula
        sharp_pix.append(2 * pix[i] - blur_pix[i])

    sharp_im = {"height": image["height"], "width": image["width"], "pixels": sharp_pix}

    round_and_clip_image(sharp_im)
    return sharp_im


def edges(image):
    """


    Parameters
    ----------
    image : image dictionary

    Returns
    -------
    returns a new image

    Enhances the edges visible in the input image, and creates a new enhanced
    image

    """

    kernel1 = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    kernel2 = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]

    o1 = correlate(image, kernel1, "extend")["pixels"][:]
    o2 = correlate(image, kernel2, "extend")["pixels"][:]

    edge_pix = []

    for i in range(len(o1)):
        # use given formula, do not round/clip until end
        pix = round(math.sqrt((o1[i] ** 2) + (o2[i] ** 2)))
        edge_pix.append(pix)

    edge_im = {"height": image["height"], "width": image["width"], "pixels": edge_pix}
    round_and_clip_image(edge_im)
    return edge_im


# VARIOUS FILTERS (LAB 2 STUFF BEGINS)


def color_to_greyscale(image):
    """
    takes in an image dictionary and converts the pixel list of tuples into
    three lists of each val in tuple
    """
    red = []
    green = []
    blue = []
    for t in image["pixels"]:
        red.append(t[0])
        green.append(t[1])
        blue.append(t[2])

    return (red, green, blue)


def greyscale_to_color(i1, i2, i3):
    """
    turns 3 greyscale images to one color image
    """
    ans = []
    for index in range(len(i1)):
        ans.append((i1[index], i2[index], i3[index]))

    return ans


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """

    def apply_color_greyscale(image):
        color_list = color_to_greyscale(image)
        grey_list = []
        for i in range(len(color_list)):
            im = {
                "height": image["height"],
                "width": image["width"],
                "pixels": color_list[i],
            }
            grey_list.append(filt(im))
        new_pix = greyscale_to_color(
            grey_list[0]["pixels"], grey_list[1]["pixels"], grey_list[2]["pixels"]
        )
        return {"height": image["height"], "width": image["width"], "pixels": new_pix}

    return apply_color_greyscale


def make_blur_filter(kernel_size):
    """
    returns blur filter that only takes in one variable

    """
    def apply_color_greyscale_blur(image):
        return blurred(image, kernel_size)

    return apply_color_greyscale_blur


def make_sharpen_filter(kernel_size):
    """
    returns sharpen filter that only takes in one variable

    """
    def apply_color_greyscale_sharpen(image):
        return sharpened(image, kernel_size)

    return apply_color_greyscale_sharpen


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """

    def cascade(image):
        im = {
            "height": image["height"],
            "width": image["width"],
            "pixels": image["pixels"],
        }
        for filt in filters:
            im = filt(im)
        return im

    return cascade


# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving_helper(image):
    """
    one iteration of seamcarving as described in the lab writeup

    """
    #Make a greyscale copy
    grey = greyscale_image_from_color_image(image)
    #Compute energy map
    energy = compute_energy(grey)
    #Compute a "cumulative energy map"
    cem = cumulative_energy_map(energy)
    #Find the minimum-energy seam. 
    seam = minimum_energy_seam(cem)
    #Remove the computed path
    new_im = image_without_seam(image, seam)
    
    return new_im

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    new_im = image
    for i in range(ncols):
        new_im = seam_carving_helper(new_im)
        
    return new_im


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    new_pix = []
    for t in image["pixels"]:
        new_pix.append(round(0.299 * t[0] + 0.587 * t[1] + 0.114 * t[2]))
    return {"height": image["height"], "width": image["width"], "pixels": new_pix}


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


# pytest lab.py test_seam_carving_helpers.py


def cumulative_energy_map(energy):
    """
    where the value at each position is the total energy of the lowest-energy 
    path from the top of the image to that pixel.

    """
    # create 2d array cumulative map
    cumulative_map = [[0] * energy["width"] for _ in range(energy["height"])]

    # Cumulative map range 0 to 1
    for col in range(energy["width"]):
        cumulative_map[0][col] = get_pixel(energy, 0, col) + min(
            get_pixel_k(energy, 0, col, "zero"),
            get_pixel_k(energy, 0, max(col - 1, 0), "zero"),
            get_pixel_k(energy, 0, min(col + 1, energy["width"] - 1), "zero"),
        )

    # Cumulative map range 1 to height of energy map
    for row in range(1, energy["height"]):
        for col in range(energy["width"]):
            # check if left and right cols are out of bounds
            left = max(col - 1, 0)
            right = min(col + 1, energy["width"] - 1)

            cumulative_map[row][col] = get_pixel(energy, row, col) + min(
                cumulative_map[row - 1][col],
                cumulative_map[row - 1][left],
                cumulative_map[row - 1][right],
            )

    # Flatten the cumulative_map into 1d array to make it the same as usual pixels list
    cem = [ele for row in cumulative_map for ele in row]

    return {"height": energy["height"], "width": energy["width"], "pixels": cem}


def min_index(row, cem):
    """
    Returns the minimum value, row, and index of a pixel in given row

    """
    two_d_array = [
        cem["pixels"][i * cem["width"] : (i + 1) * cem["width"]]
        for i in range(cem["height"])
    ]
    min_val = float("inf")
    index = -1

    for col in range(cem["width"]):
        if two_d_array[row][col] < min_val:
            min_val = two_d_array[row][col]
            index = col

    return (min_val, row, index)


def minimum_energy_seam(cem):
    """
    First, the minimum value pixel in the bottom row of the cumulative energy map is located. 
    This is the bottom pixel of the minimum seam. The seam is then traced back up to the top r
    ow of the cumulative energy map by following the adjacent pixels with the smallest cumulative 
    energies.
    """
    index_list = []

    # Create pixels 2D array for easier indexing
    two_d_array = [
        cem["pixels"][i * cem["width"] : (i + 1) * cem["width"]]
        for i in range(cem["height"])
    ]

    # Find the minimum-energy pixel in the bottom row
    min_bottom = min_index(cem["height"] - 1, cem)
    index_list.append(min_bottom)

    for row in range(
        cem["height"] - 2, -1, -1
    ):  # Iterate from second-to-last row to the first row
        _, _, col = index_list[-1]
        left = max(col - 1, 0)
        right = min(col + 1, cem["width"] - 1)

        min_val, _, col = min(
            (two_d_array[row][left], row, left),
            (two_d_array[row][col], row, col),
            (two_d_array[row][right], row, right),
        )
        print(left, col, right)

        index_list.append((min_val, row, col))

    indexes = []
    for t in index_list:
        indexes.append(t[1] * cem["width"] + t[2])  # Compute the flat list index

    print("Minimum Energy Seam:")
    print(indexes)

    return indexes


            
def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """ 
    new_pix = image["pixels"][:]
    seam.sort()
    seam = seam[::-1]
    for index in seam:
        new_pix.pop(index)
    return {"height": image["height"], "width": image["width"]-1, "pixels": new_pix}


# CUSTOM FILTER


def custom_filter(image, height, width):
    """
    Given a greyscale image and a desired height and width for a new image to be
    generated, returns a new image (without modifying the original) that contains
    randomly chosen pixels from the input image.
    """
    len_pix = len(image["pixels"])
    new_pix = []
    for i in range((height - 1) * (width - 1)):
        index = random.randrange(0, len_pix)
        new_pix.append(image["pixels"][index])

    return {"height": height, "width": width, "pixels": new_pix}


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    #     i = {
    #     "height": 3,
    #     "width": 2,
    #     "pixels": [(255, 0, 0), (39, 143, 230),
    #                (255, 191, 0), (0, 200, 0),
    #                (100, 100, 100), (179, 0, 199)],
    # }
    #     caillou = load_color_image("test_images/caillou.jpeg")

    #     filter1 = color_filter_from_greyscale_filter(edges)
    #     filter2 = make_blur_filter(5)
    #     filt = filter_cascade([filter1, filter1, filter2, filter1])

    #     filtered = custom_filter(caillou, 50, 50)

    #     save_color_image(filtered, "filtered5.png", mode="PNG")
    print(1)
