import numpy as np
import math

from scipy.fft import dctn, idctn

ALPHA = 0.1
SCRAMBLE_KEY = 20131227

def image_scramble(image, key):
    height, width = image.shape
    flat_img = image.reshape(-1)
    total_pixels = flat_img.shape[0]

    np.random.seed(key)

    random_indices = np.random.permutation(total_pixels)
    return flat_img[random_indices].reshape(height, width)


def inverse_image_scramble(image, key):
    height, width = image.shape
    flat_scrambled = image.reshape(-1)
    total_pixels = flat_scrambled.shape[0]

    np.random.seed(key)

    original_indices = np.random.permutation(total_pixels)
    restored_img = np.zeros_like(flat_scrambled)

    for i in range(total_pixels):
        restored_img[original_indices[i]] = flat_scrambled[i]

    return restored_img.reshape(height, width)


def decomposition(image):
        _height, _width = image.shape[:2]
        col_dct = dctn(image, axes=(0,), norm='ortho')

        _height_half = _height // 2
        _low_freq = col_dct[:_height_half, :]
        _high_freq = col_dct[_height_half:, :]

        L_idct = idctn(_low_freq, axes=(0,), norm='ortho')
        H_idct = idctn(_high_freq, axes=(0,), norm='ortho')

        L_dct = dctn(L_idct, axes=(1,), norm='ortho')
        H_dct = dctn(H_idct, axes=(1,), norm='ortho')

        width_half = _width // 2
        return (
            idctn(L_dct[:, :width_half], axes=(1,), norm='ortho') # LL
            , idctn(L_dct[:, width_half:], axes=(1,), norm='ortho') # LH
            , idctn(H_dct[:, :width_half], axes=(1,), norm='ortho') # HL
            , idctn(H_dct[:, width_half:], axes=(1,), norm='ortho') # HH
        )


def reconstruction(LL, LH, HL, HH):
    _ll_height, _ll_width = LL.shape[:2]
    _lh_height, _lh_width = LH.shape[:2]
    _hl_height, _hl_width = HL.shape[:2]
    _hh_height, _hh_width = HH.shape[:2]

    LL_dct = dctn(LL, norm='ortho')
    LH_dct = dctn(LH, norm='ortho')
    HL_dct = dctn(HL, norm='ortho')
    HH_dct = dctn(HH, norm='ortho')

    LL_pad = np.pad(LL_dct, ((0, _hl_height), (0, _lh_width)), mode='constant')
    LH_pad = np.pad(LH_dct, ((0, _hh_height), (_ll_width, 0)), mode='constant')
    HL_pad = np.pad(HL_dct, ((_ll_height, 0), (0, _hh_width)), mode='constant')
    HH_pad = np.pad(HH_dct, ((_lh_height, 0), (_hl_width, 0)), mode='constant')

    return (idctn(LL_pad, norm='ortho')
            + idctn(LH_pad, norm='ortho')
            + idctn(HL_pad, norm='ortho')
            + idctn(HH_pad, norm='ortho'))


def watermark_level(img_height, img_width, wm_height, wm_width):
    _img_ratio = 0
    if wm_height < wm_width:
        _img_ratio = img_width / wm_width
    else:
        _img_ratio = img_height / wm_height
    return math.floor(math.log2(_img_ratio))