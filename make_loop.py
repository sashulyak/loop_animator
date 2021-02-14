"""Make reversed loop video."""
import argparse
import cv2
import logging
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

    parser.add_argument(
        '--target_duration',
        dest='target_duration',
        type=float,
        required=False,
        default=8.0,
        help='Duration of target video in seconds.'
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


def get_video_frames_count(video_path: str) -> float:
    """
    Get video file frames count.

    :param video_path: path to the video
    :return: video frames count
    """
    video = cv2.VideoCapture(video_path)
    return int(video.get(cv2.CAP_PROP_FRAME_COUNT))


def main(args) -> None:
    """Main script."""
    input_video_frames_count = get_video_frames_count(args.input_file_path)
    input_video_fps = get_fps(args.input_file_path)
    input_video_duration = input_video_frames_count / input_video_fps

    looped_file_path = args.input_file_path.split('.')[0] + '_looped.mp4'
    looped_video_frames_count = input_video_frames_count * 2

    make_loop_cmd = [
        'ffmpeg',
        '-i',
        args.input_file_path,
        '-filter_complex',
        f'[0]reverse[r];[0][r]concat,loop=0:{looped_video_frames_count},setpts=N/{input_video_fps}/TB',
        looped_file_path
    ]
    run(make_loop_cmd)

    looped_video_duration = input_video_duration * 2
    speed_changing_coefficient = args.target_duration / looped_video_duration

    change_speed_cmd = [
        'ffmpeg',
        '-i',
        looped_file_path,
        '-vcodec',
        'h264',
        '-an',
        '-vf',
        f'fps={args.target_fps}, setpts={speed_changing_coefficient}*PTS',
        args.output_file_path
    ]
    run(change_speed_cmd)

    os.remove(looped_file_path)

    logging.info(f'All done! Video saved to {args.output_file_path}')


if __name__ == '__main__':
    args = parse_args()
    main(args)
