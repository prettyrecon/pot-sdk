#!/usr/bin/env bash

# for MongoDB Authentication
AUTH_MONGODB_HOST=localhost; export AUTH_MONGODB_HOST
AUTH_MONGODB_PORT=27017; export AUTH_MONGODB_PORT
AUTH_MONGODB_DB=testdb; export AUTH_MONGODB_DB

# for API (for both client and server
API_PREFIX=/test; export API_PREFIX
# combination of set([r(db), n(osql), t(sdb), o(mnise), f(ulltext), c(ustom), u(nittest)])_api
#API_NAME=u_api; export API_NAME
API_VERSION=1.0; export API_VERSION

# for API server
API_HOST=localhost; export API_HOST
API_PORT=35000; export API_PORT

unset PY_DEBUG
#PY_DEBUG=1; export PY_DEBUG
