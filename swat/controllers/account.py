#
# Account Management Controller file for SWAT
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#   
# You should have received a copy of the GNU General Public License
# 
import logging

from formencode import variabledecode
from pylons import request, tmpl_context as c, url
from pylons.controllers.util import redirect, url_for

from swat.lib.base import BaseController, render
from swat.lib.samr_manager import SAMPipeManager, User, Group

from pylons.i18n.translation import _

from swat.lib.helpers import ControllerConfiguration, DashboardConfiguration, \
BreadcrumbTrail, SwatMessages, ParamConfiguration, filter_list

from pylons.templating import render_mako_def

from samba import param

log = logging.getLogger(__name__)

class AccountController(BaseController):
    """ Account Management Controller """
    def __init__(self):
        """ Initialization """
        me = request.environ['pylons.routes_dict']['controller']
        action = request.environ['pylons.routes_dict']['action']
        
        log.debug("Controller: " + me)
        log.debug("Action: " + action)
        
        if(request.environ['pylons.routes_dict'].has_key("subaction")):
            action = request.environ['pylons.routes_dict']['subaction'] + action
        
        c.config = ControllerConfiguration(me, action)
        
        c.breadcrumb = BreadcrumbTrail(c.config)
        c.breadcrumb.build()
            
        c.samba_lp = param.LoadParm()
        c.samba_lp.load_default()
        
        self.__manager = SAMPipeManager(c.samba_lp)
        
        domains = self.__manager.fetch_and_get_domain_names()
        self.__manager.set_current_domain(0)
        self.__manager.fetch_users_and_groups()
        
        # FIXME just so that options may work
        c.current_page = int(request.params.get("page", 1))
        c.per_page =  int(request.params.get("per_page", 10))
        c.filter_name = request.params.get("filter_value", "")
        c.filter_status = int(request.params.get("filter_status", -1))
        
    def index(self):
        c.user_list = self.__manager.user_list
        c.group_list = self.__manager.group_list
        
        c.list_users = True
        c.list_groups = True
        
        return render('/default/derived/account-dashboard.mako')
    
    def user(self, subaction="index", id=-1):
        id = int(id)        
        user_manager = UserManager(self.__manager)
        template = "/default/derived/account.mako"
        is_new = False
        
        c.user_list = self.__manager.user_list
        c.list_users = True
        c.list_groups = False
        
        if len(c.filter_name) > 0:
            c.user_list = self.__filter_users(c.user_list, c.filter_name)
        
        if c.filter_status != -1:
            if c.filter_status == 1:
                c.user_list = self.__manager.filter_enabled_disabled(True)
            elif c.filter_status == 0:
                c.user_list = self.__manager.filter_enabled_disabled(False)
                
        
        if id == -1:
            is_new = True

        ##
        ## Edit a User
        ##
        if subaction == "edit" or subaction == "add":
            c.p = ParamConfiguration('user-account-parameters')
            c.user = user_manager.edit(id, is_new)

            if c.user is not None:
                template = "/default/derived/edit-user-account.mako"
            else:
                type = "critical"
                cause = _("Unkown Reason")
                
                if group_manager.has_message():
                    cause = group_manager.get_message()
                
                message = _("Unable to get User to edit - %s" % (cause))
                SwatMessages.add(message, type)
        ##
        ## Save the changes made to a User
        ##
        elif subaction == "save" or subaction == "apply":
            (new_id, saved) = user_manager.save(id, is_new)
            
            if saved:
                type = "cool"
                message = _("Sucessfuly saved the User with the ID %s" % (new_id))
            else:
                type = "critical"
                cause = _("Unkown Reason")
                
                if user_manager.has_message():
                    cause = user_manager.get_message()
                
                message = _("Error saving the User with the ID %s: %s" % (new_id, cause))
                
            SwatMessages.add(message, type)
            
            if subaction == "save_add":
                redirect(url_for("with_subaction", controller='account', action="user", subaction="add"))
            elif subaction == "save":
                redirect(url(controller='account', action='user'))
            elif subaction == "apply":
                redirect(url("account_action", action='user', subaction='edit', id=new_id))
            
        ## 
        ## Remove a Certain User or a List of Users
        ## 
        elif subaction == "remove":
            list_uid = variabledecode.variable_decode(request.params).get("uid", id)
            ok_list = []
            
            if not isinstance(list_uid, list):
                list_uid = [list_uid]

            for uid in list_uid:
                uid = int(uid)
                removed = user_manager.remove(uid)

                if removed:
                    ok_list.append(uid)
                    log.info("Deleted " + str(uid) + " :: success: " + str(removed))
                else:
                    SwatMessages.add(user_manager.get_message(), "critical")
                    
            if len(ok_list) > 0:
                joined = ", ".join(["%d" % v for v in ok_list])
                
                if len(ok_list) == 1:
                    message = _("The User with the ID %s was deleted sucessfuly" \
                                % (joined))
                else:    
                    message = _("The Users IDs [%s] were deleted sucessfuly" \
                                % (joined))
                
                SwatMessages.add(message)
                
            redirect(url(controller='account', action='user'))
            
        ##
        ## Disable a User or a List of Users
        ##
        elif subaction == "toggle":
            list_uid = variabledecode.variable_decode(request.params).get("uid", id)
            enabled_list = []
            disabled_list = []
            
            if not isinstance(list_uid, list):
                list_uid = [list_uid]
                
            for uid in list_uid:
                uid = int(uid)
                (toggled, new_status) = user_manager.toggle(uid)

                if toggled:
                    if new_status == True:
                        disabled_list.append(uid)
                    else:
                        enabled_list.append(uid)
                else:
                    SwatMessages.add(_("Error toggling User ID %d: %s" % (uid, user_manager.get_message())), "critical")
                
            if len(enabled_list) > 0:
                joined = ", ".join(["%d" % v for v in enabled_list]) 
                message = _("The following User IDs [%s] were ENABLED successfuly" % (joined))
                SwatMessages.add(message)
                
            if len(disabled_list) > 0:
                joined = ", ".join(["%d" % v for v in disabled_list]) 
                message = _("The following User IDs [%s] were DISABLED successfuly" % (joined))
                SwatMessages.add(message)
                
            redirect(url(controller='account', action='user'))

        return render(template)
    
    def group(self, subaction="index", id=-1):
        id = int(id)        
        group_manager = GroupManager(self.__manager)
        template = '/default/derived/account.mako'
        is_new = False
        
        c.group_list = self.__manager.group_list
        c.list_users = False
        c.list_groups = True
        
        if len(c.filter_name) > 0:
            c.group_list = self.__filter_groups(c.group_list, c.filter_name)
        
        if id == -1:
            is_new = True
        
        ##
        ## Edit a Group
        ##
        if subaction == "edit" or subaction == "add":
            c.p = ParamConfiguration('group-parameters')
            c.group = group_manager.edit(id, is_new)

            if c.group is not None:
                c.user_group_list = self.__manager.get_users_in_group(id)
                template = "/default/derived/edit-group.mako"
            else:
                type = "critical"
                cause = _("Unkown Reason")
                
                if group_manager.has_message():
                    cause = group_manager.get_message()
                    
                message = _("Unable to get Group to edit - %s" % (cause))
                SwatMessages.add(message, type)

        ##
        ## Save the changes made to a Group
        ##
        elif subaction == "save" or subaction == "apply" or subaction == "save_add":
            (new_id, saved) = group_manager.save(id, is_new)
            
            if saved:
                type = "cool"
                message = _("Sucessfuly saved the Group with the ID %s" % (id))
            else:
                type = "critical"
                cause = _("Unkown Reason")
                
                if group_manager.has_message():
                    cause = group_manager.get_message()
                
                message = _("Error saving the Group with the ID %s: %s" % (id, cause))
                
            SwatMessages.add(message, type)
            
            if subaction == "save_add":
                redirect(url_for("with_subaction", controller='account', action="group", subaction="add"))
            elif subaction == "save":
                redirect(url(controller='account', action='group'))
            elif subaction == "apply":
                redirect(url("account_action", action='group', subaction='edit', id=new_id))
            
        ## 
        ## Remove a Certain Group
        ## 
        elif subaction == "remove":
            removed = group_manager.remove(id)
            
            if removed:
                type = "cool"
                message = _("Sucessfuly deleted the Group with the ID %s" % (id))
            else:
                type = "critical"
                cause = _("Unkown Reason")
                
                if group_manager.has_message():
                    cause = group_manager.get_message()
                
                message = _("Error deleting the Group with the ID %s - %s" % (id, cause))
                
            SwatMessages.add(message, type)
            redirect(url(controller='account', action='user'))

        return render(template)
        
    def save(self):
        """ """
        id = request.params.get("id", -1)
        
        action = request.environ['pylons.routes_dict']['action']
        task = request.params.get("task", "").strip().lower()
        type = request.params.get("type", "").strip().lower()

        if type == "user":
            self.user(action, id)
        elif type == "group":
            self.group(action, id)
    
    def apply(self):
        """ """
        self.save()
        
    def save_add(self):
        self.save()

    def cancel(self):
        """ """
        type = request.params.get("type", "").strip().lower()
        
        message = _("Editing canceled. No changes were saved.")
        SwatMessages.add(message, "warning")
        
        redirect(url(controller='account', action=type))
        
    def show_groups(self):
        """ """
        already_selected = request.params.get('as', '')
        log.debug("These are selected: " + already_selected)
        
        if len(already_selected) > 0:
            already_selected = already_selected.split(',')
        
        return render_mako_def('/default/component/popups.mako', \
                               'group_list', \
                               already_selected=already_selected)
        
    def __filter_groups(self, items, regex='.*'):
        """ TODO Must Improve """
        import re
        temp = []
        
        for item in items:
            if re.search(regex, item.name, re.IGNORECASE) is not None:
                temp.append(item)
                
        return temp
    
    def __filter_users(self, items, regex='.*'):
        """ TODO Must Improve """
        import re
        temp = []
        
        for item in items:
            if re.search(regex, item.username, re.IGNORECASE) is not None:
                temp.append(item)
                
        return temp

class UserManager(object):
    """ Manager CRUD Operations for User Accounts """
    def __init__(self, manager):
        """ Class Constructor
        
        Keyword arguments
        manager -- A SAMPipeManager Instance with a valid connection to Samba
        
        """
        self.__manager = manager
        self.__message = ""
        
    def edit(self, id, is_new):
        """ Gets a User for editing. If we are adding a new User an empty
        User object will be returned
        
        Keyword arguments:
        id -- The ID of the User we are editing
        is_new -- Indicated if the User we are editing is new (actually means
        we are adding one) or not
        
        Returns:
        A User Object or None if there is an error
        
        """
        user = None

        try:
            if not is_new:
                if not self.__manager.user_exists(id):
                    raise RuntimeError(-1, _("User does not exist in the Database"))
                    
                user = self.__manager.fetch_user(id)
            else:
                user = User("", "", "", -1)
        except RuntimeError as message:
            log.debug(message)
            self.__set_message(message)
            
        return user
    
    def remove(self, id):
        """ Removes a User with a certain ID from the User Database
        
        Keyword arguments:
        id -- The ID of the User to remove
        
        Returns:
        Boolean indicating if the operation suceeded or not
        
        """
        removed = False
        
        try:
            if not self.__manager.user_exists(id):
                raise RuntimeError(-1, _("User does not exist in the Database"))
                    
            self.__manager.delete_user(User("", "", "", id))
            removed = True
        except RuntimeError as message:
            log.debug(message)
            self.__set_message(message)
        
        return removed
    
    def toggle(self, id):
        """ """
        toggled = False
        
        try:
            if not self.__manager.user_exists(id):
                raise RuntimeError(-1, _("User does not exist in the Database"))
            
            toggled = self.__manager.toggle_user(id)
        except RuntimeError as message:
            log.debug(message)
            self.__set_message(message)
        
        return toggled

    def save(self, id, is_new):
        """ Saves User Information to the Database
        
        Keyword arguments:
        id -- If the User already exists this will be his ID
        is_new -- Indicates if we are the user we are adding if new or not
        
        Returns:
        Boolean indicating if the operation suceeded or not
        
        """
        saved = False
        
        try:
            ##
            ## Basic
            ##
            username = request.params.get("account_username", "")
            fullname = request.params.get("account_fullname", "")
            description = request.params.get("account_description", "")
            
            password = request.params.get("account_password", "")
            confirm_password = request.params.get("confirm_password", "")
            
            if len(password) > 0 and password != confirm_password:
                raise RuntimeError(-1, _("Passwords do not match"))
            
            user = User(username, fullname, description, id)
            
            ##
            ## Account Status
            ## FIXME too complicated
            ##
            user.must_change_password = request.params.get("account_must_change_password", "no")
            if user.must_change_password == "yes":
                user.must_change_password = True
            else:
                user.must_change_password = False
                
            user.cannot_change_password = request.params.get("account_cannot_change_password", "no")
            if user.cannot_change_password == "yes":
                user.cannot_change_password = True
            else:
                user.cannot_change_password = False
        
            user.password_never_expires = request.params.get("account_password_never_expires", "no")
            if user.password_never_expires == "yes":
                user.password_never_expires = True
            else:
                user.password_never_expires = False
            
            user.account_disabled = request.params.get("account_account_disabled", "no")
            if user.account_disabled == "yes":
                user.account_disabled = True
            else:
                user.account_disabled = False
            
            user.account_locked_out = request.params.get("account_account_locked_out", "no")
            if user.account_locked_out == "yes":
                user.account_locked_out = True
            else:
                user.account_locked_out = False
                
            ##
            ## Profile
            ##
            user.profile_path = request.params.get("account_profile_path", "")
            user.logon_script = request.params.get("account_logon_script", "")
            user.homedir_path = request.params.get("account_homedir_path", "")
            user.map_homedir_drive = int(request.params.get("account_map_homedir_drive", ""))
            
            ##
            ## Groups
            ##
            user.group_list = []
            for g in request.params.get("account_group_list", "").split(","):
                for gg in self.__manager.group_list:
                    if gg.name == g.strip():
                        user.group_list.append(gg)
            
            if is_new:
                self.__manager.add_user(user)
                id = user.rid
            else:
                if not self.__manager.user_exists(id):
                    raise RuntimeError(-1, _("User does not exist in the Database"))
                    
                self.__manager.update_user(user)
            
            saved = True
        except RuntimeError as message:
            log.debug(message)
            self.__set_message(message)
        except TypeError, message:
            log.debug(message)
            self.__set_message((-1, message))
 
        return (id, saved)
    
    def get_message(self):
        """ Gets the Status Message set by this Class """
        return self.__message
    
    def __set_message(self, message):
        """ Sets the Status Message for this Class """
        self.__message = str(message[1])
        
    def has_message(self):
        """ Checks if there is a Status Message to show to the User """
        if len(self.__message) > 0:
            return True
        return False

class GroupManager(object):
    def __init__(self, manager):
        """ Class Constructor
        
        Keyword arguments
        manager -- A SAMPipeManager Instance with a valid connection to Samba
        
        """
        self.__manager = manager
        self.__message = ""

    def edit(self, id, is_new):
        """ Gets a Group for editing. If we are adding a new Group an empty
        Group object will be returned
        
        Keyword arguments:
        id -- The ID of the Group we are editing
        is_new -- Indicated if the Group we are editing is new (actually means
        we are adding one) or not
        
        Returns:
        A Group Object or None if there is an error
        
        """
        group = None

        try:
            if not is_new:
                if not self.__manager.group_exists(id):
                    raise RuntimeError(-1, _("Group does not exist in the Database"))
                
                group = self.__manager.fetch_group(id)
            else:
                group = Group("", "", -1)
        except RuntimeError as message:
            log.debug(message)
            self.__set_message(message)
            
        return group
    
    def remove(self, id):
        """ Removes a Group with a certain ID from the Group Database
        
        Keyword arguments:
        id -- The ID of the Group to remove
        
        Returns:
        Boolean indicating if the operation suceeded or not
        
        """
        removed = False
        
        try:
            if not self.__manager.group_exists(id):
                raise RuntimeError(-1, _("Group does not exist in the Database"))

            self.__manager.delete_group(Group("", "", id))
            removed = True
        except RuntimeError as message:
            log.debug(message)
            self.__set_message(message)
        
        return removed
    
    def save(self, id, is_new):
        """ Saves Group Information to the Database
        
        Keyword arguments:
        id -- If the Group already exists this will be its ID
        is_new -- Indicates if we are the Group we are adding if new or not
        
        Returns:
        Boolean indicating if the operation suceeded or not
        
        """
        saved = False
        
        name = request.params.get("group_name", "")
        description = request.params.get("group_description", "")

        try:
            group = Group(name, description, id)
            
            if is_new:
                self.__manager.add_group(group)
                id = group.rid
            else:
                if not self.__manager.group_exists(id):
                    raise RuntimeError(-1, _("Group does not exist in the Database"))

                self.__manager.update_group(group)
                
            saved = True
        except RuntimeError as message:
            log.debug(message)
            self.__set_message(message)
            
        return (id, saved)

    """ Manager CRUD Operations for Groups """
    def get_message(self):
        """ Gets the Status Message set by this Class """
        return self.__message
    
    def __set_message(self, message):
        """ Sets the Status Message for this Class """
        self.__message = str(message[1])
        
    def has_message(self):
        """ Checks if there is a Status Message to show to the User """
        if len(self.__message) > 0:
            return True
        return False
