import os
import tempfile
import zipfile

import pytest
from snapcheck.snap import Board, Snap, load_snap
from snapcheck.snap.elements import Element, ImageElement
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem


class TestSnap:
    def test_create_snap_minimal(self):
        snap = Snap()
        assert snap.title is None
        assert snap.description is None
        assert snap.metadata == {}
        assert snap.ratings == []
        assert snap.boards == []
        assert snap._dir is None
        assert snap._path is None

    def test_create_snap_with_values(self):
        rating = Rating(name="Quality")
        board = Board(title="Test Board")

        snap = Snap(
            title="Test Snap",
            description="A test snap",
            metadata={"author": "Test User"},
            ratings=[rating],
            boards=[board],
        )

        assert snap.title == "Test Snap"
        assert snap.description == "A test snap"
        assert snap.metadata == {"author": "Test User"}
        assert len(snap.ratings) == 1
        assert len(snap.boards) == 1

    def test_validate_undefined_rating_in_board(self):
        rating1 = Rating(id="rating1", name="Quality")
        rating2 = Rating(id="rating2", name="Accuracy")

        element = Element(intended_ratings=[rating2])
        board = Board(title="Board", elements=[element])

        # rating2 is used in a board added after the creation, without calling link_ratings()
        snap = Snap(ratings=[rating1])
        snap.boards.append(board)

        with pytest.raises(ValueError, match="is not defined in the ratings list"):
            snap._validate()

    def test_validate_valid_snap(self):
        rating = Rating(id="rating1", name="Quality")
        element = Element(intended_ratings=[rating])
        board = Board(title="Board", elements=[element])

        snap = Snap(ratings=[rating], boards=[board])
        snap._validate()  # Should not raise

    def test_validate_checks_scale(self):
        scale = RatingScale(
            description="Scale",
            ratings=[
                RatingScaleItem(name="Good", value=1),
                RatingScaleItem(name="Good", value=2),  # Duplicate name
            ],
        )
        rating = Rating(name="Quality", scale=scale)
        snap = Snap(ratings=[rating])

        with pytest.raises(ValueError, match="Duplicate rating name"):
            snap._validate()

    def test_intended_ratings_are_added(self):
        extra = Rating(id="extra", name="Extra")
        rating = Rating(id="rating1", name="Quality")
        board = Board(title="Board", elements=[Element(intended_ratings=[rating])])

        snap = Snap(ratings=[extra], boards=[board])

        assert snap.ratings == [extra, rating]

    def test_intended_ratings_are_linked(self):
        rating = Rating(id="rating1", name="Quality")
        # A copy with the same id is replaced by the rating of the snap
        element = Element(intended_ratings=[rating.model_copy()])
        board = Board(title="Board", elements=[element])

        snap = Snap(ratings=[rating], boards=[board])

        assert element.intended_ratings[0] is rating
        snap.update_rating("rating1", 2)
        assert element.intended_ratings[0].value == 2

    def test_intended_ratings_stay_linked_after_undo(self):
        rating = Rating(id="rating1", name="Quality")
        board = Board(title="Board", elements=[Element(intended_ratings=[rating]), Element(intended_ratings=[rating])])
        snap = Snap(boards=[board])

        snap.update_rating("rating1", 1)
        snap.update_rating("rating1", 2)
        snap.revert_changes()

        elements = snap.boards[0].elements
        assert elements[0].intended_ratings[0] is snap.ratings[0]
        assert elements[1].intended_ratings[0] is snap.ratings[0]
        assert snap.ratings[0].value == 1

    def test_update_unknown_rating_keeps_the_snap(self):
        rating = Rating(id="rating1", name="Quality")
        board = Board(title="Board", elements=[Element(intended_ratings=[rating])])
        snap = Snap(boards=[board])

        with pytest.raises(ValueError, match="Rating with ID 'unknown' not found"):
            snap.update_rating("unknown", 1)

        # The snap has not been restored: the references to its objects are still valid
        assert snap.boards[0] is board
        assert snap.ratings[0] is rating

    def test_link_ratings_without_id(self):
        board = Board(title="Board", elements=[Element(intended_ratings=[Rating()])])

        with pytest.raises(ValueError, match="has no id"):
            Snap(boards=[board])

    def test_link_ratings_same_id_different_definitions(self):
        axial = Rating(name="Quality", description="Axial view")
        coronal = Rating(name="Quality", description="Coronal view")
        element = Element(intended_ratings=[coronal])
        board = Board(title="Board", elements=[element])

        with pytest.warns(UserWarning, match="Several ratings have the id 'quality'"):
            snap = Snap(ratings=[axial], boards=[board])

        assert snap.ratings == [axial]
        assert element.intended_ratings[0] is axial

    def test_link_ratings_removes_duplicates(self):
        rating = Rating(id="rating1", name="Quality")

        snap = Snap(ratings=[rating, rating.model_copy()])

        assert snap.ratings == [rating]
        assert len(snap.ratings) == 1

    def test_link_ratings_after_replacing_a_rating(self):
        rating = Rating(id="rating1", name="Quality")
        element = Element(intended_ratings=[rating])
        snap = Snap(boards=[Board(title="Board", elements=[element])])

        snap.ratings[0] = Rating(id="rating1", name="Quality", value=1)
        snap.link_ratings()

        assert element.intended_ratings[0] is snap.ratings[0]

    def test_to_dict_without_compress(self):
        rating = Rating(name="Quality")
        board = Board(title="Board")
        snap = Snap(title="Test", ratings=[rating], boards=[board])

        data = snap.to_dict(compress=False)

        assert data["title"] == "Test"
        assert len(data["ratings"]) == 1
        assert len(data["boards"]) == 1
        assert "_scales" not in data

    def test_to_dict_with_compress(self):
        scale = RatingScale(description="Quality scale", ratings=[RatingScaleItem(name="Good", value=1)])
        rating1 = Rating(name="Quality1", scale=scale)
        rating2 = Rating(name="Quality2", scale=scale)

        snap = Snap(ratings=[rating1, rating2])
        data = snap.to_dict(compress=True)

        # Shared objects are extracted into "_refs" and referenced by "$@<cls>#<idx>".
        assert "_refs" in data
        scale_refs = data["_refs"]["snapcheck.snap.rating.RatingScale"]
        assert len(scale_refs) == 1  # the scale is shared, so stored only once
        rating_refs = data["_refs"]["snapcheck.snap.rating.Rating"]
        assert rating_refs[0]["scale"].startswith("$@")
        assert rating_refs[1]["scale"].startswith("$@")
        # both ratings point to the same (shared) scale
        assert rating_refs[0]["scale"] == rating_refs[1]["scale"]

    def test_update_rating(self):
        rating = Rating(id="rating1", name="Quality", value=None)
        snap = Snap(ratings=[rating])
        snap.update_rating("rating1", 5)
        assert snap.ratings[0].value == 5

    def test_close(self):
        snap = Snap()
        tmp_dir = tempfile.TemporaryDirectory()
        snap._dir = tmp_dir

        dir_path = tmp_dir.name
        assert os.path.exists(dir_path)

        snap.close()

        # Directory should be cleaned up
        assert not os.path.exists(dir_path)


class TestSnapSaveLoad:
    def test_save_and_load_minimal_snap(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.snap")

            # Create and save
            snap = Snap(title="Test Snap", description="Test description", metadata={"version": "1.0"})
            snap.save(save_path)

            assert os.path.exists(save_path)

            # Load
            loaded_snap = load_snap(save_path)

            assert loaded_snap.title == "Test Snap"
            assert loaded_snap.description == "Test description"
            assert loaded_snap.metadata == {"version": "1.0"}
            assert loaded_snap._filepath == save_path

            loaded_snap.close()

    def test_load_links_intended_ratings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.snap")
            rating = Rating(id="rating1", name="Quality")
            board = Board(
                title="Board", elements=[Element(intended_ratings=[rating]), Element(intended_ratings=[rating])]
            )
            Snap(boards=[board]).save(save_path)

            loaded_snap = load_snap(save_path)

            elements = loaded_snap.boards[0].elements
            assert elements[0].intended_ratings[0] is loaded_snap.ratings[0]
            assert elements[1].intended_ratings[0] is loaded_snap.ratings[0]
            loaded_snap.close()

    # def test_save_and_load_with_boards_and_ratings(self):
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         save_path = os.path.join(tmpdir, "test.snap")

    #         rating = Rating(id="quality", name="Quality")
    #         board = Board(
    #             title="Test Board",
    #             description="Board description"
    #         )

    #         snap = Snap(
    #             title="Complex Snap",
    #             ratings=[rating],
    #             boards=[board]
    #         )
    #         snap.save(save_path)

    #         loaded_snap = load_snap(save_path)

    #         assert loaded_snap.title == "Complex Snap"
    #         assert len(loaded_snap.ratings) == 1
    #         assert loaded_snap.ratings[0].name == "Quality"
    #         assert len(loaded_snap.boards) == 1
    #         assert loaded_snap.boards[0].title == "Test Board"

    #         loaded_snap.close()

    def test_save_with_file_elements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test image file
            img_path = os.path.join(tmpdir, "test_image.png")
            with open(img_path, "wb") as f:
                f.write(b"fake image content")

            save_path = os.path.join(tmpdir, "test.snap")

            element = ImageElement(src=img_path, is_local=False)
            board = Board(title="Board with image", elements=[element])
            snap = Snap(boards=[board])

            snap.save(save_path)

            # Verify archive contains content directory
            with zipfile.ZipFile(save_path, "r") as zf:
                files = zf.namelist()
                assert any("content/" in f for f in files)

            # Load and verify
            loaded_snap = load_snap(save_path)
            assert len(loaded_snap.boards) == 1
            assert len(loaded_snap.boards[0].elements) == 1

            loaded_snap.close()

    def test_save_without_path_raises_error(self):
        snap = Snap(title="Test")

        with pytest.raises(ValueError, match="No path provided"):
            snap.save()

    def test_save_reuses_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.snap")

            snap = Snap(title="Test")
            snap.save(save_path)

            # Modify and save again without path
            snap.title = "Modified"
            snap.save()

            # Should save to same path
            loaded = load_snap(save_path)
            assert loaded.title == "Modified"
            loaded.close()

    def test_load_invalid_archive_no_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create zip without JSON
            zip_path = os.path.join(tmpdir, "invalid.snap")
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("random.txt", "not a json file")

            with pytest.raises(FileNotFoundError, match="No JSON file found"):
                load_snap(zip_path)

    # def test_load_validates_snap(self):
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         save_path = os.path.join(tmpdir, "test.snap")

    #         # Create snap with invalid reference
    #         rating1 = Rating(id="rating1", name="Quality")
    #         rating2 = Rating(id="rating2", name="Accuracy")
    #         element = Element(intended_ratings=[rating2])
    #         board = Board(title="Board", elements=[element])

    #         # Manually save without validation
    #         snap = Snap(ratings=[rating1], boards=[board])
    #         snap.save(save_path)

    #         # Loading should fail validation
    #         with pytest.raises(ValueError, match="is not defined in the ratings list"):
    #             load_snap(save_path)
