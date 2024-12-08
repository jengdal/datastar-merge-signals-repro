import json
import pathlib

from fastapi import FastAPI
from jinja2.utils import htmlsafe_json_dumps
from sse_starlette import EventSourceResponse
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

template_folder = pathlib.Path(__file__).parent.joinpath("./templates/").resolve()
static_folder = pathlib.Path(__file__).parent.joinpath("./static/").resolve()
app = FastAPI(debug=True)
app.mount("/static", StaticFiles(directory=static_folder), name="static")

templates = Jinja2Templates(
    directory=template_folder, lstrip_blocks=True, trim_blocks=True
)


def datastar_merge_signals(signals, only_if_missing=False):
    def dumps(
        *args,
        **kwargs,
    ):
        return json.dumps(*args, **kwargs)

    json_signals = htmlsafe_json_dumps(signals, dumps=dumps)
    data = [f"signals {json_signals}"]
    if only_if_missing:
        data.append("onlyIfMissing true")
    data = "\n".join(data)
    return {"event": "datastar-merge-signals", "data": data}


def datastar_fragment(
    fragment: str,
    selector: str | None = None,
    merge_type: str | None = None,
    view_transition: bool | None = False,
):
    data = []
    if selector:
        data.append(f"selector {selector}\n")
    if merge_type:
        data.append(f"mergeMode {merge_type}\n")
    if view_transition is False:
        data.append("useViewTransition false\n")
    fragment = "\n".join(f"fragments {f}" for f in fragment.strip().split("\n"))
    data.append(fragment)

    data = "".join(data)
    item = {"event": "datastar-merge-fragments", "data": data}
    return item


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    data_signals = {
        "obj": {
            "name": "",
            "labels": {"a": "a"},
        },
    }
    return templates.TemplateResponse(
        request=request, name="merge.html", context={"data_signals": data_signals}
    )


@app.put("/set-labels/", response_class=HTMLResponse)
async def set_labels(request: Request):
    data_signals = {
        "obj": {
            "labels": {"a": "a"},
        }
    }

    async def sse_wrapper():
        tmpl = templates.env.get_template("labels.html")
        yield datastar_merge_signals(data_signals)
        yield datastar_fragment(tmpl.render(data_signals=data_signals))

    return EventSourceResponse(sse_wrapper())


@app.put("/clear-labels/", response_class=HTMLResponse)
async def clear_labels(request: Request):
    data_signals = {
        "obj": {
            "labels": None,
        }
    }

    async def sse_wrapper():
        # yield datastar_fragment('<div id="labels-container"></div>')
        yield datastar_merge_signals(data_signals)

    return EventSourceResponse(sse_wrapper())
