# RDFs-from-wikitables
Generating RDFs from wikitables using the wikitables-package

# Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py {storePagesWiki | generateRDFs | extractPages}
```

That uses the basic version. To use another Database change settings.py. Also insert wikipedia titles or wikipedia links as textfiles into /data and reference them correctly in the script that will be used.
