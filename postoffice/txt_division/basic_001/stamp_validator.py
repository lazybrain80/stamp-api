import cv2
import pywt
import numpy as np

from scipy.fft import dctn
from scipy.linalg import svd
from .common import (
    ALPHA,
    crop_to_even,
    subband_diag,
    image_to_text
)

class StampValidator:
    def __init__(self) -> None:
        pass

    def validate(self, wm_img: cv2.typing.MatLike, embedding_len: int, validater: any ) -> str:
        _wm_u, _wm_v, _ori_s = validater
        _, _, _channel_watermarked  = cv2.split(
            cv2.cvtColor(
                wm_img,
                cv2.COLOR_BGR2YCrCb
            ))
        _croped_wm_img, _, _ = crop_to_even(_channel_watermarked)
        _wm_ll, (_, _, _) = pywt.dwt2(_croped_wm_img, 'haar')

        _wm_height, _wm_width = _wm_ll.shape[:2]
        _gap = 0
        if _wm_height != _wm_width:
            _gap = abs(_wm_height - _wm_width)

        
        _, _twm_s, _  = svd(dctn(_wm_ll, norm='ortho'), full_matrices=True)
        _recon_wm_s = (_twm_s - _ori_s) / ALPHA
        _recon_wm_s = subband_diag(_recon_wm_s, _wm_width, _wm_height, _gap)
        _recon_wm_img = _wm_u @ _recon_wm_s @ _wm_v

        # 이미지를 텍스트로 변환
        _detectd_wm_text = image_to_text(_recon_wm_img, embedding_len)
        return _detectd_wm_text
