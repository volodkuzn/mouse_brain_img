from typing import NamedTuple, Union
import typing
import ffmpeg
import pathlib
import attr
import numpy as np
import numpy.typing as npt


class ImageSequence(NamedTuple):
    w_505: npt.NDArray[np.float16]
    w_656: npt.NDArray[np.float16]


class Point(NamedTuple):
    x: float
    y: float


@attr.s(auto_attribs=True)
class BrainImages(object):
    imgs: ImageSequence
    flatfield: Union[ImageSequence, float]

    dot_coords = None

    @staticmethod
    def from_video(
        video_paths: list[Union[str, pathlib.Path]],
        *,
        flatfield: typing.Optional[Union[ImageSequence, float]] = None,
        dot_coords: typing.Optional[Point] = None,
    ) -> "BrainImages":
        """Provide path video for 505, then for 656 nm diode"""
        video_paths_ = [pathlib.Path(video_path) for video_path in video_paths if type(video_path) is not pathlib.Path]
        if "505" not in video_paths_[0].name:
            video_paths_ = video_paths_[::-1]
        assert ("505" in video_paths_[0].name) and ("656" in video_paths_[1].name)
        probe = ffmpeg.probe(video_paths[0])
        width, height = probe["streams"][0]["width"], probe["streams"][0]["height"]
        imgs = list()
        for video_path in video_paths:
            out_505, err = ffmpeg.input(video_path).output("pipe:", format="rawvideo", pix_fmt="gray").run(capture_stdout=True)
            imgs.append(np.frombuffer(out_505, np.uint8).reshape([-1, height, width]).astype(np.float16))
        if flatfield is None:
            flatfield = 1.0
        return BrainImages(ImageSequence(*imgs), flatfield)
