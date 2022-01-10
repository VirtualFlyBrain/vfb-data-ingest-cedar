import os
from datetime import datetime as dt
from neo4jrestclient.client import GraphDatabase
from vfb_neo4j.vfb.uk.ac.ebi.vfb.neo4j.neo4j_tools import neo4j_connect
from vfb_neo4j.vfb.uk.ac.ebi.vfb.neo4j.KB_tools import KB_pattern_writer
from vfb_neo4j.vfb.uk.ac.ebi.vfb.neo4j.KB_tools import kb_owl_edge_writer


class VFBKB():
    def __init__(self):
        self.db = None
        self.kb_owl_pattern_writer = None
        self.max_base36 = 1679615  # Corresponds to the base36 value of ZZZZZZ
        self.db_client = "vfb"


    ######################
    #### Core methods ####
    ######################

    def init_db(self):
        if not self.db:
            self.kb = os.getenv('KBserver')
            self.user = os.getenv('KBuser')
            self.password = os.getenv('KBpassword')
            try:
                if self.db_client == "vfb":
                    self.db = neo4j_connect(self.kb, self.user, self.password)
                    self.kb_owl_pattern_writer = KB_pattern_writer(self.kb, self.user, self.password)
                    self.kb_owl_edge_writer = kb_owl_edge_writer(self.kb, self.user, self.password)
                else:
                    self.db = GraphDatabase(self.kb, username=self.user, password=self.password)
                return True
            except Exception as e:
                print("Database could not be initialised: {}".format(e))
                return False
        else:
            return True

    def parse_vfb_client_data(self, data_in):
        data = []
        for d_in in data_in:
            #print(d_in)
            columns = d_in['columns']
            #print(columns)
            for rec in d_in['data']:
                d = dict()
                print(rec)
                for i in range(len(columns)):
                    print(i)
                    d[columns[i]]=rec['row'][i]
                data.append(d)
        #print("DATAOUT: " + str(data))
        return data

    def parse_neo4j_default_client_data(self, data_in):
        #print("DATAIN: " + str(data_in.rows))
        data = []
        columns = []
        if data_in.rows:
            for c in data_in.rows[0]:
                columns.append(c)
        #print(str(columns))
        if data_in.rows:
            for d_row in data_in.rows:
                d = dict()
                for c in columns:
                    d[c] = d_row[c]
                data.append(d)
        #print("DATAOUT: " + str(data))
        return data

    def query(self, q):
        print("Q: "+str(q))
        if self.init_db():
            if self.db_client == "vfb":
                x = self.parse_vfb_client_data(self.db.commit_list([q]))
            else:
                x = self.parse_neo4j_default_client_data(self.db.query(q,data_contents=True))
            return x
        else:
            raise ValueError("Database not initialised!")

    def get_last_crawling_time(self, template_id):
        q = "MATCH (n:CrawlerLog {iri:'%s'}" % template_id
        q = q + ") RETURN n.lastCrawledOn as lastCrawledOn"

        results = self.query(q=q)
        if len(results) == 1:
            return results[0]['lastCrawledOn']
        return "2000-01-01T01:01:01-01:00"

    def update_last_crawling_time(self, template_id, last_crawled_on):
        q = "MERGE (n:CrawlerLog {{iri:'{template_id}', lastCrawledOn: '{lastCrawledOn}'}})"\
            .format(template_id=template_id, lastCrawledOn=last_crawled_on)

        results = self.query(q=q)


db = VFBKB()
