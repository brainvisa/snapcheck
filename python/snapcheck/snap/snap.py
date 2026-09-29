import json
import os.path as op
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from os import listdir, makedirs, mkdir, rename
from pathlib import Path
from typing import Any
from warnings import warn

from bs4 import BeautifulSoup as bs
from lepton_common import LObject
from pypdf import PdfWriter
from snapcheck.snap.board import AbstractElement, Board
from snapcheck.snap.elements import FileElement, ImageElement
from snapcheck.snap.rating import Rating
from xhtml2pdf import pisa


def html_to_pdf(html_string, output_path):
    with open(output_path, "w+b") as pdf_file:
        pisa.CreatePDF(html_string, dest=pdf_file)


def prettify_html(html_string: str) -> str:
    """Prettify the HTML string for better readability."""
    soup = bs(html_string, "html.parser")
    return soup.prettify()


@dataclass
class Snap(LObject):
    """
    A Snap represents a collection of boards, ratings, and associated metadata.
    """

    title: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    ratings: list[Rating] = field(default_factory=list)
    boards: list[Board] = field(default_factory=list)
    global_comment: str = ""

    _dir: tempfile.TemporaryDirectory | None = None
    _path: str | None = None

    def get_all_elements(self) -> list[AbstractElement]:
        """Return a flat list of all elements in all boards, including those in rows."""
        all_elements = []
        for board in self.boards:
            all_elements.extend(board.get_all_elements())
        return all_elements

    def _validate(self):
        """
        Check if the Snap object is valid.
        This can include checks like ensuring that all ratings and boards are properly defined.
        """
        # Check that all ratings referenced in boards are defined in the ratings list
        for board in self.boards:
            for int_rating in board.all_intended_ratings:
                for rating in self.ratings:
                    if int_rating.id == rating.id:
                        break
                else:
                    raise ValueError(
                        f"Rating with #'{rating.id}' used by board '{board.title}' is not defined in the ratings list."
                    )
        checked_scales = []
        for rating in self.ratings:
            if rating.scale is None or rating.scale in checked_scales:
                continue
            rating.scale.check()

    def close(self):
        """Remove temporary directory if set."""
        if self._dir:
            self._dir.cleanup()

    def update_rating(self, ratingId: str, value: any):
        with self.changing():
            for i, n in enumerate(self.ratings):
                if n.id == ratingId:
                    self.ratings[i].value = value
                    break
            else:
                raise ValueError(f"Note with ID '{ratingId}' not found.")

    def to_json(self, path: str):
        warn(
            "Using to_json() method on Snap object will only save metadata.\n"
            + "To also save the boards content, use the save() method"
        )
        return super().to_json()

    def save(self, path: str | None = None):
        # By default keep the same path
        if path is None:
            if self._filepath is None:
                raise ValueError("No path provided to save the Snap object.")
            path = self._filepath

        # Create the content directory
        fname = op.basename(path).split(".")[-2]
        tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_snap_")
        content_path = op.join(tmp_dir.name, "content")
        mkdir(content_path)
        js_f = op.join(tmp_dir.name, fname + ".json")

        # List all elements
        files_elements: list[FileElement] = list(filter(lambda e: isinstance(e, FileElement), self.get_all_elements()))
        source_tracker = {}
        # Copy each source file and change its path in each elements
        for el in files_elements:
            if el.is_local:
                # If the file is already local, behave as it isn't to
                # copy the files to the new destination
                # It's a bit ugly but it works...
                el.is_local = False
                el.src = op.join(self._dir.name, el.src)
            el.export_to_local(tmp_dir.name, "content", source_tracker)

        # Save the JSON file
        super().to_json(js_f)

        # Compress all together
        # TODO: make directly the archive with the proper name
        # Create the archive directly with the desired file name and extension
        base_name, _ = op.splitext(path)
        archive_path = shutil.make_archive(base_name=base_name, format="zip", root_dir=tmp_dir.name)
        # If the extension is not .snap, rename the archive
        rename(archive_path, path)
        self._filepath = path

        self._has_changed = False

    def _generate_board_html_header(self, board_index: int) -> str:
        header = f"""<div class='snap-header'>
            <div class='snap-title'>
                <a href='00_INDEX.html'>{self.title}</a>
            </div>
            <nav class='snap-nav'>
                <ul>"""
        for b, board in enumerate(self.boards):
            header += f"<li><a href='board_{b}.html'"
            if b == board_index:
                header += " class='active'"
            header += f">{board.title}</a></li>"
        header += "</ul></nav></div>"
        return header

    def export_to_html(self, save_path: str | None = None, compress: bool = False):
        # Create the ouput directory
        makedirs(save_path, exist_ok=True)

        # Generate boards HTML scripts
        boards = [board.to_html() for board in self.boards]
        board_links = [op.join(save_path, f"board_{b}.html") for b in range(len(self.boards))]

        # Save each board
        for b, board in enumerate(self.boards):
            board_html = f"""<html>
            <head>
                <title>{self.title} - {self.boards[b].title}</title>
                <link rel="stylesheet" href="index/style.css">
            </head><body>"""
            board_html += self._generate_board_html_header(b)
            board_html += boards[b]
            board_html += "</body></html>"
            with open(board_links[b], "w") as f:
                f.write(prettify_html(board_html))

        # Save home page
        home_html = f"""<html>
        <head>
            <title>{self.title}</title>
            <link rel="stylesheet" href="index/style.css">
        </head><body>"""
        home_html += self._generate_board_html_header(-1)
        home_html += "<h2>Boards</h2><ul>"
        for b, board in enumerate(self.boards):
            home_html += f"<li><a href='board_{b}.html'>{board.title}</a></li>"
        home_html += "</ul>"
        home_html += "</body></html>"
        home_path = op.join(save_path, "00_INDEX.html")
        with open(home_path, "w") as f:
            f.write(prettify_html(home_html))

        # Copy css
        css_src = Path(__file__).parent / "export_style.css"
        index_dir = Path(save_path) / "index"
        index_dir.mkdir(exist_ok=True)
        shutil.copy(css_src, index_dir / "style.css")

        # Copy the content
        shutil.copytree(
            Path(self._dir.name) / "content",
            Path(save_path) / "content",
            dirs_exist_ok=True,
        )

        if compress:
            # Compress the directory into a zip file
            zip_path = str(save_path) + ".zip"
            shutil.make_archive(base_name=save_path, format="zip", root_dir=save_path)
            return zip_path
        return save_path

    def export_to_pdf(self, path: str):
        """Export the Snap object to a PDF file."""
        # Export as HTML in a temporary directory
        tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_snap_pdf_")
        html_dir = op.join(tmp_dir.name, "html")
        self.export_to_html(html_dir)

        # Convert each board HTML to PDF
        pdf_dir = op.join(tmp_dir.name, "pdf")
        makedirs(pdf_dir, exist_ok=True)
        files = []
        for f in sorted(listdir(html_dir)):
            if not f.endswith(".html"):
                # Skip non-HTML entries (e.g. the "index" assets directory).
                continue
            html_path = op.join(html_dir, f)
            with open(html_path, "r") as fp:
                html_string = fp.read()
            pdf_f = op.join(pdf_dir, f.replace(".html", ".pdf"))
            html_to_pdf(html_string, pdf_f)
            files.append(pdf_f)

        # Merge all board PDFs into a single PDF file
        merger = PdfWriter()
        for pdf_path in files:
            merger.append(pdf_path)
        merger.write(path)
        merger.close()


def new_infered_snap(path: str) -> Snap:
    """Create a new Snap object with default values."""
    # Check if the path is an image file (jpg, png, gif, bmp, tiff)
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"]
    if any(path.lower().endswith(ext) for ext in image_extensions):
        el = ImageElement(src=path)
    else:
        raise OSError(f"File format not supported for Snap creation: {path}")

    board = Board(
        title="Board 1",
        description="",
        elements=[el],
    )

    snap = Snap(title="Untitled Snap", description="", boards=[board])

    return snap


def load_snap(path: str) -> Snap:
    """Load a Snap object from a .snpk archive.

    A .snpk is a zip containing a JSON file plus its content assets. The extracted
    content is kept in a TemporaryDirectory referenced by ``snap._dir`` so it lives
    exactly as long as the Snap is open (and is cleaned up by ``Snap.close()``).

    If ``path`` is not a snap archive at all (e.g. a raw image opened directly),
    fall back to inferring a snap from that file. Genuine corruption of a snap
    archive (bad JSON, invalid structure) is raised, not silently swallowed.
    """
    tmp_dir = tempfile.TemporaryDirectory(prefix="snapcheck_snap_load_")
    try:
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(tmp_dir.name)
    except zipfile.BadZipFile:
        # Not a snap archive: treat the file as raw content to infer a snap from.
        tmp_dir.cleanup()
        return new_infered_snap(path)

    # Find the JSON file at the root of the archive
    json_files = [f for f in listdir(tmp_dir.name) if f.endswith(".json")]
    if not json_files:
        tmp_dir.cleanup()
        raise FileNotFoundError(f"{path} is an invalid Snap. No JSON file found at the root of the archive.")

    with open(op.join(tmp_dir.name, json_files[0]), "r") as f:
        data = json.load(f)

    snap = Snap.from_dict(data)
    snap._filepath = path
    snap._dir = tmp_dir

    # Validate the loaded object
    snap._validate()

    return snap


def save_snap(snap: Snap, path: str):
    """Save a Snap object to a JSON file"""
    snap.save(path)


def new_snap(path: str) -> Snap:
    """Create a new Snap object with default values."""
    snap = Snap()
    snap._filepath = path
    return snap
