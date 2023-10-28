import json
import os
from aiohttp import web

async def POST(request):
        name = request.match_info.get('name', "Anonymous")
        print("Post request by", name)

        try:
                json_data = {
                             "pseudo" : request.rel_url.query["pseudo"],
                             "quota" : float(request.rel_url.query["quota"]),
                             "quota_max" : float(request.rel_url.query["quota_max"]),
                             "connexion" : float(request.rel_url.query["connexion"]),
                             "connected" : request.rel_url.query["connected"],
                            }

        except KeyError:
                return web.Response(text="Wrong arguments\n")

        if json_data["connected"]=="false": # no implicit conversion between str and bool
                json_data["connected"] = False
        else:
                json_data["connected"] = True

        json_file = json.dumps(json_data, indent=4)

        with open("./routes/users/{name}/"+json_data["pseudo"]+".json", 'w') as file:
                file.write(json_file)

        return web.Response(text="Successfully executed query\n")

async def DELETE(request):
        name = request.match_info.get("name", "Anonymous")
        print("DELETE request by", name)

        try:
                pseudo = request.rel_url.query["pseudo"]

        except KeyError:
                return web.Response("Wrong arguments\n")

        try:
                os.remove("./routes/users/{name}/"+pseudo+".json")

        except FileNotFoundError:
                print(f"Can't delete {pseudo} user")
                return web.Response(text="User not found\n")

        print(f"Succesfully deleted {pseudo} user")
        return web.Response(text="Succesfully executed query\n")

async def GET(request):
        name = request.match_info.get('name', "Anonymous")
        print("GET request by", name)

        # #### get GET parameters : [url]?name=XXX ####
        query_name = None
        if 'qname' in request.rel_url.query:
                query_name = request.rel_url.query['qname']

        if query_name is None:
                users = []

                for file in os.listdir("./routes/users/{name}"):
                        if file.endswith(".json"):
                                with open("./routes/users/{name}/"+file) as json_file:
                                        users.append(json.load(json_file))

                return web.json_response(users)

        with open("./routes/users/{name}/"+query_name+".json") as json_file:
                res = json.load(json_file)

        # #### for JSON ####
        return web.json_response(res)

        # #### for text ####
        # text = "Hello, " + name
        # return web.Response(text=text)