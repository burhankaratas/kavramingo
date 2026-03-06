from app.modules.quiz import quiz_bp


@quiz_bp.route("/multiple-choice")
def multiple_choice():
    pass


@quiz_bp.route("/matching")
def matching():
    pass


@quiz_bp.route("/flashcard")
def flashcard():
    pass


@quiz_bp.route("/fill-blank")
def fill_blank():
    pass
