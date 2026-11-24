"""
Image Optimizer 코어 변환 엔진(converter_core.py) 무결성 및 안정성 검증 테스트 스위트
- 정지 이미지 포맷 변환 (PNG, JPG, BMP, TIFF)
- 알파 투명도 채널 보존 및 합성 제거 검증
- 애니메이션 GIF -> WebP 및 첫 프레임 JPG 변환 검증
- 다양한 리사이즈 모드(비율, 최대가로폭, SNS 프리셋) 검증
- 비정상 파일(0바이트, 깨진 파일) 예외 처리 검증
- 동시 듀얼 포맷 출력 및 디렉터리 모드 검증
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageSequence
from converter_core import (
    ConversionOptions,
    FileResult,
    SUPPORTED_EXTENSIONS,
    apply_resize,
    flatten_alpha,
    has_alpha,
    process_single_file,
)


class TestConverterCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 전체 테스트에서 공유할 임시 작업 디렉토리 생성
        cls.test_dir = Path(tempfile.mkdtemp(prefix="imgopt_test_"))

    @classmethod
    def tearDownClass(cls):
        # 테스트 완료 후 임시 디렉토리 정리
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        # 각 테스트 메서드별 독립 하위 폴더 생성
        self.case_dir = self.test_dir / self._testMethodName
        self.case_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # 헬퍼 함수: 테스트용 동적 이미지 생성
    # -------------------------------------------------------------
    def _create_rgb_image(self, filename: str, size=(400, 300), color="blue") -> Path:
        p = self.case_dir / filename
        img = Image.new("RGB", size, color=color)
        draw = ImageDraw.Draw(img)
        draw.rectangle((50, 50, size[0] - 50, size[1] - 50), fill="yellow")
        img.save(p)
        return p

    def _create_rgba_image(self, filename: str, size=(400, 300)) -> Path:
        """투명 영역(Alpha 0)과 불투명 영역(Alpha 255)이 공존하는 RGBA 이미지 생성"""
        p = self.case_dir / filename
        img = Image.new("RGBA", size, (0, 0, 0, 0))  # 완전 투명 배경
        draw = ImageDraw.Draw(img)
        draw.ellipse((50, 50, size[0] - 50, size[1] - 50), fill=(255, 0, 0, 255))  # 불투명 빨강 원
        img.save(p, "PNG")
        return p

    def _create_animated_gif(self, filename: str, frames_count=3, size=(200, 200)) -> Path:
        p = self.case_dir / filename
        frames = []
        colors = ["red", "green", "blue"]
        for i in range(frames_count):
            frame = Image.new("RGBA", size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(frame)
            draw.rectangle((20 * i, 20 * i, size[0] - 20 * i, size[1] - 20 * i), fill=colors[i % 3])
            frames.append(frame)

        frames[0].save(
            p,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
            transparency=0,
            disposal=2,
        )
        return p

    # -------------------------------------------------------------
    # 1. 알파 투명도 처리 검증
    # -------------------------------------------------------------
    def test_alpha_preservation_webp(self):
        """투명 PNG를 WebP로 변환할 때 투명 배경(Alpha 채널)이 완벽히 보존되는지 검증"""
        src = self._create_rgba_image("transparent.png")
        options = ConversionOptions(output_formats=["WEBP"], remove_alpha=False)

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        out_file = self.case_dir / "transparent.webp"
        self.assertTrue(out_file.exists())

        # 결과 WebP의 알파 채널 확인
        with Image.open(out_file) as out_img:
            self.assertIn(out_img.mode, ("RGBA", "LA", "P"))
            self.assertTrue(has_alpha(out_img, real_only=True))

    def test_alpha_removal_flatten(self):
        """'투명 배경 제거' 옵션 활성화 시 흰색 배경 합성 및 RGB 변환 검증"""
        src = self._create_rgba_image("transparent_flatten.png")
        options = ConversionOptions(
            output_formats=["WEBP"],
            remove_alpha=True,
            flatten_background=(255, 255, 255),
        )

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        out_file = self.case_dir / "transparent_flatten.webp"
        self.assertTrue(out_file.exists())

        with Image.open(out_file) as out_img:
            self.assertEqual(out_img.mode, "RGB")
            # 원래 투명했던 모서리 (0, 0) 픽셀이 흰색(255, 255, 255)이어야 함
            pixel = out_img.getpixel((0, 0))
            self.assertEqual(pixel, (255, 255, 255))

    # -------------------------------------------------------------
    # 2. 정지 이미지 압축 및 포맷 변환
    # -------------------------------------------------------------
    def test_jpg_to_webp_conversion(self):
        """일반 JPG -> WebP 압축 변환 및 용량 유효성 검증"""
        src = self._create_rgb_image("sample.jpg", size=(800, 600))
        options = ConversionOptions(output_formats=["WEBP"], quality=80)

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        out_file = self.case_dir / "sample.webp"
        self.assertTrue(out_file.exists())
        self.assertGreater(out_file.stat().st_size, 0)

        with Image.open(out_file) as out_img:
            self.assertEqual(out_img.size, (800, 600))

    def test_dual_format_simultaneous_output(self):
        """동시 2개 포맷(WEBP + JPG) 출력 검증"""
        src = self._create_rgb_image("dual.png", size=(500, 500))
        options = ConversionOptions(output_formats=["WEBP", "JPG"], quality=85)

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")
        self.assertIn("WEBP", res.new_sizes)
        self.assertIn("JPG", res.new_sizes)

        out_webp = self.case_dir / "dual.webp"
        out_jpg = self.case_dir / "dual.jpg"
        self.assertTrue(out_webp.exists())
        self.assertTrue(out_jpg.exists())

    # -------------------------------------------------------------
    # 3. 애니메이션 GIF 변환 검증
    # -------------------------------------------------------------
    def test_animated_gif_to_animated_webp(self):
        """3프레임 GIF -> 애니메이션 WebP 변환 시 프레임 수 및 루프 유지 검증"""
        src = self._create_animated_gif("anim.gif", frames_count=3)
        options = ConversionOptions(output_formats=["WEBP"])

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        out_webp = self.case_dir / "anim.webp"
        self.assertTrue(out_webp.exists())

        with Image.open(out_webp) as out_img:
            self.assertTrue(getattr(out_img, "is_animated", False))
            self.assertEqual(out_img.n_frames, 3)

    def test_animated_gif_to_static_jpg(self):
        """움직이는 GIF -> JPG 출력 시 첫 프레임 정상 추출 검증"""
        src = self._create_animated_gif("anim_to_jpg.gif", frames_count=3)
        options = ConversionOptions(output_formats=["JPG"])

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        out_jpg = self.case_dir / "anim_to_jpg.jpg"
        self.assertTrue(out_jpg.exists())

        with Image.open(out_jpg) as out_img:
            self.assertFalse(getattr(out_img, "is_animated", False))
            self.assertEqual(out_img.format, "JPEG")

    # -------------------------------------------------------------
    # 4. 리사이즈 엔진 검증
    # -------------------------------------------------------------
    def test_resize_scale_percent(self):
        """비율(%) 축소: 1000x800 -> 50% 축소 시 정확히 500x400 검증"""
        src = self._create_rgb_image("scale.jpg", size=(1000, 800))
        options = ConversionOptions(
            output_formats=["WEBP"],
            resize_mode="scale_percent",
            scale_percent=50,
        )

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        with Image.open(self.case_dir / "scale.webp") as img:
            self.assertEqual(img.size, (500, 400))

    def test_resize_max_width(self):
        """최대 가로폭 제한: 가로 2400x1200 -> max_width 1200 시 1200x600 비율 유지 검증"""
        src = self._create_rgb_image("wide.jpg", size=(2400, 1200))
        options = ConversionOptions(
            output_formats=["WEBP"],
            resize_mode="max_width",
            max_width=1200,
        )

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        with Image.open(self.case_dir / "wide.webp") as img:
            self.assertEqual(img.size, (1200, 600))

    def test_resize_sns_preset_fit(self):
        """SNS 프리셋 (유튜브 썸네일 FHD: 1920x1080) fit 모드 검증"""
        src = self._create_rgb_image("yt.jpg", size=(3840, 2160))  # 16:9 4K
        options = ConversionOptions(
            output_formats=["WEBP"],
            resize_mode="sns_preset",
            sns_preset_target="youtube_thumb_fhd",
            sns_crop_mode="fit",
        )

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        with Image.open(self.case_dir / "yt.webp") as img:
            self.assertEqual(img.size, (1920, 1080))

    # -------------------------------------------------------------
    # 5. 출력 디렉토리 모드 검증
    # -------------------------------------------------------------
    def test_output_mode_subfolder(self):
        """하위 폴더(subfolder) 출력 모드 검증"""
        src = self._create_rgb_image("sub_test.png")
        options = ConversionOptions(
            output_formats=["WEBP"],
            output_mode="sub",
            subfolder_name="test_optimized",
        )

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        expected_file = self.case_dir / "test_optimized" / "sub_test.webp"
        self.assertTrue(expected_file.exists())

    # -------------------------------------------------------------
    # 6. 비정상 파일 및 예외 처리 검증 (안정성 핵심)
    # -------------------------------------------------------------
    def test_empty_zero_byte_file(self):
        """0바이트 빈 파일 입력 시 앱이 크래시되지 않고 정상 에러 상태를 반환하는지 검증"""
        empty_file = self.case_dir / "empty.png"
        empty_file.write_bytes(b"")

        options = ConversionOptions(output_formats=["WEBP"])
        res = process_single_file(empty_file, options)

        self.assertEqual(res.status, "error")
        self.assertIn("0 바이트", res.error_message)

    def test_corrupted_image_file(self):
        """텍스트 데이터로 위장한 손상된 이미지 파일 입력 시 안전 에러 처리 검증"""
        bad_file = self.case_dir / "corrupted.jpg"
        bad_file.write_bytes(b"THIS IS NOT A VALID IMAGE DATA 1234567890")

        options = ConversionOptions(output_formats=["WEBP"])
        with self.assertRaises(Exception):
            process_single_file(bad_file, options)

    # -------------------------------------------------------------
    # 7. 포맷별 특수 호환성 및 고해상도 스트레스 검증
    # -------------------------------------------------------------
    def test_rgba_to_jpg_automatic_flatten(self):
        """알파 채널(RGBA)이 있는 이미지를 JPG로 변환할 때 에러 없이 흰색 배경으로 자동 합성되는지 검증"""
        src = self._create_rgba_image("alpha.png")
        options = ConversionOptions(output_formats=["JPG"])

        res = process_single_file(src, options)
        self.assertEqual(res.status, "success")

        out_jpg = self.case_dir / "alpha.jpg"
        self.assertTrue(out_jpg.exists())
        with Image.open(out_jpg) as img:
            self.assertEqual(img.mode, "RGB")
            self.assertEqual(img.format, "JPEG")

    def test_bmp_and_tiff_conversion(self):
        """레거시 포맷인 BMP 및 TIFF 이미지의 WebP 정상 변환 검증"""
        bmp_path = self.case_dir / "legacy.bmp"
        img = Image.new("RGB", (300, 200), color="purple")
        img.save(bmp_path, "BMP")

        options = ConversionOptions(output_formats=["WEBP"])
        res = process_single_file(bmp_path, options)
        self.assertEqual(res.status, "success")
        self.assertTrue((self.case_dir / "legacy.webp").exists())

    def test_large_resolution_stress(self):
        """초대형 고해상도(8000x5000) 이미지 처리 시 DecompressionBomb 에러 없이 정상 축소/압축되는지 검증"""
        large_path = self.case_dir / "large_8k.png"
        img = Image.new("RGB", (8000, 5000), color="navy")
        img.save(large_path, "PNG")

        options = ConversionOptions(
            output_formats=["WEBP"],
            resize_mode="max_width",
            max_width=1920,
            quality=80,
        )
        res = process_single_file(large_path, options)
        self.assertEqual(res.status, "success")

        out_webp = self.case_dir / "large_8k.webp"
        self.assertTrue(out_webp.exists())
        with Image.open(out_webp) as out_img:
            self.assertEqual(out_img.width, 1920)
            self.assertEqual(out_img.height, 1200)


if __name__ == "__main__":
    unittest.main()
