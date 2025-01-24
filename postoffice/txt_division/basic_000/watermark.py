import struct
import numpy as np

from .dwtDctSvd import EmbedDwtDctSvd

class TextWatermarkEncoder(object):
    def __init__(self, content=b''):
        seq = np.array([n for n in content], dtype=np.uint8)
        self._watermarks = list(np.unpackbits(seq))
        self._wmLen = len(self._watermarks)

    def encode(self, cv2Image, **configs):
        height, width = cv2Image.shape[:2]
        if height * width < 256 * 256:
            raise RuntimeError('image too small, should be larger than 256x256')

        embed = EmbedDwtDctSvd(self._watermarks, wmLen=self._wmLen, **configs)
        return embed.encode(cv2Image)


class TextWatermarkDecoder(object):
    def __init__(self, length=0):
        self._wmLen = length
        pass

    def reconstruct_bytes(self, bits):
        nums = np.packbits(bits)
        bstr = b''
        for i in range(self._wmLen//8):
            bstr += struct.pack('>B', nums[i])
        return bstr

    def reconstruct(self, bits):
        if len(bits) != self._wmLen:
            raise RuntimeError('bits are not matched with watermark length')
        return self.reconstruct_bytes(bits)

    def decode(self, cv2Image, **configs):
        height, width = cv2Image.shape[:2]
        if height * width < 256 * 256:
            raise RuntimeError('image too small, should be larger than 256x256')

        embed = EmbedDwtDctSvd(watermarks=[], wmLen=self._wmLen, **configs)
        return self.reconstruct(embed.decode(cv2Image))
