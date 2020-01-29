"""
Copyright 2020, University of Freiburg,
Chair of Algorithms and Data Structures.
Authors: Patrick Brosi <brosi@cs.uni-freiburg.de>,
         Claudius Korzen <korzen@cs.uni-freiburg.de>.
"""

import re
import time
import readline  # NOQA
import sys
import sqlite3


class SPARQL:
    """ A simple SPARQL engine for a SQLite backend. """

    def __init__(self):
        """
        Creates a new SPARQL engine.
        """
        # A pattern to parse the triples in the WHERE clause of a SPARQL query.
        self.triple_pattern = re.compile(
            '\\s?(\\?[^\\s]+|[^\\s]+)\\s+([^\\s]+)\\s+(\\?[^\\s]+|[^\\s]+)'
        )

    def sparql_to_sql(self, sparql):
        """
        Translates the given SPARQL query to a corresponding SQL query.

        PLEASE NOTE: there are many ways to express the same SPARQL query in
        SQL. Stick to the implementation advice given in the lecture. Thus, in
        case your formatting, the name of your variables / columns or the
        ordering differs, feel free to adjust the syntax
        (but not the semantics) of the test case.

        The SPARQL query in the test below lists all german politicians whose
        spouses were born in the same birthplace.

        >>> engine = SPARQL()
        >>> engine.sparql_to_sql("SELECT ?x ?y WHERE {"
        ...                      "?x occupation politician . "
        ...                      "?x country_of_citizenship Germany . "
        ...                      "?x spouse ?y . "
        ...                      "?x place_of_birth ?z . "
        ...                      "?y place_of_birth ?z "
        ...                      "}") # doctest: +NORMALIZE_WHITESPACE
        'SELECT t0.subject, \
                t2.object \
         FROM   wikidata as t0, \
                wikidata as t1, \
                wikidata as t2, \
                wikidata as t3, \
                wikidata as t4 \
         WHERE  t0.predicate="occupation" \
                AND t0.object="politician" \
                AND t1.predicate="country_of_citizenship" \
                AND t1.subject=t0.subject \
                AND t1.object="Germany" \
                AND t2.predicate="spouse" \
                AND t2.subject=t0.subject \
                AND t3.predicate="place_of_birth" \
                AND t3.subject=t0.subject \
                AND t4.predicate="place_of_birth" \
                AND t4.subject=t2.object \
                AND t4.object=t3.object;'

        """

        # Transform all letters to lower cases.
        sparqll = sparql.lower()

        # Find all variables in the SPARQL between the SELECT and WHERE clause.
        select_start = sparqll.find("select ") + 7
        select_end = sparqll.find(" where", select_start)
        variables = sparql[select_start:select_end].split()

        # Find all triples between "WHERE {" and "}"
        where_start = sparqll.find("{", select_end) + 1
        where_end = sparqll.rfind("}", where_start)
        where_text = sparql[where_start:where_end]
        triple_texts = where_text.split(".")
        triples = []
        for triple_text in triple_texts:
            m = self.triple_pattern.match(triple_text)
            subj = m.group(1).strip()
            pred = m.group(2).strip()
            obj = m.group(3).strip()
            triples.append((subj, pred, obj))

        # Find the (optional) LIMIT clause.
        limit_start = sparqll.find(" limit ", where_end)
        limit = sparql[limit_start + 7:].strip() if limit_start > 0 else None

        # create FROM statement, prepare WHERE
        # statement
        select = "SELECT "
        from_ = " FROM "
        where = " WHERE "
        limit_ = ""
        var_occ = {}  # key:=variable, value:=occurence of variable

        for i in range(len(triples)):
            if i != 0:  # after first query sparate to one before
                from_ += ", "
                where += " AND "

            # one dimension for each tripel
            from_ += "wikidata as t" + str(i)

            # predicate need to be equal with pattern
            where += "t" + str(i) + ".predicate=\"" + triples[i][1] + "\""
            # get occurence of variable
            if triples[i][0][0] == '?':  # subject
                if triples[i][0] in var_occ:
                    # add to dic
                    var_occ[triples[i][0]] += ["t" + str(i) + ".subject"]
                    # subject need to be equal with the variable
                    where += " AND t" + str(i) + ".subject=" + \
                             var_occ[triples[i][0]][0]
                else:
                    # extend list
                    var_occ[triples[i][0]] = ["t" + str(i) + ".subject"]

                if triples[i][2][0] == '?':  # object
                    if triples[i][2] in var_occ:
                        var_occ[triples[i][2]] += ["t" + str(i) + ".object"]
                        # object need to be equal with the variable
                        where += " AND t" + str(i) + ".object=" + \
                                 var_occ[triples[i][2]][0]
                    else:
                        # extend list
                        var_occ[triples[i][2]] = ["t" + str(i) + ".object"]

                else:
                    # object need to be equal with the pattern
                    where += " AND t" + str(i) + ".object=\"" + \
                             triples[i][2] + "\""

        # show columns of firt occurence of varable
        select += var_occ[variables[0]][0]
        for var in variables[1:]:
            select += ", " + var_occ[var][0]

        if limit is not None:
            limit_ = " LIMIT " + limit

        # Compose the SQL query and return it.
        return select + from_ + where + limit_ + ";"

    def process_sql_query(self, db_name, sql):
        """
        Runs the given SQL query against the given instance of a SQLite3
        database and returns the result rows.

        >>> engine = SPARQL()
        >>> sql = engine.sparql_to_sql("SELECT ?x ?y WHERE {"
        ...                            "?x occupation politician . "
        ...                            "?x country_of_citizenship Germany . "
        ...                            "?x spouse ?y . "
        ...                            "?x place_of_birth ?z . "
        ...                            "?y place_of_birth ?z"
        ...                            "}")
        >>> sorted(engine.process_sql_query("example.db", sql))
        ... # doctest: +NORMALIZE_WHITESPACE
        [('Fritz_Kuhn', 'Waltraud_Ulshöfer'), \
         ('Helmut_Schmidt', 'Loki_Schmidt'), \
         ('Karl-Theodor_zu_Guttenberg', 'Stephanie_zu_Guttenberg'), \
         ('Konrad_Adenauer', 'Auguste_Adenauer'), \
         ('Konrad_Adenauer', 'Emma_Adenauer'), \
         ('Konrad_Naumann', 'Vera_Oelschlegel'), \
         ('Waltraud_Ulshöfer', 'Fritz_Kuhn'), \
         ('Wolfgang_Schäuble', 'Ingeborg_Schäuble')]
        """

        # Run the SQL query against the database and return the result.
        db = sqlite3.connect(db_name)  # open db
        cursor = db.cursor()
        cursor.execute(sql)  # run query
        res = []
        # read results
        for row in cursor.fetchall():
            res.append(tuple("\t".join(row).split()))
        db.close()  # close db

        return res


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 sparql_to_sql.py <database> [<sparql_file>]")
        exit(1)

    # Reads the path to the SQLite3 database from the command line.
    db_filename = sys.argv[1]

    # Read path to file with SPARQL query
    if len(sys.argv) == 3:
        sparql_file = sys.argv[2]

    # Connect to the database.
    engine = SPARQL()

    while (True):
        # Read the SPARQL query to process from the command line.

        if len(sys.argv) == 3:
            # read from file
            try:
                sparql = open(sparql_file, "r").read()
            except Exception:
                print("Error with sparql-file.")
                sys.exit(1)
        else:
            # read from input
            sparql = input("Enter SPARQL query: ")

            # Translate the SPARQL query to an SQL query.
            try:
                sql = engine.sparql_to_sql(sparql)
            except Exception:
                print("Syntax error...")
                sys.exit(1)

        # Run the SQL query against the database.
        sql = engine.sparql_to_sql(sparql)
        time_ = time.monotonic()
        res = engine.process_sql_query(db_filename, sql)
        time_ = time.monotonic() - time_
        # Output the result rows.
        for pair in res:
            out = ""
            for item in pair:
                out += item + "\t"
            print(out)
        print(len(res), time_)
        # exit after executing query from file
        if len(sys.argv) == 3:
            exit(0)
