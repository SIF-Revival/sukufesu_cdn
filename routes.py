# base imports
import os
import hashlib
import json as _json
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

# Sanic import
import sanic
from sanic.response import json, file_stream, file, text
from aiofiles import os as async_os

# config import
import config

NOT_FOUND = json({
    "error": "FILE_NOT_FOUND",
    "status_code": 404
}, status=404)

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def expireDate(expire: bool = True) -> str:
    now = datetime.now()
    if expire: 
        now.__add__(3600 * 24 * 10)
    stamp = mktime(now.timetuple())
    return format_date_time(stamp) #Format: Wed, 22 Oct 2008 10:52:40 GMT

async def test(request):
    return json({"hello": "world"})

async def getAssetFile(request, assetPath=""):
    print(assetPath)
    path = config.SIF_BASE_ASSET_PATH + assetPath
    if os.path.exists(path):
        return await file_stream(path, headers={
            # "ETag": f"\"{etag}\"",
            "Last-Modified": expireDate(False),
            "Expires": expireDate()
        })
    else:
        return NOT_FOUND

async def getBatchFile(request, assetPath=""):
    print(assetPath)
    path = config.SIF_BASE_BATCH_PATH + assetPath
    if os.path.exists(path):
        return await file_stream(path, headers={
            # "ETag": f"\"{etag}\"",
            "Last-Modified": expireDate(False),
            "Expires": expireDate()
        })
    else:
        return NOT_FOUND

async def getAssetsList(request, os:str, version:str):
    path = f"{config.SIF_BASE_BATCH_PATH}{version}/"
    print(path)
    if os.path.exists(path):
        assetsList = []

        scandir = os.scandir(path)
        for file in scandir:
            assetsList.append({
                "size": os.path.getsize(f"{path}/{file.name}"),
                "url": f"{config.SIF_BASE_DOMAIN_PATH}{path[2:]}{file.name}"
            })

        return json({"response_data": assetsList, "status_code": 200})
    else:
        return NOT_FOUND

async def getVersions(request):
    versions = []
    for path in os.scandir(config.SIF_BASE_BATCH_PATH):
        if path.is_dir():
            versions.append(path.name)
    return json({
        "response_data": {
            "versions": versions
        },
    })

def add_external_routes(app):
    # GET
    app.add_route(test, '/', methods=["GET"])
    app.add_route(getAssetFile, '/assets/', methods=["GET"])
    app.add_route(getBatchFile, '/batch/', methods=["GET"])
    app.add_route(getAssetFile, '/assets/<assetPath:path>', methods=["GET"])
    app.add_route(getBatchFile, '/batch/<assetPath:path>', methods=["GET"])
    app.add_route(getVersions, '/api/versions', methods=['GET'])
    app.add_route(getAssetsList, '/api/getBatchAssets/<os:str>/<version:str>', methods=["GET"])

    @app.middleware('response')
    async def print_on_response(request, response: sanic.response.BaseHTTPResponse):
        # print("I print when a response is returned by the server")
        #response.headers['Access-Control-Allow-Origin'] = "*"
        #response.headers['Access-Control-Allow-Methods'] = "GET, POST"
        pass

    @app.middleware('request')
    async def prerequest(request: sanic.request.Request):
        #print("request made:", request.headers)
        pass