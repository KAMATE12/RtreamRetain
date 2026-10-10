# S1-03 — Local development environment

Student: Emmanuel Kamate
Group: M80-103CB-26
Sprint: 1 — October 5–18, 2026
Setup dates: October 9–10, 2026

## Objective

Prepare the local development environment and understand
the role of each tool used by StreamRetain.

## Environment and verified versions

- Operating system: Windows 10 Enterprise 22H2,
  build 19045.6456.
- Hardware: Lenovo ThinkPad T470s, Intel Core i5-7200U,
  8 GB RAM.
- Hardware virtualization: enabled.
- Git: 2.55.0.windows.5.
- Python used by the project: 3.12.10.
- Node.js: 24.21.0.
- npm: 11.19.0.
- WSL package: 3.0.1.0; default architecture: WSL 2.
- Docker Engine: 29.8.2.
- Docker Compose: 5.5.1.
- Angular CLI after the security fix: 21.2.26.
- MCP SDK after the security fix: 1.31.0.

## Repository

Remote: https://github.com/KAMATE12/RtreamRetain
Local folder: C:\Users\LAPTOP\Projects\RtreamRetain

The repository was cloned with Git.
The initial git status showed a clean working tree
on main, up to date with origin/main.

## Tool responsibilities

- Git tracks changes to project files.
- GitHub hosts the repository and project board.
- Python runs the backend.
- FastAPI provides the backend API.
- Angular provides the browser interface.
- Node.js runs frontend development and build tools.
- npm installs frontend dependencies.
- PostgreSQL will store synthetic customer records
  and retention actions.
- Docker and Compose will run the PostgreSQL service
  using the project's configuration.
- WSL 2 provides the Linux environment used by Docker Desktop.

## Backend dependency setup

Commands run from the repository root:

    py -3.12 -m venv .venv
    .\.venv\Scripts\python.exe --version
    .\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
    .\.venv\Scripts\python.exe -m pip check

Results:
- The virtual environment uses Python 3.12.10.
- Backend dependencies were installed successfully.
- pip check returned: No broken requirements found.

The project uses the Python executable inside .venv
to keep its dependencies separate from other projects.

## Frontend dependency setup

Commands run inside frontend:

    npm.cmd ci
    npm.cmd audit
    npm.cmd install-scripts ls
    npm.cmd audit fix
    npm.cmd audit
    npm.cmd run build

Results:
- Initial installation completed.
- The initial audit reported two high-severity affected
  packages related to one MCP SDK advisory:
  GHSA-6qxp-vccf-f47h.
- npm audit fix was run without --force.
- The subsequent audit reported zero known vulnerabilities.
- Angular CLI 21.2.26 and MCP SDK 1.31.0 were verified.
- The Angular build completed successfully.
- Build output: frontend/dist/frontend.

The updated package-lock.json records the dependency fix.

## Installation-script warnings

npm reported unconfigured install-script permissions for:
- @parcel/watcher
- esbuild
- lmdb
- msgpackr-extract

No blanket script approval was applied.
The build succeeded with the current installation.
These warnings remain documented; they were not reported
as resolved. Development-server operation is still to be tested.

## Local configuration

The local .env configuration was prepared from .env.example.
A local database password was configured consistently in
POSTGRES_PASSWORD and DATABASE_URL.

The password is not included in this document.

Verification:

    git check-ignore -v .env

Result:

    .gitignore:2:.env       .env

The example configuration remains shareable.
The local .env file is ignored by Git.

## Difficulties and solutions

- Python 3.12 was initially missing:
  installed using py install 3.12.
- The command py 3.12 was incorrect:
  corrected to py -3.12.
- Hardware virtualization was disabled:
  enabled in the Lenovo BIOS.
- The initial WSL command displayed help:
  installed current WSL with
  wsl --install --no-distribution, then restarted Windows.
- Docker initially could not reach its engine:
  opened Docker Desktop and resumed the engine.
  docker info then returned server information
  using the desktop-linux context.
- cd StreamRetain failed:
  the actual repository folder is named RtreamRetain.
- Frontend dependency vulnerabilities:
  applied npm audit fix and verified the audit and build.

## Angular CLI configuration

frontend/angular.json now contains analytics: false.
This disables Angular CLI usage analytics for this workspace.

## Verification limits and next steps

Completed:
- Tool version checks.
- Docker client-to-engine communication.
- Repository cloning.
- Backend and frontend dependency installation.
- Python dependency consistency check.
- Frontend security audit and successful build.
- Local configuration and ignore-rule verification.

Not yet verified:
- FastAPI server operation.
- Angular page operation in the browser.
- Angular-to-API communication.
- PostgreSQL container startup and application connection.

These runtime checks will be performed in the following
Sprint 1 tasks.