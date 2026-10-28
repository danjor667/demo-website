# Page Turner

A small Django bookstore: browse and search books, add them to a cart, apply a discount code and
place an order. Every page has a **Feedback** button that sends reports to the AmaliAI feedback
backend.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate        # creates db.sqlite3 with a sample catalogue
FEEDBACK_PROJECT_ID=<project id> python manage.py runserver
```

Then open http://localhost:8000.

## Feedback

| Variable | Default | Purpose |
|---|---|---|
| `FEEDBACK_API_URL` | `http://localhost:8080/api/v1` | Feedback backend, including `/api/v1` |
| `FEEDBACK_PROJECT_ID` | (none) | The project's ID in the feedback backend. Without it the button reports an error. |
| `FEEDBACK_PROJECT_NAME` | `Page Turner` | Sent with each report |

The browser posts the form to this site, and the server forwards it to `POST /feedback/submit`
with the page URL, browser and viewport size.

## Tests

```bash
python manage.py test
```

## AI-drafted fixes

`.github/workflows/ai-fix.yml` lets the feedback backend send a flagged feedback item to this
repository, where a coding agent drafts a fix and opens a draft pull request.
