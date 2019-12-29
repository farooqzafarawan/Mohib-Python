#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Use global -simulate option for test purposes. No changes to live wiki will be done.
The following parameters are supported:
&params;
-always           The bot won't ask for confirmation when putting a page
-text:            Use this text to be added; otherwise 'Test' is used
-replace:         Dont add text but replace it
-top              Place additional text on top of the page
-summary:         Set the action summary message for the edit.
"""

from __future__ import absolute_import, division, unicode_literals

import pywikibot
import sys
import mwparserfromhell as mwp
from scripts import noreferences
from scripts import reflinks
from pywikibot import pagegenerators

from pywikibot.bot import (
    SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
from pywikibot.tools import issue_deprecation_warning

# This is required for the text that is shown when you run this script with the parameter -help.
#docuReplacements = { '&params;': pagegenerators.parameterHelp }


class CopyRefLinksBot(
    # Refer pywikobot.bot for generic bot classes
    SingleSiteBot,  # A bot only working on one site
    ExistingPageBot,  # CurrentPageBot which only treats existing pages
    NoRedirectPageBot,  # CurrentPageBot which only treats non-redirects
    AutomaticTWSummaryBot,  # Automatically defines summary; needs summary_key
):
    """
    @ivar summary_key: Edit summary message key.Use summary_key to set default edit summary message.
    @type summary_key: str
    """
    summary_key = 'basic-changing'

    def __init__(self, generator, **kwargs):
        """
        @param generator: the page generator that determines on which pages to work
        @type generator: generator
        """

        # call initializer of the super class
        super(CopyRefLinksBot, self).__init__(site=True, **kwargs)

        # assign the generator to the bot
        self.generator = generator

        # Extracting sfn templates and converting them in REF tags
        self.sfnlist = []
        self.sfn = ('sfn', '<sfn>', '</sfn>', 'sfnp', '<sfnp>', '</sfnp>', 'r')

        # define the edit summary
        self.summary = u'خودکار: اندراج حوالہ جات'  # bot summary

    def refTagForming(self, wikicode):
        i = 1
        reftags = {}

        # Surrounding sfn templates with tags
        for template in wikicode.filter_templates():
            if template.name in sfn:
                if template.name == 'sfn':
                    if template not in sfnlist:
                        self.sfnlist.append(template)
                    templ_rep = sfn[1] + str(template) + sfn[2]
                elif template.name == 'r':  # Handling new case of 'r' tag
                    templ_rep = '<r>' + str(template) + '</r>'
                else:
                    templ_rep = sfn[4] + str(template) + sfn[5]
                wikicode.replace(template, templ_rep)

        # alltags = wikicode.filter_tags()
        # Creating Dictionary of References, ref num as key and  vales (reference name and link  as tuple)
        for tag in wikicode.filter_tags():
            if tag.tag in ('ref', 'sfn', 'sfnp', 'r'):

                if tag.tag in self.sfn:
                    refval = tag.tag
                elif tag.attributes == []:  # check if attributes list is empty
                    refval = 'NoRefName'
                else:
                    name = tag.attributes[0]
                    refval = name.value

                if tag.contents is None:
                    pass
                else:
                    # creating list of second element in each tuple in dictionary reftags
                    # ('sfn', '{{sfn|Jhaveri|2001|pp=149}}')
                    secValTuple = [tup[1] for tup in reftags.values()]
                    if tag.contents not in secValTuple:
                        reftags[i] = (refval, tag.contents)
                        i += 1

        return reftags

    def treat_page(self):
        """Load the given page, do some changes, and save it."""
        # let's define some basic variables
        urtext = self.current_page.text
        urtitle = self.current_page.title()

        #eng_site = pywikibot.Site('en')
        #eng_title = ''

        interDict = {}
        try:
            site = pywikibot.Site('ur', 'wikipedia')
            urpage = pywikibot.Page(site, urtitle)

            langlst = urpage.iterlanglinks()

            for i in langlst:
                lang = str(i.site).split(':')[1]
                interDict[lang] = i.title
                if lang == 'en':
                    break

            # If there is no inter-wiki page then exit the program
            if len(interDict) == 0:
                print('Link Dictionary is empty')
                sys.exit()

            eng_title = interDict['en']
        except:
            pywikibot.output(
                u'\03{lightred}Unable to fetch interwiki links!\03{default}')
            return False

        site = pywikibot.Site('en', 'wikipedia')
        enpage = pywikibot.Page(site, eng_title)

        wikitext = enpage.get()
        wikicode = mwp.parse(wikitext)

        # Forming reference if tag value is either ref,sfn,sfnp
        reftags = self.refTagForming(wikicode)

        dlinks = {}
        for k, v in reftags.items():
            dkey = 'و' + str(k) + 'و'
            if v[0] in sfn:
                dlinks[dkey] = str(v[1])
            else:
                dlinks[dkey] = '<ref>' + str(v[1]) + '</ref>'

        urtext = urpage.text
        for r in tuple(dlinks.items()):
            urtext = urtext.replace(*r)

        # Removing Duplicate references by using named reference(first instance) and
        # then only using named reference without content
        deDupRef = reflinks.DuplicateReferences(site)
        urtext = deDupRef.process(urtext)
        
        #write_output(urtext, 'AfterdeDuplicate.txt')

        # Used noreferences to add Reference List in Article
        norefbot = noreferences.NoReferencesBot(None)
        if norefbot.lacksReferences(urtext):
            urpage.text = norefbot.addReferences(urtext)
        else:
            urpage.text = urtext + '\n'

        # save the page
        urpage.save(summary=self.summary, minor=False)
        #self.put_current(urpage.text, summary=self.summary)


def main(*args):
    """
    Process command line arguments and invoke bot.
    If args is an empty list, sys.argv is used.
    @param args: command line arguments
    @type args: unicode
    """

    options = {}
    # Process global arguments to determine desired site
    local_args = pywikibot.handle_args(args)

    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages to work on.
    genFactory = pagegenerators.GeneratorFactory()

    for arg in local_args:

        # Catch the pagegenerators options
        if genFactory.handleArg(arg):
            continue  # nothing to do here

        # Now pick up your own options
        arg, sep, value = arg.partition(':')
        option = arg[1:]
        if option in ('summary', 'page'):
            if not value:
                pywikibot.input('Please enter a value for ' + arg)
            options[option] = value
        # take the remaining options as booleans.
        # You will get a hint if they aren't pre-definded in your bot class
        else:
            options[option] = True

    # The preloading option is responsible for downloading multiple pages from the wiki simultaneously.
    gen = genFactory.getCombinedGenerator(preload=True)
    if gen:
        # pass generator and private options to the bot
        bot = CopyRefLinksBot(gen, **options)
        bot.run()  # guess what it does
        return True
    else:
        pywikibot.bot.suggest_help(missing_generator=True)
        return False


if __name__ == '__main__':
    main()

