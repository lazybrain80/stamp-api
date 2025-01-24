from .img_division.basic_000 import Stamper


async def stamp_image_basic_000(
	original_image,
	watermark_image,
):
    stamp_machine = Stamper()
    stamp_machine.set_original_image(original_image)
    stamp_machine.set_watermark_image(watermark_image)
    return stamp_machine.stamp_watermark()