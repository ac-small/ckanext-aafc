# Bilingual String Notes

## Introduction
For multilingual strings, we've been using alternative solution which usually involves hard coding strings in template instead of externalize the string because the preferred solutions was not implemented.
The issue is now fixed. A ITranslate interface is implemented and correctly load the complied message object that specific to our plugin.

In CKAN documentation, the multilingual solution using ITranslate interface involves in 2 parts: extract the target strings into a plain text message file, and then compile into a message object file for CKAN application to load.
In our implementation, the target string for translation need to be manually created in the plain text message file with ".po" extension. Then run "msgfmt" command to compile the message file.

## The process 
1. In template, put the target string in the format of {{ _("target_string") }}
2. in "aafc-ext" plugin directory under "ckanext/aafc/i18n/" update a few message file with following string
> 
>   msgid "target_string"
>
>   msgstr "translated_target_str"
> 
   in pot file, po files. The english version (under "en/LC_MESSAGES") is optional. The msgid will be the displayed value

3. Send the plain text file associated with the target language (i.e. French) to translation service for translation
4. compile the translated plain text message file. Go to "fr/LCMESSAGES" folder, run "msgfmt ckanext-aafc.po -o ckanext-aafc.mo".
5. Restart ckan application, the compiled message object should be loaded.

## Configuration change
In the ckan configruation, following 2 lines needs to be added. The directory value need to match the real environment.(the sample is from dev.ini inside VM)

ckan.i18n.extra_directory=/app/ckan/venv/src/ckanext-aafc/ckanext/aafc/i18n/
ckan.i18n.extra_locales=fr

