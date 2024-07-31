import argparse
from fractions import Fraction
from typing import Union

import matplotlib.pyplot as plt
import music21
from music21 import note, chord, stream

GRAPH_COLORS = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'cyan', 'magenta',
                'lime', 'pink', 'teal', 'lavender']
PITCH_CLASSES = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']

FloatOrFraction = Union[float, Fraction]


def save_piano_roll_fig(piano_roll: list[tuple[int, FloatOrFraction, FloatOrFraction]], path: str = './piano_rolls/',
                        output_path: str = ".", show_legend: bool = False):
    """
    Save a piano roll figure.
    :param piano_roll: A list of tuple containing the pitch, start time and end time of the notes.
    :param path: The path to the input file.
    :param output_path: The path to the folder where the file should be saved.
    :param show_legend: Whether to show the legend or not.
    :return: None
    """
    min_pitch = min([n[0] for n in piano_roll])
    max_pitch = max([n[0] for n in piano_roll])
    min_y = min_pitch - (min_pitch % 12)
    max_y = max_pitch + 13 - (max_pitch % 12)
    plt.clf()
    fig = plt.Figure(layout='constrained', figsize=(14, 5))
    ax = fig.subplots()
    legend = {}

    piano_roll.sort(key=lambda n: n[2], reverse=False)

    for pitch, start, end in piano_roll:
        pc = pitch % 12
        ax.plot([start, end], [pitch, pitch],
                color=GRAPH_COLORS[pc])
        legend[PITCH_CLASSES[pc]] = GRAPH_COLORS[pc]

    if len(piano_roll) > 0:
        ax.set_xlim(0, piano_roll[-1][2] + 0.1)
    else:
        ax.set_xlim(0, 1)
    ax.set_ylim(min_y, max_y)  # Could be setup to only the used octaves
    ax.set_title(f'Piano roll for {path}')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Pitch')
    ax.grid(True)
    ax.set_yticks([i for i in range(min_y, max_y, 12)])
    ax.set_yticklabels([f'C{i // 12 - 1}-({i})' for i in range(min_y, max_y, 12)])

    # Legend
    if show_legend:
        legend = dict(sorted(legend.items(), key=lambda item: PITCH_CLASSES.index(item[0])))
        colors_to_print = list(legend.values())
        pitch_classes_to_print = list(legend.keys())
        handles = [plt.Line2D([0], [0], color=colors_to_print[i], label=pitch_classes_to_print[i]) for i in
                   range(len(colors_to_print))]
        fig.legend(handles=handles, loc='outside right')
    try:
        fig.savefig(f'{output_path}/piano_rolls/{path}.png')
    except FileNotFoundError:
        # If the directory does not exist, the figure is not saved (but the program should not crash).
        print('The directory does not exist for saving the piano roll figure.')
    plt.close(fig)


def music21_stream_to_piano_roll(music_stream: stream.Stream) -> list[tuple[int, float, float]]:
    """
    Convert a music21 stream to a piano roll representation.

    :param music_stream: The music21 stream.
    :return: A list of tuples containing the pitch, start time, and end time of the notes.
    """
    notes = []

    flat_stream = music_stream.flatten()

    for element in flat_stream.notes:
        if isinstance(element, note.Note):
            absolute_start = element.getOffsetBySite(flat_stream)
            absolute_end = absolute_start + element.quarterLength
            notes.append((element.pitch.midi, absolute_start, absolute_end))
        elif isinstance(element, chord.Chord):
            absolute_start = element.getOffsetBySite(flat_stream)
            absolute_end = absolute_start + element.quarterLength
            for pitch in element.pitches:
                notes.append((pitch.midi, absolute_start, absolute_end))

    return notes


if __name__ == "__main__":
    # Parse one argument, the path to the music sheet with argparse
    parser = argparse.ArgumentParser(description="Convert a music sheet to a piano roll")
    parser.add_argument("music_sheet_path", type=str, help="The path to the music sheet(.xml, .mid, .mxl)")
    args = parser.parse_args()
    music_sheet_path = args.music_sheet_path

    # Load the music sheet
    music_sheet = music21.converter.parse(music_sheet_path)

    # Convert the music sheet to a piano roll
    piano_roll_tuples = music21_stream_to_piano_roll(music_sheet)

    # Save the piano roll figure
    save_piano_roll_fig(piano_roll_tuples, music_sheet_path)
