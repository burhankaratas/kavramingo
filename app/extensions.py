from flask_mysqldb import MySQL
from flask_login import LoginManager

mysql = MySQL()
login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = "Bu sayfaya erişmek için giriş yapmalısınız."


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    return User.from_row(row)
