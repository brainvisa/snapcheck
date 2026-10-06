# SnapCheck
SnapCheck is a tool to annotate data displayed by graphical boards. Its main goal is to provides an interface to assign ratings to data observed throughout sets of screenshots.

## Python package
Provides Snap core objects and methods. Can be used to create Snaps from pipelines and other tools.

## Spnacheck GUI
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

To build the HTML documentation and export it in `DEST/snapcheck`:
```shell
pixi run export-docs DEST
```

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

