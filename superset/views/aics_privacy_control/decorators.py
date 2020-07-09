import functools
import logging

from flask import request, g
from flask_appbuilder.security.sqla import models as ab_models

from superset import db, security_manager
from superset.models.user_attributes import UserAttribute
from superset.views.base import json_error_response, get_user_roles

def aics_access_key_verification(require_admin=False):
    def _decorator(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            req_json = request.get_json()
            access_key: str = req_json.get("access_key")

            session = db.session()
            user_id: int = session.query(UserAttribute.user_id).filter_by(access_key=access_key).first()

            if not user_id:
                err_msg = f"Invalid access_key: {str(access_key)}"
                logging.warning(err_msg)
                extra_info = {'err_msg': f'{err_msg}, request: {str(req_json)}'}

                return json_error_response(err_msg), extra_info

            user_id = user_id[0]
            extra_info = {'user_id': user_id}
            g.user = security_manager.get_user_by_id(user_id)

            if g.user.active == 0:
                err_msg = f"Invalid user: {g.user}(id: {user_id}) is inactive"
                logging.warning(err_msg)
                extra_info = {'err_msg': f'{err_msg}, request: {str(req_json)}'}

                return json_error_response(err_msg), extra_info

            if require_admin:
                Role = ab_models.Role
                admin_role = session.query(Role).filter(Role.name == "Admin").one_or_none()
                if not admin_role in get_user_roles():
                    err_msg = f"Permission denied: {g.user}(id: {user_id}) is not Admin"
                    logging.warning(err_msg)
                    extra_info = {'err_msg': f'{err_msg}, request: {str(req_json)}'}

                    return json_error_response(err_msg), extra_info

            return func(*args, **kwargs)

        return wrap
    return _decorator