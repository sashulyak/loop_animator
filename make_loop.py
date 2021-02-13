"""Make reversed loop video."""
import argparse
import cv2
import os
from subprocess import run


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    :param args: command line arguments
    :return: argparse results
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input_file_path',
        dest='input_file_path',
        type=str,
        required=True,
        help='Path to the input video.'
    )
    parser.add_argument(
        '-o',
        '--output_file_path',
        dest='output_file_path',
        type=str,
        required=True,
        help='Path to the output video.'
    )

    parser.add_argument(
        '--target_fps',
        dest='target_fps',
        type=float,
        required=False,
        default=25.0,
        help='Frames per second for target file.'
    )

    return parser.parse_args()


def get_fps(video_path: str) -> float:
    """
    Get video's frames persecond.

    :param video_path: path to the video
    :return: FPS
    """
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    return fps


def get_video_duration(video_path: str) -> float:
    """
    Get video file duration in seconds.

    :param video_path: path to the video
    :return: duratin of the video in seconds
    """
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    return video.get(cv2.CAP_PROP_POS_MSEC) / 1000


def main(args) -> None:
    """Main script."""
    input_video_duration = get_video_duration(input_file_path)
    input_video_fps = get_fps(input_file_path)

    looped_file_path = input_file_path.split('.')[0] + '_looped.mp4'
    looped_video_frames_count = int(input_video_fps * input_video_duration * 2)
    make_loop_cmd = [
        'ffmpeg',
        '-i',
        input_file_path,
        '-filter_complex',
        f'"[0]reverse[r];[0][r]concat,loop=0:{looped_video_frames_count},setpts=N/{input_video_fps}/TB"',
        looped_file_path
    ]

    completed_process = run(make_loop_cmd, shell=True, capture_output=True, text=True)
    if completed_process.returncode != 0:
        print('Someting went wrong. Exiting...')
        return

    looped_video_duration = input_video_duration * 2
    target_duration = get_video_duration(output_file_path)
    speed_changing_coefficient = target_duration / looped_video_duration

    change_speed_cmd = [
        'ffmpeg',
        '-i',
        looped_file_path,
        '-vcodec',
        'h264',
        '-an',
        '-vf',
        f'"fps={args.target_fps}, setpts={speed_changing_coefficient}*PTS"',
        output_file_path
    ]

    completed_process = run(change_speed_cmd, shell=True, capture_output=True, text=True)
    if completed_process.returncode != 0:
        print('Someting went wrong. Exiting...')
        return

    os.remove(looped_file_path)


if __name__ == '__main__':
    args = parse_args()
    main(args)
