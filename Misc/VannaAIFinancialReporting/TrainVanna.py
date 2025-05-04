import json
import vanna
import pyodbc
from vanna.remote import VannaDefault
from Config import Configuration as Config

def get_ddls():
    file = open('TrainingRAG-Artifact/Proc.json', 'r')
    proc = json.load(file)
    file = open('TrainingRAG-Artifact/Tables.json', 'r')
    tables = json.load(file)
    file = open('TrainingRAG-Artifact/Views.json', 'r')
    views = json.load(file)
    data = []
    data.extend(tables)
    data.extend(views)
    data.extend(proc)
    return data

api_key = vanna.get_api_key(Config.EmailAddress)

vn = VannaDefault(model=Config.Vanna_Model_Name, api_key=Config.Vanna_API_Key)
 
vn.connect_to_mssql(odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};Server='+Config.SQLServer+';Database='+Config.Database+';Uid='+Config.UserName+';Pwd='+Config.Password+';Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;') # You can use the ODBC connection string here

print("Connection Successfull")
# The information schema query may need some tweaking depending on your database. This is a good starting point.
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")

# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
plan = vn.get_training_plan_generic(df_information_schema)
plan
 
print("Plan trained Successfull")
# If you like the plan, then uncomment this and run it to train
vn.train(plan=plan)

# Training P2
for query in get_ddls():
    vn.train(ddl = query["command"])

print("DDL trained Successfull")
# Training P3
f = open("TrainingRAG-Artifact/Documentation.txt", "r")
documentation = f.read()

vn.train(documentation = documentation)
print("Documentation trained Successfull")

trained_data = vn.get_training_data()
trained_data.to_csv("TrainingRAG-Artifact/training_summary.csv")
print("All Set!")

