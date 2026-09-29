"""Sphinx configuration of the SnapCheck documentation.

Build it with ``make html`` (from this directory) in the lepton-dev-env environment: the python
packages (snapcheck, snapserve, snapclient) and the backend dependencies must be importable, as the
API reference and the REST API documentation are generated from the code.
"""

import dataclasses
import json
import os.path as op
import sys
import warnings
from datetime import date
from pathlib import Path
from warnings import warn

import sphinx_bootstrap_theme
from sphinx.util import inspect as sphinx_inspect

DOCS_DIR = Path(__file__).parent

# The docstrings of lepton (documented with the classes inheriting from it) use unknown numpydoc
# sections
warnings.filterwarnings("ignore", message="Unknown section", category=UserWarning, module="numpydoc")
sys.path.insert(0, op.abspath("../python"))

# -- Project information -------------------------------------------------------------------------

project = "SnapCheck"
author = "SnapCheck Developers (CATI team)"
td = date.today()  # noqa: DTZ011 - local date of the build
copyright = f"{td.year}, SnapCheck Developers (CATI team). Last updated on {td.isoformat()}"

pyproject_root = "../pyproject.toml"
with open(pyproject_root) as f:
    for line in f:
        if line.startswith("version = "):
            version = line.split("=")[1].strip().strip('"')
            break
    else:
        warn(f"Could not find version in {pyproject_root}")
        version = "0.0.0"
release = version

# -- General configuration -----------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "numpydoc",
    "sphinx_gallery.gen_gallery",
    "sphinxcontrib.autodoc_pydantic",
    "sphinxcontrib.fulltoc",
    "sphinxcontrib.openapi",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
}

# -- API reference (autodoc, autosummary, numpydoc, autodoc_pydantic) ----------------------------

# Generate a page per module, class and function (see api/index.rst and _templates/autosummary)
autosummary_generate = True
autosummary_imported_members = False
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "show-inheritance": True,
}
# PyQt5 is not needed to document the client
autodoc_mock_imports = ["PyQt5"]

# The members are listed by the autosummary templates
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False

# Pydantic models: list the fields with their type, default value and documentation
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_member_order = "bysource"
autodoc_pydantic_field_list_validators = False
autodoc_pydantic_field_show_constraints = False
# The fields docstrings are also their descriptions (use_attribute_docstrings): show them once
autodoc_pydantic_field_doc_policy = "docstring"


def list_pydantic_models() -> dict[str, list[str]]:
    """List the pydantic models of the packages, with their documented methods.

    With Sphinx 9, autodoc_pydantic does not replace the class documenter of automodule and
    autoclass: the autosummary templates use its autopydantic_model directive for these classes.
    This directive only documents the fields: the templates add the methods with automethod.
    """
    import importlib
    import inspect
    import pkgutil

    from pydantic import BaseModel

    models = {}
    for package_name in ("snapcheck", "snapserve", "snapclient"):
        package = importlib.import_module(package_name)
        for module_info in pkgutil.walk_packages(package.__path__, f"{package_name}."):
            try:
                module = importlib.import_module(module_info.name)
            except ImportError as e:
                warn(f"Cannot import {module_info.name}: {e}")
                continue
            for obj in vars(module).values():
                if isinstance(obj, type) and issubclass(obj, BaseModel) and obj.__module__ == module.__name__:
                    models[f"{obj.__module__}.{obj.__qualname__}"] = [
                        name
                        for name, member in vars(obj).items()
                        if not name.startswith("_") and inspect.isfunction(member) and member.__doc__
                    ]
    return models


autosummary_context = {"pydantic_models": list_pydantic_models()}


class _DefaultValue:
    """A default value displayed as the given text in the signatures."""

    def __init__(self, text: str):
        self.text = text

    def __repr__(self) -> str:
        return self.text


def clean_dataclass_signature(app, what, name, obj, options, signature, return_annotation):
    """Make the signatures of the dataclasses (Snap, Board, elements...) readable.

    The default value of their fields created with a ``default_factory`` is ``<factory>``, which Sphinx
    cannot parse: show the value created by the factory instead (``[]``, ``{}``...). The private fields
    (``_dir``, ``_path``...) are not given by the users: remove them.
    """
    if what != "class" or not signature or not dataclasses.is_dataclass(obj):
        return None
    sig = sphinx_inspect.signature(obj)
    params = []
    for param in sig.parameters.values():
        if param.name.startswith("_"):
            continue
        field = obj.__dataclass_fields__.get(param.name)
        if field is not None and field.default_factory is not dataclasses.MISSING:
            param = param.replace(default=_DefaultValue(repr(field.default_factory())))
        params.append(param)
    unqualified = app.config.autodoc_typehints_format == "short"
    signature = sphinx_inspect.stringify_signature(
        sig.replace(parameters=params), show_return_annotation=False, unqualified_typehints=unqualified
    )
    return signature, return_annotation


# -- Examples gallery ----------------------------------------------------------------------------

sphinx_gallery_conf = {
    "examples_dirs": "../examples",
    "gallery_dirs": "auto_examples",
    # Execute the examples, except the ones whose name contains "sgskip"
    "filename_pattern": "^((?!sgskip).)*$",
    "within_subsection_order": "FileNameSortKey",
    # Link the code of the examples to the API reference, and list the examples using each object
    # in its API page (minigallery directive of the templates)
    "doc_module": ("snapcheck",),
    "reference_url": {"snapcheck": None},
    "backreferences_dir": "generated/backreferences",
    "remove_config_comments": True,
}

# -- REST API ------------------------------------------------------------------------------------


def export_openapi_schema():
    """Export the OpenAPI schema of the backend in generated/openapi.json.

    It is rendered by developers/rest_api.rst.
    """
    from snapserve.app import app

    generated = DOCS_DIR / "generated"
    generated.mkdir(exist_ok=True)
    spec = app.app.openapi()
    spec["info"]["version"] = version
    with open(generated / "openapi.json", "w") as f:
        json.dump(spec, f, indent=2)


export_openapi_schema()

# -- HTML output ---------------------------------------------------------------------------------

html_theme = "bootstrap"
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_logo = "_static/logo.jpg"
html_static_path = ["_static"]
html_css_files = ["snapcheck.css"]
html_js_files = ["external_links.js"]

html_sidebars = {"**": ["localtoc.html", "searchbox.html"]}
html_show_sourcelink = False
html_theme_options = {
    "navbar_title": "SnapCheck",
    "bootswatch_theme": "flatly",
    "bootstrap_version": "3",
    "navbar_sidebarrel": False,
    "navbar_pagenav": False,
    "globaltoc_depth": 2,
    "navbar_links": [
        ("User guide", "user_guide"),
        ("Developers", "developers/index"),
        ("Examples", "auto_examples/index"),
        ("API reference", "api/index"),
        ("GitHub", "https://github.com/brainvisa/snapcheck", True),
    ],
}

htmlhelp_basename = "snapcheckdoc"


def setup(app):
    app.connect("autodoc-process-signature", clean_dataclass_signature)
