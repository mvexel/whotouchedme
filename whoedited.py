#!/usr/bin/env python

# pylint: disable=C0103,C0111,R0902,R0913

import os
import argparse
from operator import itemgetter
import csv
import osmium


class WhoEditedHandler(osmium.SimpleHandler):
    def __init__(self, osm_username, keys, nodes=True, ways=True, relations=True, includemine=True, shallow=True):
        osmium.SimpleHandler.__init__(self)
        self.osm_username = osm_username
        self.keys = keys
        self.process_nodes = nodes
        if nodes:
            self.mynodes_ids = set()
            self.nodes_out = {}
        self.process_ways = ways
        if ways:
            self.myways_ids = set()
            self.ways_out = {}
        self.process_relations = relations
        if relations:
            self.myrelations_ids = set()
            self.relations_out = {}
        self.includemine = includemine
        self.shallow = shallow

    @staticmethod
    def make_summary(o, out_dict):
        record = (o.version, o.changeset, o.timestamp, o.user, o.deleted)
        if o.id in out_dict:
            out_dict[o.id].append(record)
        else:
            out_dict[o.id] = [record]

    def node(self, n):
        if self.process_nodes and (
            any(item in self.keys for item in [tag.k for tag in n.tags])
                or not self.keys):
            if n.user == self.osm_username:
                self.mynodes_ids.add(n.id)
                if self.shallow:
                    self.relations_out[n.id] = []
                if self.includemine:
                    self.make_summary(n, self.nodes_out)
            elif n.id in self.mynodes_ids:
                self.make_summary(n, self.nodes_out)

    def way(self, w):
        if self.process_ways and (
            any(item in self.keys for item in [tag.k for tag in w.tags])
                or not self.keys):
            if w.user == self.osm_username:
                self.myways_ids.add(w.id)
                if self.shallow:
                    self.relations_out[w.id] = []
                if self.includemine:
                    self.make_summary(w, self.ways_out)
            elif w.id in self.myways_ids:
                self.make_summary(w, self.ways_out)

    def relation(self, r):
        if self.process_relations and (
            any(item in self.keys for item in [tag.k for tag in r.tags])
                or not self.keys):
            if r.user == self.osm_username:
                self.myrelations_ids.add(r.id)
                if self.shallow:
                    self.relations_out[r.id] = []
                if self.includemine:
                    self.make_summary(r, self.relations_out)
            elif r.id in self.myrelations_ids:
                self.make_summary(r, self.relations_out)


def flatten(outdict):
    result = []
    for key in outdict:
        for item in outdict[key]:
            record = [key]
            record.extend(item)
            result.append(record)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pbf_history_file')
    parser.add_argument('osm_username')
    parser.add_argument('out_path')
    parser.add_argument('--keylist', help='a comma-separated list of tag keys. \
        Only features having tags with this key will be considered.')
    parser.add_argument('--skipnodes', action='store_true',
                        help='Do not output nodes')
    parser.add_argument('--skipways', action='store_true',
                        help='Do not output ways')
    parser.add_argument('--skiprelations', action='store_true',
                        help='Do not output relations')
    parser.add_argument('--includemine', action='store_true',
                        help='Do not output relations')
    parser.add_argument('--shallow', action='store_true',
                        help='Only consider my last edit to any feature')

    args = parser.parse_args()

    keys = []
    if args.keylist:
        keys.extend(args.keylist.split(','))

    osmium_handler = WhoEditedHandler(
        args.osm_username,
        keys,
        not args.skipnodes,
        not args.skipways,
        not args.skiprelations,
        args.includemine,
        args.shallow)
    osmium_handler.apply_file(args.pbf_history_file)

    # write out result files
    if not args.skipnodes:
        flat_nodeslist = flatten(osmium_handler.nodes_out)
        with open(os.path.abspath(os.path.join(args.out_path, 'nodes.csv')), 'w') as fh:
            csvwriter = csv.writer(fh)
            for row in sorted(flat_nodeslist, key=itemgetter(0, 1)):
                csvwriter.writerow(row)
    if not args.skipways:
        flat_wayslist = flatten(osmium_handler.ways_out)
        with open(os.path.abspath(os.path.join(args.out_path.items(), 'ways.csv')), 'w') as fh:
            csvwriter = csv.writer(fh)
            for row in sorted(flat_wayslist, key=itemgetter(0, 1)):
                csvwriter.writerow(row)
    if not args.skiprelations:
        flat_relationslist = flatten(osmium_handler.relations_out)
        with open(os.path.abspath(os.path.join(args.out_path, 'relations.csv')), 'w') as fh:
            csvwriter = csv.writer(fh)
            for row in sorted(flat_relationslist, key=itemgetter(0, 1)):
                csvwriter.writerow(row)


if __name__ == '__main__':
    main()
