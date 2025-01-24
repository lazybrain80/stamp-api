import cv2
import pywt
import numpy as np
from scipy.fft import dctn, idctn
from scipy.linalg import svd
from .common import (
    ALPHA,
    crop_to_even,
    restore_original_size,
    subband_diag,
    text_to_image
)


class StampOperator:
    def __init__(self):
        pass

    def stamp(self, original_img: cv2.typing.MatLike, text_watermark: str):
        # read and cvt image
        _ycrcb_img = cv2.cvtColor(
                original_img,
                cv2.COLOR_BGR2YCrCb
            )
        _img_y, _img_cr, _img_cb = cv2.split(_ycrcb_img)
        _img_y = _img_y.astype(np.float32)
        _img_cr = _img_cr.astype(np.float32)
        _img_cb = _img_cb.astype(np.float32)

        _croped_img, _bottom_rest, _right_rest = crop_to_even(_img_cb)

        _ori_ll, (_ori_lh, _ori_hl, _ori_hh) = pywt.dwt2(_croped_img, 'haar')

        _ori_u, _ori_s, _ori_v  = svd(dctn(_ori_ll, norm='ortho'), full_matrices=True)

        _wm_height, _wm_width  = _ori_ll.shape[:2]

        # 텍스트 데이터를 이미지로 변환
        _wm_text_image, bit_count = text_to_image(text_watermark, _wm_width, _wm_height)
        
        _gap = 0
        if _wm_width != _wm_height:
            _gap = abs(_wm_width - _wm_height)

        _wm_u, _wm_s, _wm_v = svd(_wm_text_image, full_matrices=True)
        _wm_ori_s = _ori_s + ALPHA * _wm_s
        stamp_info = (_wm_u, _wm_v, _ori_s)
        #svd 복원
        _wm_ori_s = subband_diag(_wm_ori_s, _wm_width, _wm_height, _gap)
        _wm_ori_ll = _ori_u @ _wm_ori_s @ _ori_v

        # idctn
        _wm_ori_ll = idctn(_wm_ori_ll, norm='ortho')
        _wm_ori_cb = pywt.idwt2(( _wm_ori_ll, ( _ori_lh, _ori_hl, _ori_hh)), 'haar')
        _wm_ori_cb = restore_original_size(_wm_ori_cb, _bottom_rest, _right_rest)
        
        return cv2.cvtColor(
            cv2.merge((_img_y.astype(np.uint8), _img_cr.astype(np.uint8), _wm_ori_cb.astype(np.uint8)))
            , cv2.COLOR_YCrCb2BGR
        ), stamp_info