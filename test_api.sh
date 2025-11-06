curl http://localhost:5002/debug/request-headers

curl http://localhost:5000/debug/service-token \
  -H "Cookie: session=<your-session-cookie>"

curl http://localhost:5002/debug/request-headers \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "X-Service-Name: frontend"


  