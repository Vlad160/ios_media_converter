import argparse
import os.path
import pathlib
import subprocess

ios_photo_ext = "HEIC"
ios_video_ext = "HEVC"
BATCH_SIZE = 100


def create_filter(ext):
    def filter_lambda(filename):
        file_path = pathlib.Path(filename)
        return file_path.is_file() and file_path.suffix.endswith(ext)

    return filter_lambda


def create_existing_files_filter(dest_dir, source_ext, target_ext):
    def filter_lambda(filename):
        file_path = pathlib.Path(filename)
        if file_path.suffix.endswith(source_ext):
            possible_dest_file = os.path.join(
                dest_dir, "{}.{}".format(file_path.stem, target_ext)
            )
            return not os.path.exists(possible_dest_file)

    return filter_lambda


def convert_photos(dest_dir, photos):
    cmd = [
        "magick",
        "mogrify",
        "-format",
        "jpg",
        "-path",
        dest_dir,
        *photos,
    ]
    fconvert = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = fconvert.communicate()
    assert fconvert.returncode == 0, stderr


def main():
    parser = argparse.ArgumentParser(
        description="Пример приложения с именованными аргументами"
    )

    parser.add_argument("--source", type=str, help="Source folder", required=True)
    parser.add_argument("--dest", type=str, help="Destination folder", required=True)
    parser.add_argument(
        "--exclude-photo", type=bool, help="Skip photo conversion", default=False
    )
    parser.add_argument(
        "--exclude-video", type=bool, help="Skip video conversion", default=False
    )
    parser.add_argument(
        "--ignore-dest-files",
        help="Removes file from conversion if it exists in destination folder",
        default=True,
    )
    args = parser.parse_args()

    config = {
        "source_folder": args.source,
        "dest_folder": args.dest,
        "exclude_photo": args.exclude_photo,
        "exclude_video": args.exclude_video,
        "ignore_converted_files": args.ignore_dest_files,
    }

    if not os.path.exists(config["source_folder"]) or not os.path.exists(
        config["dest_folder"]
    ):
        raise Exception(
            "Source or destination path does not exist. Please check that you are passing the right path"
        )

    sources = os.listdir(config["source_folder"])
    sources = list(map(lambda x: os.path.join(config["source_folder"], x), sources))

    photos = list(filter(create_filter(ios_photo_ext), sources))
    videos = list(filter(create_filter(ios_video_ext), sources))

    print(
        """Photos found: {}
Videos found: {}""".format(
            len(photos), len(videos)
        )
    )

    if config["ignore_converted_files"]:
        print("Filtering filters that exist in output folder...")
        photos = list(
            filter(
                create_existing_files_filter(
                    config["dest_folder"], ios_photo_ext, "jpg"
                ),
                photos,
            )
        )

        videos = list(
            filter(
                create_existing_files_filter(
                    config["dest_folder"], ios_video_ext, "mp4"
                ),
                videos,
            )
        )
        print(
            """Photos found: {}
Videos found: {}""".format(
                len(photos), len(videos)
            )
        )
    if len(photos) > 0:
        for i in range(0, len(photos), BATCH_SIZE):
            slice = photos[i : i + BATCH_SIZE]
            convert_photos(config["dest_folder"], slice)


if __name__ == "__main__":
    main()
