from pytube import YouTube
import matplotlib.pyplot as plt
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
import numpy as np

LINK = "https://www.youtube.com/watch?v=7tXsC8YlCq8"
AUDIO_FILE = "audio_clip.mp3"
WYNIK = "wynik.txt"
PIERWSZA_RAMKA = 300000
LICZBA_RAMEK = 100000

#POBIERANIE FILMU I KONWERSJA DO PLIKU MP3
def generator(link, outputfile):
    yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    stream = yt.streams.get_highest_resolution()
    filename = stream.download()
    clip = VideoFileClip(filename)
    clip.audio.write_audiofile(outputfile)
    clip.close()

#MIESZANIE BITÓW WEDŁUG WZORU
"""
x1, x2
x1, x3, x2
x1, x4, x3, x5, x2
x1, x6, x4, x7, x3, x8, x5, x9, x2 
etc
"""
def mix_bits(input_bits):
    if(len(input_bits)<3):
        return input_bits
    
    mixed_bits = [input_bits[0],input_bits[1]]
    curentstep=2
    while(len(mixed_bits)<len(input_bits)):
        a=len(mixed_bits)-1
        b=0
        if(curentstep+a>len(input_bits)):
            a=len(input_bits)-curentstep
        for i in range(a):
            mixed_bits.insert(b*2+1, input_bits[curentstep])
            b=b+1
            curentstep=curentstep+1

    return mixed_bits

#WYKONYWANIE FUNKCJI XOR NA KAŻDYCH KOLEJNYCH 2 BITACH(TABLICA NA WYJŚCIU JEST 2 RAZY KRÓTSZA OD TABLICY NA WEJŚCIU)
def xor_operation(input_bits):
    result = []
    for i in range(0, len(input_bits), 2):
        result.append(input_bits[i] ^ input_bits[i+1])
    return result

#WPISANIE 4 NAJMNIEJ ZNACZĄCYCH BITÓW LICZBY DO TABLICY
def int_to_bits(n):
    n = n & 0xF
    bit_array = [int(bit) for bit in bin(n)[2:]]
    while len(bit_array) < 4:
        bit_array.insert(0, 0)
    return bit_array

#KONWERSJA TABLICY BITÓW NA TABLICE 8-BITOWYCH LICZB CAŁKOWITYCH
def bits_to_ints(bit_array):
    num_bits = len(bit_array)
    num_ints = num_bits // 8
    int_array = []

    for i in range(num_ints):
        start_index = i * 8
        end_index = start_index + 8
        segment = bit_array[start_index:end_index]
        segment_value = int("".join(map(str, segment)), 2)
        int_array.append(segment_value)
    return int_array

#KONWERSJA TABLICY BITÓW NA LICZBĘ CAŁKOWITĄ
def bits_to_int(bit_array):
    bit_string = ''.join(str(bit) for bit in bit_array)
    value = int(bit_string, 2)
    return value

#WYDOBYWANIE SAMEJ TABLICY BITÓW BEZ POSTPROCESIINGU
def no_postprocessing(num_of_values, input_values, start_value):
    result = []
    for i in range(num_of_values):
        bit_tab = int_to_bits(input_values[start_value+i])
        result.extend(bit_tab)
    return result

#MIESZANIE I WYKONYWANIE FUNKCJI XOR NA KAŻDEJ RAMCE OSOBNO
def quick_postprocessing(num_of_values, input_values, start_value):
    result=[]
    for i in range(num_of_values):
        bit_tab = int_to_bits(input_values[start_value+i])
        mixed_segment = mix_bits(bit_tab)
        xored_segment = xor_operation(mixed_segment)
        result.extend(xored_segment)
    return result

#MIESZANIE I WYKONYWANIE FUNKCJI XOR NA WSZYSTKICH RAMKACH RAZEM
def long_postprocessing(num_of_values, input_values, start_value):
    result = []
    for i in range(num_of_values):
        bit_tab = int_to_bits(input_values[start_value+i])
        result.extend(bit_tab)
    mixed_segment = mix_bits(result)
    xored_segment = xor_operation(mixed_segment)
    return xored_segment

#generator(LINK,AUDIO_FILE)
audio = AudioSegment.from_file(AUDIO_FILE, format="mp3")
frames = audio.get_array_of_samples()

num_of_values = LICZBA_RAMEK
start = PIERWSZA_RAMKA

values = bits_to_ints(no_postprocessing(num_of_values, frames, start))
quick_result = bits_to_ints(quick_postprocessing(num_of_values, frames, start))
long_result = bits_to_ints(long_postprocessing(num_of_values, frames, start))


#RYSOWANIE WYNIKÓW

plt.subplot(3, 2, 1)
plt.scatter(range(len(values)), values, s=1)
plt.title('BRAK POSTPROCESSINGU - WYKRES')

plt.subplot(3, 2, 2)
probability1 = np.ones_like(values)/len(values)
plt.hist(values, weights = probability1, bins = 256)
plt.title('BRAK POSTPROCESSINGU - HISTOGRAM')

plt.subplot(3, 2, 3)
plt.scatter(range(len(quick_result)), quick_result, s=1)
plt.title('KRÓTKI POSTPROCESSING - WYKRES')

plt.subplot(3, 2, 4)
probability2 = np.ones_like(quick_result)/len(quick_result)
plt.hist(quick_result, weights = probability2, bins = 256)
plt.title('KRÓTKI POSTPROCESSING - HISTOGRAM')

plt.subplot(3, 2, 5)
plt.scatter(range(len(long_result)), long_result, s=1)
plt.title('DŁUGI POSTPROCESSING - WYKRES')

plt.subplot(3, 2, 6)
probability3 = np.ones_like(long_result)/len(long_result)
plt.hist(long_result, weights = probability3, bins = 256)
plt.title('DŁUGI POSTPROCESSING - HISTOGRAM')

plt.show()