from eagle_eyes.apps.games.models import level_ups, labels
import jwt


class UserService:
    @staticmethod
    def inject_user_id(request):
        try:
            x_token = request.headers.get("X-Token")
            if x_token:
                user_id = jwt.decode(x_token, options={"verify_signature": False})['data']
                return user_id
            x_token = request.headers.get("Authorization")
            x_token = x_token[7:] if "bearer" in x_token[:7].lower() else x_token
            if x_token:
                user_id = jwt.decode(x_token, options={"verify_signature": False})['data']
                return user_id
        except Exception:
            pass


def get_label(current_level: int):
    label = [
        labels[key] for key in labels.keys()
        if current_level in key
    ]
    return label[0]


def get_level_total_plays(current_level: int):
    level_up_threshold = [
        level_ups[key] for key in level_ups.keys()
        if current_level in key
    ]
    return level_up_threshold[0]
