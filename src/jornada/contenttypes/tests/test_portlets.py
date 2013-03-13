# -*- coding: utf-8 -*-

from jornada.contenttypes.portlets import articles
from jornada.contenttypes.testing import JORNADA_CONTENTTYPES_INTEGRATION_TESTING
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.GenericSetup.utils import _getDottedName
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class TestArticlesPortlet(unittest.TestCase):

    layer = JORNADA_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='portlets.Articles')
        self.assertEqual(portlet.addview, 'portlets.Articles')

    def test_registered_interfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Articles')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual([
            'plone.app.portlets.interfaces.IColumn',
            'plone.app.portlets.interfaces.IDashboard',
            ], registered_interfaces)

    def test_interfaces(self):
        portlet = articles.Assignment(count=5)
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portlet = getUtility(IPortletType, name='portlets.Articles')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]

        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], articles.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = articles.Assignment(count=5)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, articles.EditForm))

    def test_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = articles.Assignment(count=5)

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, articles.Renderer))


class RendererTestCase(unittest.TestCase):

    layer = JORNADA_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

        # Make sure Articles use simple_publication_workflow
        self.portal.portal_workflow.setChainForPortalTypes(
            ['Article'], ['simple_publication_workflow'])

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or articles.Assignment(count=5)

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_published_articles(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        r = self.renderer()
        self.assertEqual(0, len(r.published_articles()))

        self.folder.invokeFactory('Article', 'a1')
        self.folder.invokeFactory('Article', 'a2')
        r = self.renderer()
        self.assertEqual(0, len(r.published_articles()))

        self.portal.portal_workflow.doActionFor(self.folder.a1, 'publish')
        r = self.renderer()
        self.assertEqual(1, len(r.published_articles()))

        self.portal.portal_workflow.doActionFor(self.folder.a2, 'publish')
        r = self.renderer()
        self.assertEqual(2, len(r.published_articles()))

        self.assertIn('a2', r.published_articles()[0].getPath())
        self.assertIn('a1', r.published_articles()[1].getPath())
