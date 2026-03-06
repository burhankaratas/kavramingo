from app.modules.auth import auth_bp


@auth_bp.route("/login")
def login():
    pass


@auth_bp.route("/register")
def register():
    pass


@auth_bp.route("/logout")
def logout():
    pass
