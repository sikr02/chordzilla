import re
import numpy as np
from PIL import ImageFont
from docx.text.paragraph import Paragraph

CHORDS = np.array([
    "C", "D", "E", "F", "G", "A", "B", "H", "("
])

FONT = ImageFont.truetype("Microsoft Aptos Fonts/Aptos.ttf", 11)
FONT_BOLD = ImageFont.truetype("Microsoft Aptos Fonts/Aptos-Bold.ttf", 11)

def is_chord(text: str):
    s = text.split()
    if len(s) == 0:
        return False
    for i in s:
        if i[0] not in CHORDS:
            return False
    return True


def x_positions(text: str, bold: bool = False):
    positions = []
    x = 0
    for char in text:
        if bold:
            width = FONT_BOLD.getlength(char)
        else:
            width = FONT.getlength(char)
        positions.append((char, x, x + width))
        x += width
    return positions

def align_chords(chords: str, text: str) -> str:
    chords_x = x_positions(chords, True)
    text_x = x_positions(text, False)
    current_start = None
    current_chord = ""
    cleaned_chords_x = []
    for chord_name, chord_start, _ in chords_x:
        if chord_name == " ":
            if current_chord:
                cleaned_chords_x.append((current_chord, current_start))
                current_chord = ""
                current_start = None
        else:
            current_chord += chord_name
            if not current_start:
                current_start = chord_start
    if current_chord:
        cleaned_chords_x.append((current_chord, current_start))

    # Wrap chords in [...]
    cleaned_chords_x = [(f"[{name}]", start) for name, start in cleaned_chords_x]
    cleaned_text_x = [(char, (start + end) / 2) for char, start, end in text_x]

    full_line = cleaned_chords_x + cleaned_text_x
    full_line = sorted(full_line, key=lambda x: x[1])
    return "".join([i[0] for i in full_line])


def merge_line(chords: str | None, text: str | None) -> str:
    if not text and not chords:
        return ""
    elif text and not chords:
        return text
    elif chords and not text:
        return re.sub(r'(\S+)', r'[\1]', chords)
    else:
        return align_chords(chords, text)

class SongDocx:
    def __init__(self, content: list[Paragraph]):
        self.title = content[0]

        sections = []
        current_section = []
        for c in content[1:]:
            matches = re.findall(r"\[(.*?)]", c.text)
            if matches:
                if current_section:
                    sections.append(current_section)
                current_section = [c]
            else:
                current_section.append(c)
        sections.append(current_section)
        self.sections = [Section(s) for s in sections]

    def __str__(self):
        return f"{{title: {self.title.text}}}\n\n" + "\n\n".join([str(s) for s in self.sections])


class Section:
    def __init__(self, content: list[Paragraph]):
        self.type = content[0] if "[" in content[0].text and "]" in content[0].text else None

        self.content = content[1:] if self.type else content

        lines = [c.text.replace("\n", " ").replace("\t", "     ") for c in self.content]
        lines_is_chord = [is_chord(l) for l in lines]

        combined_lines = []
        current_line = [None, None]
        for i in range(len(lines_is_chord)):
            # print(f"{lines_is_chord[i]}: {lines[i]}")
            if lines_is_chord[i]:
                # Line is a chord line
                if current_line[0]:
                    # Previous line is a chord line or is chord line with text => Append to lines
                    combined_lines.append(current_line)
                current_line = [lines[i], None]  # Initialize new line with chord line
            else:
                # Line is a text line
                if lines[i] == "":
                    continue
                if current_line[1]:
                    combined_lines.append(current_line)
                    current_line = [None, lines[i]]
                else:
                    current_line[1] = lines[i]
        combined_lines.append(current_line)

        combined_lines = [merge_line(c[0], c[1]) for c in combined_lines]
        combined_text = "\n".join(combined_lines).strip()

        chorus = ["Chorus", "Refrain", "Kehrvers"]
        verse = ["Vers", "Strophe"]
        if self.type:
            new_type = self.type.text.replace("[", "").replace("]", "")
            if any(c in self.type.text for c in chorus):
                combined_text = f"{{soc: {new_type}}}\n{combined_text}\n{{eoc}}"
            elif any(v in self.type.text for v in verse):
                combined_text = f"{{sov: {new_type}}}\n{combined_text}\n{{eov}}"
            else:
                combined_text = f"{{c: {new_type}}}\n{combined_text}"

        self.combined_text = combined_text

    def __str__(self):
        return self.combined_text

