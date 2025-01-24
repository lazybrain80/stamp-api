MAX_WM_LENGTH = 30
MAX_BIT_LENGTH = MAX_WM_LENGTH * 8
######################
# fixed watermark example
# watermark_str = "lazy-gCDBa6tPCxRPaPeV8KDqmq"
# lazy-gCDBa6tPCxRPaPeV8KDqmq -> 27
def remove_null_characters(input_string):
    return input_string.replace('\0', '')


def make_fixed_watermark(watermark_str: str):
    #사용자 입력에는 공백을 워터마크로 허용하지 않음
    fixed_wm = watermark_str.replace(" ", "")
    wm_length = len(fixed_wm)
    if wm_length < MAX_WM_LENGTH:
        fixed_wm = f"{fixed_wm}" + ('\0' * (MAX_WM_LENGTH - wm_length))
    elif wm_length > MAX_WM_LENGTH:
        fixed_wm = fixed_wm[:MAX_WM_LENGTH]

    return fixed_wm
