import os
import time
import logging
import watchdog
from watchdog.observers import Observer 
from watchdog.events import PatternMatchingEventHandler

from s3 import S3CameraRecordingsInterface

logging.basicConfig(level=logging.INFO)

class EventHandler(PatternMatchingEventHandler):
    
    def __init__(self, patterns_list, bucket):
        self.__bucket = bucket
        PatternMatchingEventHandler.__init__(
            self, 
            patterns=patterns_list,
            ignore_directories=True,
            case_sensitive=False
        )

    def on_created(self, event):
        logging.debug('Creation Event Handler Hit')
        S3CameraRecordingsInterface().store_recording(event.src_path, self.__bucket)

class S3FileUploader(Observer):
    
    DIR_TO_MONITOR_ENV_KEY = 'DIR_TO_MONITOR'
    PATTERNS_TO_MONITOR_ENV_KEY = 'PATTERNS_TO_MONITOR'
    S3_BUCKET_ENV_KEY = 'S3_BUCKET'

    def __init__(self):
        dir_to_monitor = os.environ.get(self.DIR_TO_MONITOR_ENV_KEY)
        pattern_string = os.environ.get(self.PATTERNS_TO_MONITOR_ENV_KEY)
        bucket = os.environ.get(self.S3_BUCKET_ENV_KEY)

        self.__validate_env_vars(dir_to_monitor, pattern_string, bucket)

        patterns_to_monitor = pattern_string.split(',')

        logging.info(f'Monitoring "{dir_to_monitor}" for changes to files matching the following patterns:"{pattern_string}"' )

        self.__start_monitoring(dir_to_monitor, patterns_to_monitor, bucket)
 

    def __validate_env_vars(self, dir_to_monitor, pattern_string, bucket):
        if dir_to_monitor is None:
            raise EnvironmentError(
                f'Required environment variable "{self.DIR_TO_MONITOR_ENV_KEY}" is not set'
            )

        if not os.path.exists(dir_to_monitor):
            raise ValueError(
                f'Path "{dir_to_monitor}" defined by environment variable "{self.DIR_TO_MONITOR_ENV_KEY}" does not exist'
            )

        if not os.path.isdir(dir_to_monitor):
            raise ValueError(
                f'Path "{dir_to_monitor}" defined by environment variable "{self.DIR_TO_MONITOR_ENV_KEY}" is not a directory'
            )
        
        if pattern_string is None:
            raise EnvironmentError(
                f'Required environment variable "{self.PATTERNS_TO_MONITOR_ENV_KEY}" is not set'
            )
        
        if bucket is None:
            raise EnvironmentError(
                f'Required environment variable "{self.S3_BUCKET_ENV_KEY}" is not set'
            )

    def __start_monitoring(self, directory_to_monitor, patterns_to_monitor, bucket):

        super().__init__()

        self.schedule(
            EventHandler(patterns_to_monitor, bucket),
            path=directory_to_monitor,
            recursive=False
        )
        self.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        self.join()

        

if __name__ == "__main__":
    S3FileUploader()

