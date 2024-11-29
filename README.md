# WHERE ON EARTH
#### Video Demo: https://youtu.be/u7Dzbzo5Ha4
#### Description: A web-based application that allows users to maintain and visualise a record of where on earth they have been
#### Command: flask run / flask run --host=0.0.0.0 --port=5000

This web-based application that has been developed using HTML, CSS, JavaScript, Python, and SQL.

The layout (see layout.html) features a navigation bar which supports easy navigation around the website. The html utilises Bootstrap for basic formatting of the navigation bar as well as other common features throughout the application. The overall look and feel aims to be clean and spacious to compliment the user-friendly nature of the website. 

The log-in page (see login.html) simply requires a password of minimum 6 characters. The password is protected using hash values. Any issues in the validation of the log-in details will be passed to the user via an appropriate flash message. These are managed using Jinja, and colour-coded dependant on whether it is an error message, or a success message.

New users are able to toggle to the registration page (see register.html) which requires a unique username, a password and confirmation of the chosen password. Again, any issues in the validation of the registration details will be passed to the user via an appropriate flash message.

With the exception of the pages mentioned above, all other html files are protected by a function titled "login_required" (see helpers.py). Once logged in, users will also have the option to reset their password (see reset.html), provided they can recall their current password. There is also the option to delete their account entirely.

Upon logging in, users will be taken to the home page (see index.html) which displays the username and the number of countries and territories the user has been to, based on the database (see whereonearth.db).

Users can update the database by navigating to the checklists page (see checklist.html) and completing or updating the checklist of countries and territories. These have been organised into dropdown lists by region for ease of navigation, and once updated the user can submit the checklist by clicking on the "save" button. The dropdown buttons are mapped against the relevant content underneath and utilise JavaScript to either reveal or hide the content.

The full list of countries and territories has been sourced from an API found at https://restcountries.com/v3.1/all. The countries are stored in a database within whereonearth.db, including the country name, the 3-letter code, the flag, the region and whether it is a country or a territory. This database can be updated at any time by running countries.py.

Users can also visualise the data by navigating to the world map page (see scratchmap.html) which initialises a map using Leaflet (see https://leafletjs.com/), overlays a map tile sourced from https://carto.com/basemaps and references GeoJSON sourced from an API found at https://geojson-maps.kyd.au/. Using these resources and the database in whereonearth.db, the page will display a map of the world with individual countries highlighted, if visited by the user.

The pinboard page (see pinboard.html) renders a similar map, but has added interactivity which allows the user to add and remove pins from the map at the click of a button, and enables them to mark notable locations to which they have travelled. This functionality is built within JavaScript and also leans on some pop-up functionality provided by Leaflet. The longitude and latitude of these pins are automatically saved on the SQL database, allowing previously added pins to be added to the page when it is next loaded. The pin icons are sourced from https://icons8.com.

The full schema for the SQL database tables are as follows:

    CREATE TABLE sqlite_sequence(name,seq);
    CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL UNIQUE, hash TEXT NOT NULL UNIQUE);
    CREATE TABLE visits (user_id INTEGER NOT NULL REFERENCES users(id), country_id INTEGER NOT NULL REFERENCES countries(id));
    CREATE TABLE markers (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL REFERENCES users(id), latitude REAL NOT NULL, longitude REAL NOT NULL);
    CREATE TABLE countries (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL UNIQUE, flag TEXT NOT NULL, region TEXT NOT NULL, unMember TEXT NOT NULL);

The application is viewable on both desktop and mobile and the JavaScript and CSS make specific adjustments to the parameters of the maps and to improve the dimensions and navigation. There are also subtle differences when rendering each map, depending whether it is for the 'Scratch Map' or the 'Pinboard'. The maxZoom is limited for the 'Scratch Map' given the purpose of the page is to provide a large-scale view of the world map with countries highlighted. There are also slight discrepancies between the data sources for the checklists of countries and territories versus the GeoJSON data. These are limited to non-sovereign territories, and therefore don't make a large-scale impact to the visualisation on the map. Given further time and resource, it would be optimal to obtain data from a single source which can provide aligned country data and GeoJSON items, however this proved to be very time consuming.. 

Conversely, the 'Pinboard' map allows for greater zoom and therefore detail on the map, which allows the user to apply as many pins as they wish to each country. This provides the user with a second way to visualise their travels, which compliments the first, and is more accurate subject to how it is used.