"""
  Config
"""
#Application configuration File
################################
#Secret key that will be used by Flask for securely signing the session cookie
# and can be used for other security related needs
SECRET_KEY = 'SECRET_KEY'
#######################################
#Minimum Number Of Tasks To Generate
MIN_NBR_TASKS = 1
#Maximum Number Of Tasks To Generate
MAX_NBR_TASKS = 10
#Time to wait when producing tasks
WAIT_TIME = 2
#Webhook endpoint Mapping to the listener
WEBHOOK_RECEIVER_URL = 'http://192.168.1.101:8123/'
#######################################
#Map to the REDIS Server Port
BROKER_URL = 'redis://localhost:6379'
#######################################
