import cv2
import numpy as np

from scipy.linalg import svd
from .common import (
    ALPHA,
    SCRAMBLE_KEY,
    image_scramble,
    watermark_level,
    decomposition,
    reconstruction
)


class Stamper:
    def __init__(self):
        self.img_b = None
        self.img_g = None
        self.img_r = None

        self.img_y = None
        self.img_cr = None
        self.img_cg = None
        self.wm_gray = None

        self.img_height = 0
        self.img_width = 0
        self.possibe_watermark_height = 0
        self.possibe_watermark_width = 0
        self.level_r = 0
        pass

    def set_original_image(self, original):
        # Ensure the image has three channels
        if original.shape[2] == 4:  # If the image has an alpha channel
            original = cv2.cvtColor(original, cv2.COLOR_BGRA2BGR)

        self.img_height , self.img_width = original.shape[:2]

        if self.img_height < 128 or self.img_width < 128:
            raise ValueError("Image height and width must be at least 512 pixels")
        
        # split channels
        self.img_b, self.img_g, self.img_r = cv2.split(original)
        
        # convert to YCrCb color space
        _ycrcb_img = cv2.cvtColor(original, cv2.COLOR_BGR2YCrCb, original)
        # split channels
        self.img_y, self.img_cr, self.img_cb = cv2.split(_ycrcb_img)

        # limit watermark size
        self.possibe_watermark_height = self.img_height // 8
        self.possibe_watermark_width = self.img_width // 8
        pass

    def set_watermark_image(self, watermark):
        # Ensure the watermark has three channels
        if watermark.shape[2] == 4:  # If the image has an alpha channel
            watermark = cv2.cvtColor(watermark, cv2.COLOR_BGRA2BGR)

        _wm_height, _wm_width = watermark.shape[:2]

        # check limit watermark size
        if ( _wm_height > self.possibe_watermark_height
            or _wm_width > self.possibe_watermark_width):
            raise ValueError("Watermark height and width must be at most 1/8 of the image height and width")
        
        # calculate watermark level
        self.level_r = watermark_level(
            self.img_height, self.img_width, _wm_height, _wm_width
        )

        _wm_gray_image = cv2.cvtColor(watermark, cv2.COLOR_BGR2GRAY)

        # scramble watermark
        self.wm_gray = image_scramble(_wm_gray_image, SCRAMBLE_KEY)
        pass

    def stamp_watermark(self):
        wm_svds = ()

        img = self.img_y
        wm = self.wm_gray

        _decomositions = []
        d_target = img
        for _ in range(self.level_r):
            LL, LH, HL, HH = decomposition(d_target)
            _decomositions.append((LL, LH, HL, HH))
            d_target = LL
        
        _stamp_height, _stamp_width = wm.shape[:2]
        _paper_height, _paper_width = d_target.shape[:2]
        _paper_h_rest, _paper_w_rest = [], []

        # 도장찍을 영역만 남긴다.
        if _paper_height > _stamp_height:
            _paper_h_rest = d_target[_stamp_height:, :]
            d_target = d_target[:_stamp_height, :]
        
        if _paper_width > _stamp_width:
            _paper_w_rest = d_target[:, _stamp_width:]
            d_target = d_target[:, :_stamp_width]
        
        # 도장 너비, 넢이가 다른 경우를 대비하여 간격을 계산
        _gap = 0
        if _stamp_height != _stamp_width:
            _gap = abs(_stamp_height - _stamp_width)

        _u, _s, _vt = svd(d_target, full_matrices=True)
        _wm_u, _wm_s, _wm_vt = svd(wm, full_matrices=True)

        wm_svds = (_wm_u, _wm_vt, _s)

        # stamping watermark
        _new_s = _s + ALPHA * _wm_s

        # 1치원 배열을 대각 행렬로 변환
        _new_s_diag = np.diag(_new_s)

        # 도장 너비, 높이가 다른 경우 대각 행렬을 패딩
        # svd 결과가 자동으로 만들어주지 않아서 직접 만들어줘야함
        if _stamp_height > _stamp_width:
            _new_s_diag = np.pad(_new_s_diag, ((0, _gap), (0, 0)), 'constant', constant_values=0)
        elif _stamp_height < _stamp_width:
            _new_s_diag = np.pad(_new_s_diag, ((0, 0), (0, _gap)), 'constant', constant_values=0)

        _stamped_LL = _u @ _new_s_diag @ _vt
        
        # 도장찍은 영역을 복원
        if len(_paper_w_rest):
            _stamped_LL = np.concatenate((_stamped_LL, _paper_w_rest), axis=1)
        if len(_paper_h_rest):
            _stamped_LL = np.concatenate((_stamped_LL, _paper_h_rest), axis=0)
        
        # 이미지 복원
        for _, LH, HL, HH in reversed(_decomositions):
            _stamped_LL = reconstruction(_stamped_LL, LH, HL, HH)

        return wm_svds, cv2.cvtColor(
                cv2.merge((_stamped_LL, self.img_cr, self.img_cb))
                , cv2.COLOR_YCrCb2BGR
            )