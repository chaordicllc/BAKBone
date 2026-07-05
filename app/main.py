from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from eventsourcing.application import Application
from eventsourcing.domain import Aggregate, event

# --- 1. THE EVENT SOURCING LAYER ---
# This defines our data. Instead of updating a row, we record events.
class UserRegistration(Aggregate):
    @event('Registered')
    def __init__(self, username: str):
        self.username = username

# This handles saving and retrieving those events from PostgreSQL
class UserRegistryApp(Application):
    def register_user(self, username: str) -> str:
        # Create a new aggregate (this automatically generates a "Registered" event)
        user = UserRegistration(username=username)
        # Save the event to the database
        self.save(user)
        return f"Successfully registered {username}!"

    def get_all_users(self):
        # A simple helper to list usernames from our event stream
        # In a production app, you would use a "Read Model" (CQRS)
        usernames = []
        for recording in self.notification_log.select(topics=['__main__:UserRegistration']):
            # Reconstruct the aggregate from its events to read the name
            user = self.repository.get(recording.originator_id)
            usernames.append(user.username)
        return usernames

# --- 2. THE FASTAPI & HTMX LAYER ---
app = FastAPI()

# Initialize our Event Sourcing application when FastAPI starts
@app.on_event("startup")
def startup_event():
    app.state.event_app = UserRegistryApp()

# BASE PAGE: Serves the initial HTML structure
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HTMX + EventSourcing Stack</title>
        <!-- Load HTMX from a content delivery network (CDN) -->
        <script src="https://unpkg.com"></script>
        <style>
            body { font-family: sans-serif; margin: 40px; }
            input, button { padding: 8px; margin: 5px 0; }
            ul { list-style-type: square; padding-left: 20px; }
        </style>
    </head>
    <body>
        <h1>User Registry (Event Sourced)</h1>
        
        <!-- HTMX FORM: Intercepts the submit, sends a POST request, 
             and replaces the <ul> element with the server's response -->
        <form hx-post="/register" hx-target="#user-list" hx-swap="outerHTML">
            <input type="text" name="username" placeholder="Enter username" required>
            <button type="submit">Register User</button>
        </form>

        <h3>Registered Users:</h3>
        <ul id="user-list">
            <li>No users registered yet.</li>
        </ul>
    </body>
    </html>
    """

# HTMX ENDPOINT: Processes form, stores the event, and returns a raw HTML fragment
@app.post("/register", response_class=HTMLResponse)
def register_user(username: str = Form(...)):
    event_app = app.state.event_app
    
    # Save the registration event to the database
    event_app.register_user(username)
    
    # Get the updated list of all users from the event log
    all_users = event_app.get_all_users()
    
    # Return JUST the <ul> fragment. HTMX automatically swaps this into the page!
    html_fragment = '<ul id="user-list">'
    for user in all_users:
        html_fragment += f"<li>{user}</li>"
    html_fragment += "</ul>"
    
    return html_fragment
