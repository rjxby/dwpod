dwpod
===================================================================

Simple way to download files from rss feeds.
-------------------------------------------------------------------

Configuration
-------------------------------------------------------------------

Configuration tools are located in the file config.json

 * count_item - The number of scanned item(s) in feed(RSS);
 * dir_name - The folder where the files will be uploaded;
 * type_data - The type of data to be downloaded;
 * urls - Links to feeds(RSS);
 * timeout_check_urls - Interval to check for updates in feeds(RSS) (minutes);
 * timeout_check_files - Interval to cleaning up old files (minutes);
 * delta_stored - Stored time (days)

TODO
--------------------------------------------------------------------
 * work with docker
 * continue download corrupted files
 * unit tests
