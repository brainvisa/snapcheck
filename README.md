# SnapCheck
SnapCheck is a tool to annotate data displayed by graphical boards. Its main goal is to provides an interface to assign ratings to data observed throughout sets of screenshots.


## Quick Start


## Main Concepts

### Elements
Any piece of data displayed throughou web frontend. Exemple: images (JPEG, PNG, GIF...)

### Ratings
A rating is an annotation based on a scale wich may be accompagnied by a comment.

### Board
A set of elements which are displayed together. Each board can refer to several ratings.

### Snaps
The set of ratings and boards plus a general comment.


## Make a snap

### First create a rating scale
```python
from snapcheck.snap.rating import RatingScale, RatingScaleItem

generic_scale = RatingScale(
    description="Generic Scale",
    ratings=[
        RatingScaleItem(name="Bad", value=0, description="Too bad data", color="red"),
        RatingScaleItem(name="Ok", value=1, description="Good enough data", color="lightgreen"),
        RatingScaleItem(name="Excellent", value=2, description="Outstanding sample", color="green"),
    ],
)
```

### Create some ratings
```python
from snapcheck.snap.rating import Rating

fa_rating = Rating(
    id="tracto_fa",
    name="Carte de FA",
    description="Qualité de la carte de FA",
    scale=generic_scale,
)
md_rating = Rating(
    id="tracto_md",
    name="Carte de MD",
    description="Qualité de la carte de MD",
    scale=generic_scale,
)
```

### Create a board
```python
from snapcheck.snap import Board, ImageElement

metrics_board = Board(
    title="Cartes de métriques",
    description="Vérifiez la qualité des cartes de métriques.",
    elements=[
        ImageElement(
            title="Carte de FA",
            src=".local/demo_sources/CST_FA_and_bundles_masks.png",
            intended_ratings=[fa_rating],
        ),
        ImageElement(
            title="Carte de MD",
            src=".local/demo_sources/CST_MD_and_bundles_masks.png",
            intended_ratings=[md_rating],
        ),
    ],
)
```


### And save it in a new snap file
```python
from snapcheck.snap import load_snap

qc = Snap(
    title="Tractométrie",
    description=f"Tractométrie du CST (Corticospinal Tract) pour le sujet {visit.subject}/{visit.visit}",
    metadata=visit.__dict__,
    ratings=[
        subject_observations,
        b0_rating,
        mni_registration_rating,
        fa_rating,
        md_rating,
    ]
    + bundles_ratings,
    boards=[preproc_board, cst_board, metrics_board],
)

f = ".local/demo.snpk"
# qc.to_json(f)
qc.save(f)
```


## The GUI Framework
SnapCheck is made as a Web App. It is composed of a backend written in Python and a frontend, the GUI, written if TypeScript (Javascript).

### The framwork
#### The core package (python)
The core python package, named "snapcheck", provide all it is need to create and read snap files (.snpk).

#### Backend
The backend end use [FastAPI](https://fastapi.tiangolo.com/) to serve the snaps, settings and track some usefull data for the GUI (like the last loaded files paths).

#### Frontend
The frontend use the well known [React](https://react.dev/) typescript framework.

The backend and the frontend can communicate thanks to an javascript API automatically generated from the FastAPI backend.

#### The client
Even if the SnapCheck GUI can be displayed by any web browser, a Qt based client is also provided to get a better experience (avoid to lost screen space and get a better focus).


### Run the GUI
The `snapcheck` command (or `pixi run snapcheck` from the sources) starts the backend, then the Qt client
which serves the frontend. The backend is stopped when the client is closed.
```shell
snapcheck [--host 127.0.0.1] [--backend-port 8050] [--frontend-port 3000]
```
From the sources, the frontend is served by the Vite development server. In the installed package,
the built frontend is served by the client.

The backend and the client can also be started separately:
```shell
# Backend. $SNAP_ALLOW_ORIGINS adds origins allowed to call the API (CORS), comma separated.
# By default, only the frontend ports 3000 and 5173 are allowed.
SNAP_ALLOW_ORIGINS=http://127.0.0.1:3050 python -m snapserve --port 8060 [--secret SECRET] [--session ID]
# Qt client, the frontend uses the backend at --api-url (given to the page with ?api=<url>)
python -m snapclient --port 3050 --api-url http://127.0.0.1:8060 [--jwt TOKEN]
```

#### Dev and Debugging
Set the ```SNAP_UNSAFE``` environment variable to 1 to disable API security checks.


## Install

### For development
The project use [Pixi](https://pixi.sh/latest/) (Conda) to manage dependencies and build.
The frontend depends on the `@lepton/core` library, built in `../lepton/dist` (see the lepton README).

```shell
pixi shell
npm install
npm run sass        # compile the SASS files (or use a SASS live compiler in VSCode)
npm run build_api   # generate the API client, see below
```

#### The API client
The typed API client of the frontend (`src/api/generated/`, imported as `@lepton/api`) is generated from
the OpenAPI schema of the FastAPI backend. It is not versioned: generate it after cloning and after each
change of the backend API (routes, parameters or models):
```shell
npm run build_api
```
It runs two steps:
1. `python scripts/export_openapi.py`: loads the backend app (`snapserve.app`) and exports its OpenAPI schema
   in `openapi.json`. The python environment must provide the backend dependencies (lepton, lepton_common,
   fastapi...), like the `lepton-dev-env` environment.
2. `npx @hey-api/openapi-ts`: generates the client in `src/api/generated/` (types, SDK and TanStack Query
   options), as configured in `openapi-ts.config.ts`.

Then check that the frontend still compiles with `npm run typecheck`. The generated files must not be edited.

The conda and wheel builds (see below) always regenerate the API client.

### Build and publish the packages
Two conda packages are built with [rattler-build](https://rattler.build) (`recipe/recipe.yaml`):
- `snapcheck`: the core python package (no GUI)
- `snapclient`: the application (Qt client, backend and built frontend), started with the `snapcheck` command

They depend on `lepton-common` and `lepton-app`, which must be available in the forge (local conda channel).
```shell
pixi run build-conda [FORGE]    # packages in ./output/noarch
pixi run publish-conda FORGE    # build, then publish in the forge
pixi run build-wheel FORGE      # wheel (pip / uv) in ./output/wheels, frontend included
```
`FORGE` can also be set with the `LEPTON_FORGE` environment variable.
From the development environment (`lepton-dev-env`), `pixi run build-all` builds all the projects.

Install the application from a forge:
```shell
pixi global install -c file:///path/to/forge -c https://prefix.dev/conda-forge snapclient
snapcheck
```

## Test

```
pixi run client
// or
python python/snapclient/main.py
```




# TODO

Snap
~~~~
* pouvoir ajouter des notes à un board voir un snap
* implémenter les notes booléenne et avac/sans commentaires
* ajouter un commentaire global
* note par défaut avec un flag qui dit si la valeur a été changée
* flag pour identifier si le snap est a été complété

Back
~~~~
* numéro de session dans le JWT, possible?
    => réouverture d'une session GUI en l'état?

* save sidebar sections heights in user settings
* make each section hiddable
* prendre en compte les notes booléennes
* ajouter l'élement viewer3d

GUI
~~~
* scroll sur les planches
* navigation avec les flêches aussi
* grossiessement du menu lors du dezoom sur les boards
* transformation des boards board/board
* lorsqu'un fichier est ouvert depuisles fichiers récents, afficher le dossier du fichier dans le broswer de fichiers
* clear le champs de recherche du broswer lorsqu'on change de fichier
* bien gérer le has_changed lorsqu'on modofie dans la sidebar
* afficher la nouvelle valeur lorsqu'on modifie la note via le menu contextuel
* férer la fermeture des snap correctement
