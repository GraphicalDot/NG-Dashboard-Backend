import logging
from logging.config import fileConfig
import os
from os.path import dirname, abspath
LOG_PATH = dirname(dirname(abspath(__file__)))

dictLogConfig = {
        "version":1,
         'disable_existing_loggers': False,
        "handlers":{
                    "fileHandler":{
                        "class":"logging.FileHandler",
                        "formatter":"myFormatter",
                        "filename":"config2.log"
                        },
                    
         			'console': {
        				'class': 'logging.StreamHandler',
                        'level': 'DEBUG',
                        'formatter': 'detailed',
        				'stream': 'ext://sys.stdout',
    				},
    				'main_file': {
          				'level': 'DEBUG',
         				'class': 'logging.handlers.WatchedFileHandler',
            			'formatter': 'detailed',
            			'filename': os.path.join(LOG_PATH, 'main.log'),
        			},
        			'error_file': {
            			'level': 'ERROR',
            			'class': 'logging.handlers.WatchedFileHandler',
            			'formatter': 'detailed',
            			'filename': os.path.join(LOG_PATH, 'error.log'),
        			},

                    },        
        "loggers":{
            "exampleApp":{
                "handlers":["fileHandler"],
                "level":"INFO",
                },
            "main": {
            	"handlers": ["console", 'main_file', 'error_file'],
            	"propagate": False,
            }
            },
 
        "formatters":{
            "myFormatter":{
                "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
            'detailed': {
      			'format': '%(asctime)s %(module)-17s line:%(lineno)-4d ' \
      				'%(levelname)-8s %(message)s',
    		},
            }
        }





logging.config.dictConfig(dictLogConfig)
logger = logging.getLogger("main")

