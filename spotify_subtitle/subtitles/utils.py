import datetime


def generate_srt_from_text(text_input: str, line_duration_seconds: int = 4) -> str:
    lines = [line.strip() for line in text_input.strip().split('\n') if line.strip()]
    srt_blocks = []
    start_time = datetime.timedelta(seconds=0)

    for i, line in enumerate(lines):
        segment_number = i + 1
        end_time = start_time + datetime.timedelta(seconds=line_duration_seconds)

        start_srt = (datetime.datetime.min + start_time).strftime('%H:%M:%S,%f')[:-3]
        end_srt = (datetime.datetime.min + end_time).strftime('%H:%M:%S,%f')[:-3]

        block = f"{segment_number}\n{start_srt} --> {end_srt}\n{line}\n"
        srt_blocks.append(block)

        start_time = end_time

    return "\n".join(srt_blocks)
