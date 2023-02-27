FROM python:alpine

WORKDIR /root/

COPY . .

RUN pip --no-python-version-warning --disable-pip-version-check install --root-user-action=ignore .

ENTRYPOINT ["reviewcheck", "--no-notifications"]
