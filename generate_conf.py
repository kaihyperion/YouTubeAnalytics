import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

#ADD SECTION
config_file.add_section("SCOPE Settings")
# ADD SETTINGS TO SECTION

config_file.set("SCOPE Settings", "scopeList","https://www.googleapis.com/auth/yt-analytics.readonly, https://www.googleapis.com/auth/yt-analytics-monetary.readonly, https://www.googleapis.com/auth/youtube, https://www.googleapis.com/auth/youtubepartner")


# YOUTUBE ANALYTICS 2 API SETTINGS
config_file.add_section("YouTube Analytics")

config_file.set("YouTube Analytics",
                "API_SERVICE_NAME",
                "youtubeAnalytics")
config_file.set("YouTube Analytics",
                "API_VERSION",
                "v2")


# YOUTUBE REPORTING V1 API SETTINGS
config_file.add_section("YouTube Reporting")

config_file.set("YouTube Reporting",
                "API_SERVICE_NAME",
                "youtubereporting")
config_file.set("YouTube Reporting",
                "API_VERSION",
                "v1")



# YOUTUBE DATA V3 API SETTINGS
config_file.add_section("YouTube Data")

config_file.set("YouTube Data",
                "API_SERVICE_NAME",
                "youtube")
config_file.set("YouTube Data",
                "API_VERSION",
                "v3")
config_file.set("YouTube Data",
                "API_KEY",
                "AIzaSyC_ICB--wUdpFC-SrOFwp9mdWNZUFF2Rs0")


# SAVE CONFIG FILE
with open(r"conf.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Configuration file 'conf.ini' is created")

# PRINT FILE CONTENT
read_file = open('conf.ini', 'r')
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()