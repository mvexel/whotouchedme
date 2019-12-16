# WhoTouchedMe

A command line tool that helps you find out who edited OSM features that you created or edited before.

## Requirements

* Python 3.7+
* [pyosmium](https://osmcode.org/pyosmium/) 2.15+


## To run

```
usage: whoedited.py [-h] [--keylist KEYLIST] [--skipnodes] [--skipways]
                    [--skiprelations]
                    pbf_history_file osm_username out_path
```

There are two required positional arguments:

* `pbf_history_file` --> full path to an OSM History PBF file.
* `osm_username` --> the OSM username to check against
* `out_path` --> Where the 1-3 output files will be written

And four optional arguments:

* `--skipnodes` --> Don't look at nodes
* `--skipways` --> Don't look at ways
* `--skiprelations` --> Don't look at relations
* `--keylist KEYLIST` --> A comma-separated list of OSM tag keys. Only features that have any of these keys will be considered.
* `--includemine` --> Include `osm_username`'s edits in output

## Output

The tool will output 3 CSV files with the following columns:

* OSM ID
* Version
* Changeset ID
* Edit timestamp
* OSM Username
* Feature deleted

There will be one file for each type of OSM feature: `nodes.csv`, `ways.csv`, `relations.csv`, unless you skip one of the feature types, see above.

Each file will have one line for an OSM feature version that superseded a version edited by you. if you toggle `--includemine`, your own edits will also be included.

The output will contain all newer edits since the *first* edit you made to a feature.