import os

print("SETTTTTTIIINNNNG ENVIRONMENT PLEASE KILL ME.")
os.environ["KBserver"] = "http://localhost:7474"
os.environ["KBuser"] = "neo4j"
os.environ["KBpassword"] = "neo"
# os.environ["KBserver"] = "http://kb.ids.virtualflybrain.org"
# os.environ["KBuser"] = "neo4j"
# os.environ["KBpassword"] = "vfb"
os.environ["CEDAR_API_KEY"] = "apiKey f851b4d7f816de777b27e92a8a6650ba46aba23161207144b5604fa4eae16dfd"
os.environ["CURATIONAPI"] = "http://localhost:5000/api"
os.environ["CURATIONAPI_USER"] = "https://orcid.org/cedar_crawler"
os.environ["CURATIONAPI_KEY"] = "cc845b9f-6ad5-4e97-a960-77fb096f4859"
os.environ["VFBCRAWLER_EMAIL_USER"] = "vfbcrawler@gmail.com"
os.environ["VFBCRAWLER_EMAIL_PASS"] = "ebi.2022"
os.environ["CRAWL_TYPE"] = '["Dataset", "Neuron", "Split", "SplitDriver"]'
os.environ["IMAGES_FOLDER_PATH"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../images")