"""End-to-end API tests for the SnapServe backend (security + object lifecycle)."""

import os.path as op
import tempfile

import pytest
from fastapi.testclient import TestClient
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem
from snapcheck.snap.snap import Board, Snap, load_snap
from snapserve.app import app as lepton_app


@pytest.fixture()
def client():
    return TestClient(lepton_app.app)


@pytest.fixture()
def auth(client):
    token = client.post("/session/").json()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def snap_path():
    scale = RatingScale(ratings=[RatingScaleItem(name="Good", value=1)])
    snap = Snap(
        title="T",
        description="d",
        ratings=[Rating(name="Sujet", scale=scale)],
        boards=[Board(title="B0", description="desc0", style={}, elements=[])],
    )
    tmp = tempfile.mkdtemp(prefix="snap_api_test_")
    path = op.join(tmp, "t.snpk")
    snap.save(path)
    return path


class TestSecurity:
    def test_requires_token(self, client):
        assert client.get("/content//etc/hostname").status_code == 401
        assert client.get("/files//etc").status_code == 401
        assert client.get("/objects/whatever/image/x").status_code == 401

    def test_content_path_traversal_blocked(self, client, auth):
        # Absolute path outside the content dir must be denied.
        assert client.get("/content//etc/hostname", headers=auth).status_code == 403


class TestObjectLifecycle:
    def test_open_patch_save_close(self, client, auth, snap_path):
        r = client.get(f"/objects/open/{snap_path}", headers=auth)
        assert r.status_code == 200
        snap = r.json()
        sid = snap["id"]
        assert snap["version"] == 0
        rid = snap["ratings"][0]["id"]

        # patch a rating value with the correct expected_version -> version bumps
        r = client.patch(
            f"/objects/{sid}/field",
            headers=auth,
            json={"field_path": f"ratings.{{id:{rid}}}.value", "value": 1, "expected_version": 0},
        )
        assert r.status_code == 200
        assert r.json()["version"] == 1
        assert r.json()["has_changed"] is True

        # save + close now succeed (routes were broken before P1/P2)
        assert client.post("/objects/save", headers=auth, params={"object_id": sid}).status_code == 200
        assert client.request("DELETE", "/objects/close", headers=auth, params={"object_id": sid}).status_code == 200

    def test_numeric_index_path(self, client, auth, snap_path):
        sid = client.get(f"/objects/open/{snap_path}", headers=auth).json()["id"]
        r = client.patch(
            f"/objects/{sid}/field",
            headers=auth,
            json={"field_path": "boards.0.description", "value": "patched"},
        )
        assert r.status_code == 200

    def test_private_path_rejected(self, client, auth, snap_path):
        sid = client.get(f"/objects/open/{snap_path}", headers=auth).json()["id"]
        r = client.patch(
            f"/objects/{sid}/field",
            headers=auth,
            json={"field_path": "_filepath", "value": "/tmp/evil"},
        )
        assert r.status_code == 400

    def test_version_conflict(self, client, auth, snap_path):
        snap = client.get(f"/objects/open/{snap_path}", headers=auth).json()
        sid, rid = snap["id"], snap["ratings"][0]["id"]
        r = client.patch(
            f"/objects/{sid}/field",
            headers=auth,
            json={"field_path": f"ratings.{{id:{rid}}}.value", "value": 1, "expected_version": 999},
        )
        assert r.status_code == 409

    def test_no_version_bump_when_value_unchanged(self, client, auth, snap_path):
        snap = client.get(f"/objects/open/{snap_path}", headers=auth).json()
        sid, rid = snap["id"], snap["ratings"][0]["id"]
        field = f"ratings.{{id:{rid}}}.value"
        v1 = client.patch(f"/objects/{sid}/field", headers=auth, json={"field_path": field, "value": 1}).json()[
            "version"
        ]
        # same value again -> no change -> version stays
        v2 = client.patch(f"/objects/{sid}/field", headers=auth, json={"field_path": field, "value": 1}).json()[
            "version"
        ]
        assert v2 == v1


class TestSessionIsolation:
    def test_unsaved_edits_do_not_leak_across_sessions(self, client, snap_path):
        # Window 1: open + unsaved edit
        h1 = {"Authorization": f"Bearer {client.post('/session/').json()}"}
        s1 = client.get(f"/objects/open/{snap_path}", headers=h1).json()
        id1, rid = s1["id"], s1["ratings"][0]["id"]
        client.patch(
            f"/objects/{id1}/field", headers=h1, json={"field_path": f"ratings.{{id:{rid}}}.value", "value": 1}
        )

        # Window 2 (separate session) opens the same file -> independent copy
        h2 = {"Authorization": f"Bearer {client.post('/session/').json()}"}
        s2 = client.get(f"/objects/open/{snap_path}", headers=h2).json()
        assert s2["id"] != id1
        assert s2["has_changed"] is False
        assert next(r for r in s2["ratings"] if r["id"] == rid)["value"] is None

    def test_reopen_same_file_same_session_returns_same_item(self, client, auth, snap_path):
        id_a = client.get(f"/objects/open/{snap_path}", headers=auth).json()["id"]
        id_b = client.get(f"/objects/open/{snap_path}", headers=auth).json()["id"]
        assert id_a == id_b


@pytest.fixture()
def tmp_settings(monkeypatch):
    """Write the settings in a temporary file and restore the auto save setting after the test."""
    monkeypatch.setattr(lepton_app, "settings_f", op.join(tempfile.mkdtemp(prefix="snap_settings_"), "settings.json"))
    yield lepton_app.settings
    lepton_app.settings.get("snap.autosave").set_value(None)


class TestSettings:
    def test_set_setting(self, client, auth, tmp_settings):
        r = client.put("/settings/snap.autosave", headers=auth, json={"value": True})
        assert r.status_code == 200
        assert r.json()["value"] is True
        assert op.isfile(lepton_app.settings_f)
        # None resets to the default value
        assert client.put("/settings/snap.autosave", headers=auth, json={"value": None}).json()["value"] is False

    def test_set_setting_errors(self, client, auth, tmp_settings):
        assert client.put("/settings/snap.unknown", headers=auth, json={"value": True}).status_code == 404
        assert client.put("/settings/snap.autosave", headers=auth, json={"value": "yes"}).status_code == 400
        assert client.put("/settings/files.n_history", headers=auth, json={"value": True}).status_code == 400

    def test_add_group_keeps_stored_values(self, tmp_settings):
        from lepton.settings.models import Setting, Settings, SettingsGroup

        settings = Settings(groups=[SettingsGroup("g", "G", [Setting("a", "A", "int", default=1, value=5)])])
        settings.add_group(
            SettingsGroup("g", "New G", [Setting("a", "New A", "int", default=2), Setting("b", "B", "bool")])
        )
        assert settings.groups[0].title == "New G"
        assert settings.get("g.a").label == "New A"
        assert settings.get("g.a").value == 5
        assert settings.get("g.b").value is None

    def test_autosave(self, client, auth, snap_path, tmp_settings):
        snap = client.get(f"/objects/open/{snap_path}", headers=auth).json()
        sid, rid = snap["id"], snap["ratings"][0]["id"]
        field = f"ratings.{{id:{rid}}}.value"

        # Disabled: the modification is not saved
        r = client.patch(f"/objects/{sid}/field", headers=auth, json={"field_path": field, "value": 1})
        assert r.json()["has_changed"] is True

        # Enabled: each modification is saved
        client.put("/settings/snap.autosave", headers=auth, json={"value": True})
        r = client.patch(f"/objects/{sid}/field", headers=auth, json={"field_path": field, "value": None})
        assert r.json()["has_changed"] is False
        r = client.patch(f"/objects/{sid}/field", headers=auth, json={"field_path": field, "value": 1})
        assert r.json()["has_changed"] is False
        assert load_snap(snap_path).ratings[0].value == 1
