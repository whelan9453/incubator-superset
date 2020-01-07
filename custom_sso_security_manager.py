# This file is for custom OAuth2 configuration of Superset
# Although GitHub is listed as FAB supported providers,
# we still need to fill in the email explicitly to avoid an Superset internal error
# due to the email should an unique key and cannot be duplicated with empty strings
# Ref: https://github.com/apache/incubator-superset/blob/master/docs/installation.rst#custom-oauth2-configuration

import logging
from superset.security import SupersetSecurityManager

class CustomSsoSecurityManager(SupersetSecurityManager):
    # We set up a custom oauth provider for aics "github_aics"
    # and follow the user data format of Superset to return a valid superset user
    # Ref: https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/security/manager.py
    def oauth_user_info(self, provider, response=None):
        logging.debug("Oauth2 provider: {0}.".format(provider))
        if provider == 'github_aics':
            me = self.appbuilder.sm.oauth_remotes[provider].get("user")
            logging.debug("User info from Github_AICS: {0}".format(me.data))
            uname = "github_" + me.data.get("login")
            mail = me.data.get("email") or me.data.get("login") + "@asus.com"
            return {"username": uname, "email": mail}