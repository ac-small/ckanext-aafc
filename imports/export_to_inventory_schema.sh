!/bin/sh

curl -s https://registry.open.canada.ca/api/action/datastore_search \
  -H"Authorization:$API_KEY" -d '
{
  "resource_id": "7396a600-4a82-4843-8054-7d0f354d5901",
  "sort": "ref_number desc"
}' | \
 jq --compact-output '.result.records[] | select(.date_published == null) | {title_translated: {en: .title_en, fr: .title_fr}, notes_translated: {en: .description_en, fr: .description_fr}, inv_eligible_release: .eligible_for_release, inv_ref_number: .ref_number, inv_id: ._id, inv_program_align: .program_alignment_architecture_en, owner_org: "ffb385d6-94cd-481e-9656-5f6b2318d323", private: "false", type: "aafc-base-dataset", aafc_future_schema_target: "inv_open_data" } '

### TEST LOAD THE OUTPUT OF ABOVE
### ckanapi load datasets -I kole_load_inventory.json -l load_log.txt -c /etc/ckan/production.ini -u <userID>
