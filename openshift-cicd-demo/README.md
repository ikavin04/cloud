# openshift-cicd-demo

## Project description

This beginner-friendly Flask application demonstrates Continuous Integration
with GitHub Actions and a CI/CD test pipeline with OpenShift Pipelines
(Tekton). The application exposes a welcome page, a health check, and a
version endpoint.

## Objectives and technologies

- Build and test a Python Flask web application.
- Run Flake8 and Nose automatically with GitHub Actions.
- Run the same tests in Tekton on Red Hat OpenShift.
- Deploy the container to OpenShift using Kubernetes resources and a Service.
- Use an OpenShift PersistentVolumeClaim (PVC) as the Tekton shared workspace.

Technologies: Python, Flask, Flake8, Nose, Docker, GitHub, GitHub Actions,
Tekton, OpenShift Pipelines, and OpenShift PVC.

## Folder structure

```text
openshift-cicd-demo/
├── app.py
├── sitecustomize.py
├── requirements.txt
├── README.md
├── Dockerfile
├── .gitignore
├── tests/
│   ├── __init__.py
│   └── test_app.py
├── .github/workflows/workflow.yml
├── .tekton/
│   ├── tasks.yml
│   └── pipeline.yml
└── openshift/
    ├── deployment.yaml
    └── service.yaml
```

## Application features

- `GET /` returns a welcome message.
- `GET /health` returns `{"status": "healthy"}`.
- `GET /version` returns the `APP_VERSION` environment variable, defaulting to
  `1.0.0`.
- The server listens on `0.0.0.0`; `PORT` defaults to `8080`.

## Local setup and verification

Run these commands from the project root (`openshift-cicd-demo`):

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

In another terminal, try `http://localhost:8080/`, or run:

```bash
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/version
```

Stop the server with `Ctrl+C`, then run quality checks:

```bash
flake8 app.py tests
```

On Python versions where Nose 1.3.7 needs its compatibility shim, set the
project directory on `PYTHONPATH` before running Nose:

```bash
# Linux/macOS:
PYTHONPATH=. nosetests -v tests/test_app.py
# Windows PowerShell:
# $env:PYTHONPATH = "."
# nosetests -v tests/test_app.py
```

The GitHub Actions and Tekton definitions set `PYTHONPATH` automatically.

## GitHub and GitHub Actions

Create an empty GitHub repository named `openshift-cicd-demo`, then run from
the project root. Replace the placeholder with your own repository URL:

```bash
git init
git add .
git commit -m "Add OpenShift CI/CD demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/openshift-cicd-demo.git
git push -u origin main
```

The workflow in `.github/workflows/workflow.yml` runs for pushes to `main` and
pull requests targeting `main`. Open the repository's **Actions** tab to see
the `Python CI` run. A green run verifies the checkout, Python setup,
dependency installation, Flake8, and Nose steps. This project does not claim
that a remote run succeeded until GitHub reports it.

## OpenShift Pipelines prerequisites

The commands in this section run in a terminal where `oc` is installed and
you are logged in to an OpenShift cluster:

```bash
oc version
oc whoami
oc get tektonconfig
oc get pods -n openshift-pipelines
```

If `oc get tektonconfig` is unavailable, ask the cluster administrator to
install or enable the Red Hat OpenShift Pipelines Operator. Operator names
and installation permissions depend on the cluster.

Create or select a project:

```bash
oc new-project openshift-cicd-demo
```

## Create the Tekton PVC and run the Pipeline

Create a file named `tekton-pvc.yaml` locally (or apply an equivalent PVC
approved by your cluster administrator):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pipeline-source-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Apply it from the project root:

```bash
oc apply -f tekton-pvc.yaml
oc get pvc pipeline-source-pvc
```

Apply the Tasks and Pipeline:

```bash
oc apply -f .tekton/tasks.yml
oc apply -f .tekton/pipeline.yml
oc get tasks,pipelines
```

The pipeline expects source code in the shared workspace. For a simple
demonstration, copy the project into the PVC with a separate upload Task or
use a cluster-approved Git clone Task. The required PVC, tasks, and Pipeline
definitions are provided here without pretending that a cluster has executed
them.

For clusters that already provide Tekton CLI support, create and start a
PipelineRun using the PVC:

```bash
tkn pipeline start openshift-cicd-demo-pipeline \
  -w name=shared-source,claimName=pipeline-source-pvc \
  --showlog
```

If `tkn` is not installed, create an equivalent `PipelineRun` through the
OpenShift console or with `oc` using the cluster's supported Tekton API
version. Check the result with:

```bash
tkn pipelinerun list
tkn pipelinerun logs --last
```

## Build and deploy to OpenShift

Build the image using your preferred registry. Do not use the literal
`YOUR_REGISTRY` value. For example, after building and pushing an image to a
registry you control, edit `openshift/deployment.yaml` and replace:

```text
YOUR_REGISTRY/openshift-cicd-demo:latest
```

with the complete image reference. Do not commit registry credentials:

```bash
docker build -t YOUR_REGISTRY/openshift-cicd-demo:latest .
docker push YOUR_REGISTRY/openshift-cicd-demo:latest
```

Then deploy from the project root:

```bash
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc rollout status deployment/openshift-cicd-demo
oc get pods,service
```

For an external route:

```bash
oc expose service/openshift-cicd-demo
oc get route openshift-cicd-demo
```

View logs and inspect failures:

```bash
oc logs deployment/openshift-cicd-demo
oc describe deployment openshift-cicd-demo
oc get events --sort-by=.lastTimestamp
```

## Troubleshooting

- **`nosetests` is not found:** activate `.venv` and run `pip install -r
  requirements.txt`.
- **Flake8 fails:** run `flake8 .` locally and fix the reported file/line.
- **PVC is `Pending`:** check `oc describe pvc pipeline-source-pvc` and ask
  the administrator which storage class is available.
- **Tekton Task cannot find files:** ensure the source is present in the
  `shared-source` PVC and that both Tasks receive the `source` workspace.
- **Image pull fails:** replace `YOUR_REGISTRY/...` with a reachable image
  reference and configure an image pull secret if the registry is private.
- **Probe fails:** confirm the container listens on port `8080` and that
  `/health` returns HTTP 200.

## Coursera evidence checklist

Collect screenshots or terminal output only from your own successful runs:

1. Application home page showing the welcome message.
2. `/health` response showing `{"status": "healthy"}`.
3. `/version` response showing the application version.
4. Local `flake8 .` output with exit code 0.
5. Local `nosetests -v tests/test_app.py` output showing passing tests.
6. GitHub Actions `Python CI` run showing all named steps passed.
7. OpenShift/Tekton PipelineRun showing `cleanup` and `nose` succeeded.
8. OpenShift deployment showing a running pod and accessible Service/Route.

Do not fabricate evidence. Record the date, command, and environment for each
piece, and redact tokens, passwords, and private registry credentials.
