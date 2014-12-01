import datetime
from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from plone.app.contentrules.actions.move import IMoveAction
from plone.app.contentrules.actions.move import MoveActionExecutor

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

class IOrganizeAction(Interface):
    """
    """


class OrganizeAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IOrganizeAction, IMoveAction, IRuleElementData)

    element = 'uwosh.intranet.policy.actions.Organize'

    def get_target_folder(self):
        if hasattr(self, '_target_folder'):
            return self._target_folder
        else:
            return ''
            
    def set_target_folder(self, folder):
        self._target_folder = folder
        
    target_folder = property(get_target_folder, set_target_folder)

    @property
    def summary(self):
        return u"Organize added content."


class OrganizeActionExecutor(MoveActionExecutor):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IOrganizeAction, Interface)

    def __init__(self, context, element, event):
        super(OrganizeActionExecutor, self).__init__(context, element, event)
        self.portal_state = getMultiAdapter((self.context, self.context.REQUEST), 
                                        name=u'plone_portal_state')
        here = self.portal_state.portal()
        base = self.base_folder
        
        if base not in here.objectIds():
            self._invokeFactory(here, base)
            
        here = here[base]
        
        container = self.type_folder
        if container not in here.objectIds():
            self._invokeFactory(here, container)
        
        here = here[container]
            
        element.target_folder = '/'.join(here.getPhysicalPath())
        
    def _invokeFactory(self, context, id):
        pt = getToolByName(context, 'portal_types')
        type_info = pt.getTypeInfo("Folder")
        ob = type_info._constructInstance(context, id)
        ob.setTitle(id)
        return ob
        
    @property
    def base_folder(self):
        """
        The value this will return will try in this order
        1. primary user group(set in personal prefs)
        2. first found user group
        3. username
        """
        member = self.portal_state.member()
        pg = member.get('primary_group', None)
        if pg:
            return pg

        groups = member.getGroups()
        if len(groups) > 0:
            return groups[0]
            
        return member.getId()
        
    @property
    def type_folder(self):
        return self.event.object.portal_type + 's'

class OrganizeAddForm(AddForm):
    """An add form for move-to-folder actions.
    """
    form_fields = form.FormFields(IOrganizeAction)
    label = u"Add Organize Action"
    description = u"A move action can organize objects in your site."
    form_name = u"Configure element"

    def create(self, data):
        a = OrganizeAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class OrganizeEditForm(EditForm):
    """An edit form for move rule actions.
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IOrganizeAction)
    label = u"Edit Organize Action"
    description = u"A move action can organize objects in your site."
    form_name = u"Configure element"