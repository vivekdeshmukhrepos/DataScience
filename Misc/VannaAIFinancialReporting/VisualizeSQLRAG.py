import vanna
from vanna.remote import VannaDefault
from Config import Configuration
from vanna.flask import VannaFlaskApp
 
vn = VannaDefault(model=Configuration.Vanna_Model_Name, api_key=Configuration.Vanna_API_Key)
vn.connect_to_mssql(odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};Server='+Configuration.SQLServer+';Database='+Configuration.Database+';Uid='+Configuration.UserName+';Pwd='+Configuration.Password+';Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;') # You can use the ODBC connection string here

app = VannaFlaskApp(vn, allow_llm_to_see_data=True)
app.run()
