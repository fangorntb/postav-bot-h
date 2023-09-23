from pathlib import Path

from fastapi import Security
from starlette.staticfiles import StaticFiles

from scripts.core.api import (
    Router,
    Group,
    get_app,
    favicon_endpoint,
    swagger,
    process_time_middleware,
    Mount,
)
from scripts.core.security import permission_setter
from scripts.repr.api.endpoints.kn_base import (
    add_files_to_base,
    get_meta,
    delete_data,
    get_pages,
)

from scripts.repr.api.endpoints.ouauth2 import login_for_token, register
from scripts.repr.api.endpoints.queries import (
    send_query,
    similar_query,
    estimate_query,
)

API = get_app(
    Router('get', 'favicon.ico', favicon_endpoint('static/favicon-32x32.png'), include=False),
    Group(
        Router('post', 'token', login_for_token, include=True),
        Router('post', 'register', register, include=True),
        tags=['ouauth2']
    ),
    Router(
        'get',
        '/docs',
        swagger('POSTAV-BOT API', '/static/favicon-32x32.png'),
    ),
    Group(
        Router('get', path='query/all/similar', endpoint=similar_query),
        Router('post', path='query/send', endpoint=send_query),
        Router('get', path='query/{id}/estimate', endpoint=estimate_query),
        tags=['queries'],
        dependencies=[Security(permission_setter('user.sample'))]
    ),
    Group(
        Router('get', path='doc-base/meta', endpoint=get_meta),
        Router('get', path='doc-base', endpoint=get_pages),
        Router('post', path='doc-base', endpoint=add_files_to_base),
        Router('delete', path='doc-base', endpoint=delete_data),
        tags=['doc-base'],
        dependencies=[Security(permission_setter('user.admin'))],
    ),
    middlewares=[process_time_middleware],
    mount=[
        Mount(str(Path.cwd() / 'data'), StaticFiles(directory='data'), 'data'),
        Mount(str(Path.cwd() / 'static'), StaticFiles(directory='static'), 'static')
    ],
    openapi_kwargs={
        'title': 'POSTAV-BOT API',
        'version': '0.1',
        'logo_url': 'favicon.ico'
    },
    **{
        'docs_url': '/',
        'redoc_url': None,
        "swagger_ui_parameters": {"syntaxHighlight.theme": "obsidian"}
    }
)
