jwt_secret = "secret"
port = 3000
host = "0.0.0.0"
username_default = 'admin'
password_default = 'admin'

type_data = {
    'base': {
        'users': {
            'username': {
                'required': True,
                'unique': True
            },
            'password': {
                'required': True
            }
        }
    },
    'datas': {
        'devices': {
        }
    }
}
