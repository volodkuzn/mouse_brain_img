import argparse
import pathlib
import shutil
import ffmpeg


def convert_to_video(input_dir: pathlib.Path, output_dir: pathlib.Path, output_filename: str) -> str:
    out, err = (
        ffmpeg.input(str(input_dir / r"%4d.bmp"), framerate=24, start_number=0)
        .output(
            str(output_dir / output_filename),
            vcodec="libx265",
            pix_fmt="gray",
            preset="fast",
            crf=10,
        )
        .run(quiet=True)
    )
    return err


def group_and_convert(input_dir: pathlib.Path, output_dir: pathlib.Path) -> None:
    img_filenames = list(input_dir.glob("*.bmp"))
    assert len(img_filenames) % 2 == 0
    filenames_by_number = {int(fn.name.split("_")[1]): fn for fn in img_filenames}
    wavelength_list = ["505", "656"]
    for wl in wavelength_list:
        (input_dir / wl).mkdir(exist_ok=True)
    for number, filename in filenames_by_number.items():
        (input_dir / ("505" if number % 2 == 0 else "656") / "{:04d}.bmp".format(number // 2)).hardlink_to(filename)
    # ffmpeg -r 12 -start_number 0 -i ./%4d.bmp -pix_fmt gray -vcodec libx265 -level 3.0 -preset fast -crf 9 video.MOV
    for wl in wavelength_list:
        convert_to_video(input_dir / wl, output_dir=output_dir, output_filename=(input_dir.name + "_{}.MOV".format(wl)))
        shutil.rmtree(input_dir / wl)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda args: parser.print_help())
    parser.add_argument("--input-dir", type=str)
    parser.add_argument("--output-dir", type=str)
    return parser.parse_args()


def main():
    args = parse_args()
    input_dir = pathlib.Path(args.input_dir)
    output_dir = pathlib.Path(args.output_dir) if args.output_dir is not None else input_dir
    group_and_convert(input_dir=input_dir, output_dir=output_dir)


if __name__ == "__main__":
    main()
