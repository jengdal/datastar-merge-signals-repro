FROM python:3.13-bookworm

RUN pip install uv

ADD ./ /srv/app/

WORKDIR /srv/app

RUN uv sync

ENTRYPOINT [ "./entrypoint.sh" ]
