!/bin/sh

curl https://registry.open.canada.ca/api/action/datastore_search \
  -H"Authorization:$API_KEY" -d '
{
  "resource_id": "7396a600-4a82-4843-8054-7d0f354d5901",
  "sort": "date_published desc"
}' >> kole_temp.json
