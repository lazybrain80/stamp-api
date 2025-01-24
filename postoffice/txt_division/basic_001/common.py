import numpy as np

def crop_to_even(array):
    height, width = array.shape[:2]
    new_height = height if height % 2 == 0 else height - 1
    new_width = width if width % 2 == 0 else width - 1
    cropped_array = array[:new_height, :]
    bottom_array = array[new_height:, :]
    right_array = cropped_array[:, new_width:]
    cropped_array = cropped_array[:, :new_width]
    return cropped_array, bottom_array, right_array

def restore_original_size(cropped_array, bottom_array, right_array):
    _height, _width = cropped_array.shape[:2]
    bottom_padding = bottom_array.shape[0]
    right_padding = right_array.shape[1]

    restored_array = np.zeros((_height + bottom_padding, _width + right_padding), dtype=cropped_array.dtype)
    restored_array[:_height, :_width] = cropped_array
    if bottom_padding > 0:
        restored_array[_height:, :_width] = bottom_array
    
    if right_padding > 0:
        restored_array[:, _width:] = right_array
    return restored_array

def text_to_bin(text):
    text = text.encode('utf-8', 'ignore')
    return list(np.unpackbits(
        np.array([n for n in text], dtype=np.uint8)
    ))

def bin_to_text(bin_array):
    byte_array = np.packbits(bin_array).tobytes()
    text = byte_array.decode('utf-8', 'ignore')
    return text

def split_into_blocks(array, block_size):
    _height, _width = array.shape[:2]
    shape = (_height // block_size, _width // block_size, block_size, block_size)
    strides = (array.strides[0] * block_size, array.strides[1] * block_size, array.strides[0], array.strides[1])
    blocks = np.lib.stride_tricks.as_strided(array, shape=shape, strides=strides)
    return blocks

def reconstruct_from_blocks(blocks):
    block_height, block_width, block_size, _ = blocks.shape
    array_height = block_height * block_size
    array_width = block_width * block_size
    array = blocks.transpose(0, 2, 1, 3).reshape(array_height, array_width)
    return array

ALPHA = 0.9

def text_to_image(text, width=512, height=512):
    # 텍스트 데이터를 UTF-8 인코딩을 사용하여 이진 데이터로 변환
    binary_data = ''.join(format(byte, '08b') for byte in text.encode('utf-8'))
    # 이진 데이터를 N번 반복하여 512x512 크기의 배열로 변환
    binary_data_repeated = (binary_data * ((width * height) // len(binary_data) + 1))[:width * height]
    binary_array = np.array([int(bit) for bit in binary_data_repeated], dtype=np.uint8)
    binary_array = binary_array.reshape((height, width))
    
    # 배열을 OpenCV를 사용하여 이미지로 변환
    image = binary_array * 16  # 0과 1을 0과 255로 변환하여 흑백 이미지 생성
    return image, len(binary_data)

def image_to_text(image, bit_count=512):
    # 이미지를 이진 데이터로 변환 (128 이하이면 0, 128 이상이면 1)
    binary_array = (image >= 2).astype(np.uint8).flatten()  # 128 이하이면 0, 128 이상이면 1로 변환하여 1차원 배열로 변환
    binary_data = ''.join(map(str, binary_array))
    
    txt_idx = 0
    text_bin = np.zeros(bit_count)
    for bit in binary_data:
        if bit == '1':
            text_bin[txt_idx] += 1
        
        txt_idx += 1
        if txt_idx == bit_count:
            txt_idx = 0

    text_bin = np.where((text_bin/bit_count) >= 0.5, 1, 0)
    byte_array = np.packbits(text_bin).tobytes()
    text = byte_array.decode('utf-8', errors='ignore')

    # 패딩 제거
    text = text.rstrip('\x00')
    return text

def subband_diag(s, width, height, gap):
    s = np.diag(s)
    if height > width:
        s = np.pad(s, ((0, gap), (0, 0)), 'constant', constant_values=0)
    elif height < width:
        s = np.pad(s, ((0, 0), (0, gap)), 'constant', constant_values=0)
    return s