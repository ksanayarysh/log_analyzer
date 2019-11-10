this is a simple log analyzer

usage:
python log_analyzer --conf=config.ini

config.ini has a following structure:
[config]
REPORT_SIZE=100
REPORT_DIR=./report
LOG_DIR=./log


REPORT_DIR is a directory where report will be placed
REPORT_SIZE is a count of lines with max time_sum values that goes in report
LOG_DIR is a directory where logs are stored

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
