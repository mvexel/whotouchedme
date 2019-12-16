#!/usr/bin/env python

# pylint: disable=C0103,C0111,R0902,R0913

import os
import argparse
from operator import itemgetter
import csv
import osmium


class WhoEditedHandler(osmium.SimpleHandler):
    def __init__(self, osm_username, keys, nodes=True, ways=True, relations=True, includemine=True):
        osmium.SimpleHandler.__init__(self)
        self.osm_username = osm_username
        self.keys = keys
        self.process_nodes = nodes
        if nodes:
            self.my_edited_nodes = set()
            self.other_edited_nodes = set()
        self.process_ways = ways
        if ways:
            self.my_edited_ways = set()
            self.other_edited_ways = set()
        self.process_relations = relations
        if relations:
            self.my_edited_relations = set()
            self.other_edited_relations = set()
        self.includemine = includemine

    @staticmethod
    def make_summary(o):
        return (o.id, o.version, o.changeset, o.timestamp, o.user, o.deleted)

    def node(self, n):
        if self.process_nodes and (
            any(item in self.keys for item in [tag.k for tag in n.tags])
                or not self.keys):
            if n.user == self.osm_username:
                self.my_edited_nodes.add(n.id)
                if self.includemine:
                    self.other_edited_nodes.add(self.make_summary(n))
            elif n.id in self.my_edited_nodes:
                self.other_edited_nodes.add(self.make_summary(n))

    def way(self, w):
        if self.process_ways and (
            any(item in self.keys for item in [tag.k for tag in w.tags])
                or not self.keys):
            if w.user == self.osm_username:
                self.my_edited_ways.add(w.id)
                if self.includemine:
                    self.other_edited_ways.add(self.make_summary(w))
            elif w.id in self.my_edited_ways:
                self.other_edited_ways.add(self.make_summary(w))

    def relation(self, r):
        if self.process_relations and (
            any(item in self.keys for item in [tag.k for tag in r.tags])
                or not self.keys):
            if r.user == self.osm_username:
                self.my_edited_relations.add(r.id)
                if self.includemine:
                    self.other_edited_relations.add(self.make_summary(r))
            elif r.id in self.my_edited_relations:
                self.other_edited_relations.add(self.make_summary(r))


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
        args.includemine)
    osmium_handler.apply_file(args.pbf_history_file)

    # write out result files
    if not args.skipnodes:
        with open(os.path.abspath(os.path.join(args.out_path, 'nodes.csv')), 'w') as fh:
            csvwriter = csv.writer(fh)
            for row in sorted(osmium_handler.other_edited_nodes, key=itemgetter(0, 1)):
                csvwriter.writerow(row)
    if not args.skipways:
        with open(os.path.abspath(os.path.join(args.out_path, 'ways.csv')), 'w') as fh:
            csvwriter = csv.writer(fh)
            for row in sorted(osmium_handler.other_edited_ways, key=itemgetter(0, 1)):
                csvwriter.writerow(row)
    if not args.skiprelations:
        with open(os.path.abspath(os.path.join(args.out_path, 'relations.csv')), 'w') as fh:
            csvwriter = csv.writer(fh)
            for row in sorted(osmium_handler.other_edited_relations, key=itemgetter(0, 1)):
                csvwriter.writerow(row)


if __name__ == '__main__':
    main()
