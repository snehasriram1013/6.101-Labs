"""
6.101 Lab 0:
Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Returns a new sound containing the samples of the original in reverse
    order, without modifying the input sound.

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary with the samples in reversed order
    """
    backwards = sound["samples"][:]
    backwards.reverse()
    newSound = {"rate": sound["rate"], "samples": backwards}

    return newSound


def mix(sound1, sound2, p):
    """
    

    Parameters
    ----------
    sound1 : sound
    sound2 : sound
    p : float 0<x<1

    Returns
    -------
    new sound

    """
    # mix 2 good sounds
    if (
        ("rate" not in sound1)
        or ("rate" not in sound2)
        or (sound1["rate"] != sound2["rate"])
    ):
        print("no")
        return None

    r = sound1["rate"]  # get rate
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]
    if len(sound1) < len(sound2):
        new_list = len(sound1)
    elif len(sound2) < len(sound1):
        new_list = len(sound2)
    elif len(sound1) == len(sound2):
        new_list = len(sound1)
    else:
        print("whoops")
        return None


    s_list = []
    x = 0
    while x <= new_list:
        s2, s1 = p * sound1[x], sound2[x] * (1 - p)
        s_list.append(s1 + s2)  # add sounds
        x += 1
        if x == new_list:  # end
            break

    return {"rate": r, "samples": s_list}  # return new sound


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """
    delay_rate = round(delay*sound["rate"]) #calculate delay rate using formula
    #create empty list of sound+echos length
    newsound = [0]*((delay_rate*num_echoes)+len(sound["samples"])) 
    #copy sound
    original = sound["samples"][:]
    
    #iterate through num_echos
    for i in range(num_echoes+1):
        #iterate through samples
        for j in range(len(sound["samples"])):
            #update values in newsound list according to scaled echo values
            newsound[(delay_rate*i)+j] += original[j]*(scale**i)
            
    return {"rate": sound["rate"], "samples": newsound}
            
        
        
        
        


def pan(sound):
    left = sound["left"]
    right = sound["right"]
    left_len = len(left)
    new_left = []
    new_right = []
    
    for i in range(len(right)):
        new_right.append(right[i]*(i/(left_len-1)))
        new_left.append(left[i]*(1-(i/(left_len-1))))
    return {"rate": sound["rate"], "left": new_left, "right": new_right}


def remove_vocals(sound):
    left = sound["left"]
    right = sound["right"]
    new_samp = []
    for i in range(len(right)):
        new_samp.append(left[i]-right[i])
    return {"rate": sound["rate"], "samples": new_samp}
        
        


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    hello = load_wav("sounds/hello.wav")
# #reversing mystery
#     mystery = load_wav("sounds/mystery.wav")
#     mystery2 = backwards(mystery)
#     write_wav(mystery2, "mystery_reversed.wav")
    
# #mixing synth and water
#     synth = load_wav("sounds/synth.wav")
#     water = load_wav("sounds/water.wav")
#     synthWater = mix(synth, water, 0.2)
#     write_wav(synthWater, "synthWater.wav")

#     # write_wav(backwards(hello), "hello_reversed.wav")
    
# #pan car noises
#     car = load_wav("sounds/car.wav", stereo=True)
#     panCar = pan(car)
#     write_wav(panCar, "panCar.wav")
    
# #removing vocals
#     mountain = load_wav("sounds/lookout_mountain.wav", stereo=True)
#     removeMount = remove_vocals(mountain)
#     write_wav(removeMount, "removeMount.wav")
    

chord = load_wav("sounds/chord.wav")
echoChord = echo(chord, 5, 0.3, 0.6)
write_wav(echoChord, "echoChord.wav")
