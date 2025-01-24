import cv2
import numpy as np
import pickle

from scipy.linalg import svd
from .common import (
    ALPHA,
    SCRAMBLE_KEY,
    inverse_image_scramble,
    decomposition,
    watermark_level
)


class StampValidater:
    def __init__(self):
        self.wm_img_y = None
        self.stamp_height = 0
        self.stamp_width = 0
        self.lever_r = 0
        self.wm_u = None
        self.wm_vt = None
        self.origin_s = None
        pass

    def prepare(self, wm_image, validater):
        # Ensure the image has three channels
        if wm_image.shape[2] == 4:
            wm_image = cv2.cvtColor(wm_image, cv2.COLOR_BGRA2BGR)

        _wm_img_height, _wm_img_width = wm_image.shape[:2]

        self.wm_img_y ,_ ,_ = cv2.split(
            cv2.cvtColor(wm_image, cv2.COLOR_BGR2YCrCb, wm_image)
        )

        self.wm_u, self.wm_vt, self.origin_s = validater

        self.stamp_height, self.stamp_width = self.wm_u.shape[0], self.wm_vt.shape[0]

        self.level_r = watermark_level(
            _wm_img_height, _wm_img_width, self.stamp_height, self.stamp_width
        )

        pass

    def extract_watermark(self):
        
        d_target = self.wm_img_y.copy()
        for _ in range(self.level_r):
            LL, _, _, _ = decomposition(d_target)
            d_target = LL
        
        _paper_height, _paper_width = d_target.shape[:2]
        # 도장찍힌 영역을 예상하여 나머지 부분을 제거
        if _paper_height > self.stamp_height:
            d_target = d_target[:self.stamp_height, :]
        
        if _paper_width > self.stamp_width:
            d_target = d_target[:, :self.stamp_width]

        # 복원 시 도장 너비, 높이가 다른 경우를 대비하여 간격을 계산
        _gap = 0
        if self.stamp_height != self.stamp_width:
            _gap = abs(self.stamp_height - self.stamp_width)

        _, _m_s, _ = svd(d_target, full_matrices=True)
        
        # watermark estimation
        _estimated_wm_s = (_m_s - self.origin_s) / ALPHA

        # 복원 시 도장 너비, 높이가 다른 경우 대각 행렬을 패딩
        _estimated_wm_s_diag = np.diag(_estimated_wm_s)
        if self.stamp_height > self.stamp_width:
            _estimated_wm_s_diag = np.pad(_estimated_wm_s_diag, ((0, _gap), (0, 0)), 'constant', constant_values=0)
        elif self.stamp_height < self.stamp_width:
            _estimated_wm_s_diag = np.pad(_estimated_wm_s_diag, ((0, 0), (0, _gap)), 'constant', constant_values=0)

        # 도장 추출
        _estimated_wm = self.wm_u @ _estimated_wm_s_diag @ self.wm_vt
        return inverse_image_scramble(_estimated_wm, SCRAMBLE_KEY)
