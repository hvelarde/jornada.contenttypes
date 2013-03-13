# -*- coding:utf-8 -*-

from five import grok
from jornada.contenttypes import _
from jornada.contenttypes.controlpanel import IJornadaSettings
from plone.app.textfield import RichText
from plone.dexterity import content
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.component import getUtility

grok.templatedir('templates')


def check_capitalize(value):
    return value == value.capitalize()


class IArticle(form.Schema):
    """An article. Defines a news article.
    """

    subtitle = schema.TextLine(
        title=_(u"Subtitle"),
        description=_(u"Please enter a capitalized sentence."),
        constraint=check_capitalize,
    )

    author = schema.TextLine(
        title=_(u"Author"),
    )

    text = RichText(
        title=_(u"Text"),
    )

    section = schema.Choice(
        title=_(u"Section"),
        vocabulary='jornada.contenttypes.AvailableSections',
    )

    location = schema.TextLine(
        title=_(u"Location"),
    )

    image = NamedBlobImage(
        title=_(u"Image")
    )


@form.default_value(field=IArticle['section'])
def section_default_value(data):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IJornadaSettings)
    return settings.default_section


class Article(content.Item):
    """My class"""


class View(grok.View):
    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('view')
