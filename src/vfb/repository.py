import os
import json
import requests

class VFBKB():
    def __init__(self):
        self.db = None
        self.kb_owl_pattern_writer = None
        self.max_base36 = 1679615  # Corresponds to the base36 value of ZZZZZZ
        self.db_client = "vfb"
        self.client_id = os.environ['CLIENT_ID_AUTHORISATION']
        self.client_secret = os.environ['CLIENT_SECRET_AUTHORISATION']
        self.redirect_uri = os.environ['REDIRECT_URI_AUTHORISATION']
        self.authorisation_token_endpoint = os.environ['ENDPOINT_AUTHORISATION_TOKEN']


    ######################
    #### Core methods ####
    ######################

    def init_db(self):
        if not self.db:
            self.kb = os.getenv('KBserver')
            self.user = os.getenv('KBuser')
            self.password = os.getenv('KBpassword')
            try:
                if self.db_client=="vfb":
                    self.db = neo4j_connect(self.kb, self.user, self.password)
                    self.kb_owl_pattern_writer = KB_pattern_writer(self.kb, self.user, self.password)
                    self.kb_owl_edge_writer = kb_owl_edge_writer(self.kb, self.user, self.password)
                else:
                    self.db = GraphDatabase(self.kb, username=self.user, password=self.password)
                self.prepare_database()
                if os.getenv('LOAD_TEST_DATA'):
                    self.load_test_data()
                return True
            except Exception as e:
                print("Database could not be initialised: {}".format(e))
                return False
        else:
            return True

    def prepare_database(self):
        q_orcid_unique = "CREATE CONSTRAINT ON (a:Person) ASSERT a.orcid IS UNIQUE"
        q_projectid_unique = "CREATE CONSTRAINT ON (a:Project) ASSERT a.projectid IS UNIQUE"
        self.query(q_orcid_unique)
        self.query(q_projectid_unique)

    def load_test_data(self):
        test_cypher_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../testdata.cypher'))
        with open(test_cypher_path, 'r') as file:
            q_test_data = file.read()
        self.query(q_test_data)

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

    def query(self,q):
        print("Q: "+str(q))
        if self.init_db():
            if self.db_client == "vfb":
                x = self.parse_vfb_client_data(self.db.commit_list([q]))
            else:
                x = self.parse_neo4j_default_client_data(self.db.query(q,data_contents=True))
            return x
        else:
            raise DatabaseNotInitialisedError("Database not initialised!")