jwt_secret = "secret"
port = 3000
host = "0.0.0.0"
username_default = "admin"
password_default = "admin"

collection_types = {
    "server": {
        "host": {},
        "port": {},
    },
    "users": {},
    "devices": {
        "id": {"required": True}
    },
    "device_cates": {},
    "sensors": {},
    "sensor_cates": {},
    "control": {},
    "control_cates": {}
}
