from components import defineCustomElements, createElement
from browser import webcomponent, window, document, alert, ajax, html
from browser.widgets.dialog import InfoDialog
import time

fetch = window.fetch
console = window.console
document = window.document
JSON = window.JSON

REGISTERED_USERS = 0
CONNECTED_USERS = 0

defineCustomElements('connected-users', '/components/connected_users/', "P")
defineCustomElements('ligne-tableau', '/components/tableau/', "TR")

def fetch_text(response):
	if response.status == 404:
		return Promise.new( lambda resolv, error : None  )
	return response.text()

def fetch_json(response):
	if response.status == 404:
		return Promise.new( lambda resolv, error : None  )
	return response.json()

async def my_handler(json):
	global REGISTERED_USERS, CONNECTED_USERS

	if not isinstance(json, list):
		json = [json]

	for user in json:
		add_form_value(user["pseudo"])
		add_row(user["pseudo"], user["quota"], user["quota_max"],
		        user["connexion"], user["connected"])

		if user["connected"]==True:
			CONNECTED_USERS += 1

	REGISTERED_USERS = len(json)
	update_connected_users(REGISTERED_USERS, CONNECTED_USERS)

fetch("http://localhost:8080/users/anon").then(fetch_json).then(my_handler)

def update_connected_users(n_users, number):
	try:
		line = document["id_tres_special_et_inutile"]
		line.remove()

	except KeyError:
		pass

	data = {
			"is" : "connected-users",
			"id" : "id_tres_special_et_inutile",
			"data-nusers" : str(n_users),
			"data-number" : str(number)
			}
	document["users"] <= createElement("P", attrs=data)

def add_row(pseudo, quota, quota_max, last_time, is_connected=False):
	try:
		if quota/quota_max > 0.95:
			quota_exceed = True

		else:
			quota_exceed = False

	except TypeError:
		alert("Les valeurs ne sont pas bonnes")
		return

	if last_time!=0:
		connexion = round((time.time() - last_time)/3600, 1)

	else:
		connexion = 0

	data = {"is" : "ligne-tableau",
			"data-pseudo" : pseudo,
			"data-connexion" : str(connexion),
			"data-quota" : str(quota),
			"data-quota_max" : str(quota_max)
			}

	if quota_exceed:
		data["class"] = "quota-exceed"

		if is_connected:
			data["class"] += " connected"

	elif is_connected:
		data["class"] = "connected"

	document["tableau"] <= createElement("TR", attrs=data)

def add_form_value(pseudo):
	document["delete-users"] <= html.OPTION(pseudo, value=pseudo)

def add_user(ev):
	global CONNECTED_USERS, REGISTERED_USERS

	pseudo = document["pseudo"].value
	quota = document["quota_user"].value

	if pseudo=="" or quota=="":
		alert("Le pseudo ou le quota ne doivent pas etre vides")
		return

	for line in document["tableau"].rows:
		if line["data-pseudo"]==pseudo:
			alert(f"L'utilisateur {pseudo} existe deja")
			return

	add_row(pseudo, 0, float(quota), 0, False)
	document["pseudo"].value = ""
	document["quota_user"].value = ""
	add_form_value(pseudo)
	REGISTERED_USERS += 1
	update_connected_users(str(REGISTERED_USERS), str(CONNECTED_USERS))
	ajax.post(f"http://localhost:8080/users/anon?pseudo={pseudo}&quota=0&quota_max={quota}&connexion=0&connected=false")

def del_user(pseudo):
	global REGISTERED_USERS, CONNECTED_USERS

	if pseudo=="":
		return

	line = document["tableau"].select_one(f"[data-pseudo=\"{pseudo}\"]")

	if "connected" in line.attrs.get("class", ""):
		CONNECTED_USERS -= 1

	REGISTERED_USERS -= 1
	update_connected_users(str(REGISTERED_USERS), str(CONNECTED_USERS))
	line.remove()
	line1 = document["delete-users"].select_one(f"[value=\"{pseudo}\"]")
	line1.remove()
	ajax.delete(url="http://localhost:8080/users/anon", data={"pseudo":pseudo})

def users(ev):
	pseudo = document["delete-users"].value
	del_user(pseudo)

document["valider"].type = "button"
document["valider"].bind("click", add_user)
document["delete_user"].bind("click", users)

