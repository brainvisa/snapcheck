"""The snap object and the snap files (``.snpk``).

A ``.snpk`` file is a zip archive containing:

- ``<name>.json``: the snap serialized in JSON, with its ratings, boards and elements;
- ``content/``: a copy of the files displayed by the elements (images...), each file being
  copied only once.

Use :meth:`Snap.save` and :func:`load_snap` to write and read them.
"""

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
    """Convert an HTML string to a PDF file (with xhtml2pdf)."""
    with open(output_path, "w+b") as pdf_file:
        pisa.CreatePDF(html_string, dest=pdf_file)


def prettify_html(html_string: str) -> str:
    """Indent an HTML string to make it readable."""
    soup = bs(html_string, "html.parser")
    return soup.prettify()


@dataclass
class Snap(LObject):
    """A quality control document: boards to review and the ratings to fill in.

    Parameters
    ----------
    title : str or None
        Title of the snap.
    description : str or None
        Description of the snap (ex: the subject and the processing it controls).
    metadata : dict
        Free metadata (ex: study, subject, visit...).
    ratings : list of Rating
        All the ratings of the snap. The ratings intended by the elements of the boards must be in
        this list.
    boards : list of Board
        The boards to review, in this order.
    global_comment : str
        General comment of the reviewer.

    Examples
    --------
    Create a snap with one board, save it and read it again:

    >>> from snapcheck.snap import Board, ImageElement, Snap, load_snap
    >>> from snapcheck.snap.rating import Rating
    >>> rating = Rating(name="Image quality")
    >>> board = Board(title="Images", elements=[ImageElement(src="image.png", intended_ratings=[rating])])
    >>> snap = Snap(title="My QC", ratings=[rating], boards=[board])
    >>> snap.save("my_qc.snpk")  # doctest: +SKIP
    >>> snap = load_snap("my_qc.snpk")  # doctest: +SKIP

    See the examples gallery for complete examples.
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
        """Return a flat list of the elements of all the boards, including the elements in rows."""
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
        """Remove the temporary directory where the loaded snap archive has been extracted."""
        if self._dir:
            self._dir.cleanup()

    def update_rating(self, ratingId: str, value: int | None):
        """Set the value of a rating.

        Parameters
        ----------
        ratingId : str
            Id of the rating.
        value : int or None
            The new value, a value of the rating scale.

        Raises
        ------
        ValueError
            If there is no rating with this id.
        """
        with self.changing():
            for i, n in enumerate(self.ratings):
                if n.id == ratingId:
                    self.ratings[i].value = value
                    break
            else:
                raise ValueError(f"Note with ID '{ratingId}' not found.")

    def to_json(self, path: str):
        """Serialize the snap in JSON, without the content files.

        Use :meth:`save` to write a complete snap file.
        """
        warn(
            "Using to_json() method on Snap object will only save metadata.\n"
            + "To also save the boards content, use the save() method"
        )
        return super().to_json()

    def save(self, path: str | None = None):
        """Save the snap in a ``.snpk`` file.

        The files of the elements are copied in the archive and their paths become relative to it.

        Parameters
        ----------
        path : str or None
            Path of the ``.snpk`` file. By default, the file the snap has been loaded from or last
            saved to.

        Raises
        ------
        ValueError
            If no path is given and the snap has never been saved.
        """
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
        """Export the snap as a static website: a page per board and an index page.

        The snap must have been loaded from a file (see :func:`load_snap`): the files of the
        elements are copied from the extracted archive.

        Parameters
        ----------
        save_path : str
            Directory of the website, created if needed. The index page is ``00_INDEX.html``.
        compress : bool
            If True, also compress the directory in ``<save_path>.zip``.

        Returns
        -------
        str
            The path of the zip file if ``compress`` is True, else the directory.
        """
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
        """Export the snap to a PDF file: the home page, then a page per board.

        The snap must have been loaded from a file (see :meth:`export_to_html`).

        Parameters
        ----------
        path : str
            Path of the PDF file.
        """
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
    """Create a snap displaying a single file, to open an image directly in the GUI.

    Parameters
    ----------
    path : str
        Path of an image (JPEG, PNG, GIF, BMP, TIFF, SVG or WebP).

    Returns
    -------
    Snap
        An untitled snap with a single board displaying the image.

    Raises
    ------
    OSError
        If the file is not a supported image.
    """
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
    """Load a snap from a ``.snpk`` file.

    The archive is extracted in a temporary directory, kept as long as the snap is open and
    removed by :meth:`Snap.close`. If the file is not a snap archive but an image, a snap
    displaying this image is created (see :func:`new_infered_snap`).

    Parameters
    ----------
    path : str
        Path of the ``.snpk`` file (or of an image).

    Returns
    -------
    Snap
        The loaded snap.

    Raises
    ------
    FileNotFoundError
        If the archive does not contain a JSON file.
    ValueError
        If the snap is invalid (ex: a board uses a rating which is not in
        :attr:`Snap.ratings <snapcheck.snap.snap.Snap>`).
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
    """Save a snap in a ``.snpk`` file, see :meth:`Snap.save`."""
    snap.save(path)


def new_snap(path: str) -> Snap:
    """Create an empty snap, which will be saved in ``path``."""
    snap = Snap()
    snap._filepath = path
    return snap
