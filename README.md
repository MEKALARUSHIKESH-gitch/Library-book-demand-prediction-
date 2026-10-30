# AI Library Book Demand System

A Streamlit app for library inventory, book-demand predictions, borrowing records, and reading recommendations.

## Run locally

Use Python 3.13, then install the pinned dependencies and start Streamlit:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app creates and seeds `library.db` the first time it runs. The database is local and is intentionally not committed.

## Publish a live demo

GitHub Pages only hosts static websites; it cannot run this Python/Streamlit app. Deploy it from GitHub with [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this project folder to a GitHub repository. The repository root should contain `app.py` and `requirements.txt`.
2. Sign in to Streamlit Community Cloud with GitHub and create an app from that repository.
3. Select the branch containing the app, set **Main file path** to `app.py`, and choose Python 3.13 in the advanced settings.
4. Deploy. Community Cloud installs the versions in `requirements.txt`.

The model files are included in the repository. Keep them alongside `app.py`; their scikit-learn version must match the pinned dependency.

## Demo data and privacy

The app's SQLite database is local to its running instance. On Community Cloud, changes are temporary and can be lost when the app restarts or is redeployed. This is a demo setup, not persistent production storage. The librarian/admin screens are not protected by authentication, so do not use real or sensitive borrower data in a public deployment.
