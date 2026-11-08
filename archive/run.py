from docx import Document
from pathlib import Path

from song import SongDocx


SOURCE_PATH = Path(r"C:\Users\Simon\Desktop\EJ\Martinushaus\25\Martinushaus_Noten_25.docx")
DESTINATION_PATH = Path(__file__).parent / "chordpro_docs"

def main():
    doc = Document(str(SOURCE_PATH))

    songs_docx = []

    current_paragraph = []
    for i, paragraph in enumerate(doc.paragraphs):
        if paragraph.text and paragraph.style.name == "Heading 1":
            if current_paragraph:
                songs_docx.append(current_paragraph)
                current_paragraph = [paragraph]
        else:
            current_paragraph.append(paragraph)
    songs_docx.append(current_paragraph)

    # Remove everything before the first Heading
    songs_docx = songs_docx[1:]

    # songs_docx = [i for i in songs_docx if i[0].text.startswith("Stille")] # TODO: remove

    songs = [SongDocx(i) for i in songs_docx]

    for s in songs:
        dst = DESTINATION_PATH / f"{s.title.text}.chord"
        with open(dst, "w", encoding="utf-8") as f:
            f.write(str(s))


if __name__ == '__main__':
    main()
