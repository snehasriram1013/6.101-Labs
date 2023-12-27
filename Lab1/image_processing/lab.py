"""
6.101 Lab 1:
Image Processing
"""

#!/usr/bin/env python3

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


# turns list of pixels into 2d array(better representation, easier to work with)
def list_to_table(image):
    arr = [
        [0] * image["height"] for _ in range(image["width"])
    ]  # Create independent rows
    index = 0
    for row in range(image["width"]):
        for col in range(image["height"]):
            arr[row][col] = image["pixels"][index]
            index += 1
    return arr


def get_index(image, row, col):
    return ((row) * image["width"]) + (col)


def get_pixel(image, row, col):
    return image["pixels"][get_index(image, row, col)]


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


def inverted(image):
    return apply_per_pixel(image, lambda color: (255 - color))


# HELPER FUNCTIONS


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
    #kernel is a 2d array representation, as this will math most closely with the 
    #matrix representation shown in the lab writeup, and it is easiest to iterate
    #through and keep track of
    corr_pixels = []
    for xrow in range(image["height"]):
        for xcol in range(image["width"]):
            # calc index and initialize correlation var
            corr = 0
            for k_row in range(len(kernel)):
                for k_col in range(len(kernel[0])):
                    #iterates over each pixel, then each kernel and performs linear correlation
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
    
    #checks if pixels in range, and if they are valid ints
    #if not, reassigns or rounds values
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
        #use given formula
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
        #use given formula, do not round/clip until end
        pix = round(math.sqrt((o1[i] ** 2) + (o2[i] ** 2)))
        edge_pix.append(pix)

    edge_im = {"height": image["height"], "width": image["width"], "pixels": edge_pix}
    round_and_clip_image(edge_im)
    return edge_im


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
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


# pytest test.py -k test_inverted


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
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

    print(5)
