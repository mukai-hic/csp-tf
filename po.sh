#!/bin/bash
set -ex
curl -X POST -fs http://localhost:8080/detect \
-H "content-type: image/jpeg" \
--data-binary @input.jpg
