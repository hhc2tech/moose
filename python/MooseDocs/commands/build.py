"""Defines the MooseDocs build command."""
import os
import sys
import multiprocessing
import logging
import subprocess
import shutil

import anytree
import livereload

import mooseutils

import MooseDocs
from MooseDocs import common
from MooseDocs.tree import pages
from check import check

def command_line_options(subparser, parent):
    """
    Define the command line options for the build command.
    """
    parser = subparser.add_parser('build', parents=[parent],
                                  help='Convert markdown into HTML or LaTeX.')

    parser.add_argument('--config', default='config.yml',
                        help="The configuration file.")
    parser.add_argument('--disable', default=[], type=list, nargs='*',
                        help="A list of extensions to disable.")
    parser.add_argument('--destination',
                        default=None,
                        help="Destination for writing build content.")
    parser.add_argument('--serve', action='store_true',
                        help="Create a local live server.")
    parser.add_argument('--dump', action='store_true',
                        help="Show page tree to the screen.")
    parser.add_argument('--grammar', action='store_true',
                        help='Show the lexer components in order.')
    parser.add_argument('--num-threads', '-j', type=int, default=multiprocessing.cpu_count(),
                        help="Specify the number of threads to build pages with.")
    parser.add_argument('--port', default='8000', type=str,
                        help="The host port for live web server (default: %(default)s).")
    parser.add_argument('--host', default='127.0.0.1', type=str,
                        help="The local host for live web server (default: %(default)s).")
    parser.add_argument('--clean', action='store_true',
                        help="Clean the destination directory when the '--files' option is used. "
                             "The destination directory is always cleaned otherwise.")
    parser.add_argument('-f', '--files', default=[], nargs='*',
                        help="A list of file to build, this is useful for testing. The paths " \
                             "should be as complete as necessary to make the name unique, just " \
                             "as done within the markdown itself.")
    parser.add_argument('--home', default=None, help="The 'home' URL for the hosted website. " \
                                                     "This is mainly used by CIVET to allow " \
                                                     "temporary sites to be functional.")

    parser.add_argument('--check', action='store_true',
                        help="Run the default check command prior to build, the main purpose " \
                             "of this command is to allow the make targets to avoid creating " \
                             "the syntax multiple times.")

class MooseDocsWatcher(livereload.watcher.Watcher):
    """
    A livereload watcher for MooseDocs that adds nodes to the directory tree when pages are added.

    Inputs:
        translator[Translator]: Instance of the translator object for converting files.
        options[argparse]: Complete argparse options as passed into the main function.
    """

    def __init__(self, translator, options, *args, **kwargs):
        super(MooseDocsWatcher, self).__init__(*args, **kwargs)
        self._options = options
        self._translator = translator

        for node in anytree.PreOrderIter(self._translator.root):
            self.watch(node.source, self.build, delay=2)

    def build(self):
        func = lambda n: n.source == self.filepath
        nodes = [anytree.search.find(self._translator.root, filter_=func)]
        if nodes[0] and nodes[0].dependencies:
            for node in anytree.PreOrderIter(self._translator.root):
                if node.fullpath in nodes[0].dependencies:
                    nodes.append(node)
            self._translator.execute(num_threads=1, nodes=nodes)

    def execute(self):
        """
        Perform complete build.
        """
        self._translator.execute(self._options.num_threads)


    #def examine(self):
    #    """
    #    Investigate directories for new files and add them to the tree if found.

    #    TODO: Remove nodes if page is deleted.
    #    TODO: Handle !include (see extensions.include.py for more information).
    #    """
    #    for node in anytree.PreOrderIter(self._translator.root):

    #        # Only perform check on valid directories
    #        if not isinstance(node, pages.DirectoryNode) or not os.path.exists(node.source):
    #            continue

    #        # Build map of child pages for the directory
    #        children = {child.name:child for child in node.children \
    #                    if isinstance(child, pages.FileNode)}

    #        # Compare the list of files in the directory with those tracked by MooseDocs
    #        for filename in os.listdir(node.source):  #pylint: disable=no-member
    #            if filename.endswith(MooseDocs.FILE_EXT) and not filename.startswith('.'):
    #                if filename not in children:
    #                    source = os.path.join(node.source, filename)
    #                    if filename.endswith('.md'):
    #                        new = pages.MarkdownNode(node, source=source)
    #                    else:
    #                        new = pages.FileNode(node, source=source) #pylint: disable=redefined-variable-type
    #                    new.base = self._options.destination
    #                    self.watch(new.source, new.build, delay=2) #pylint: disable=no-member
    #                    new.init(self._translator)
    #                    new.build()

    #    return super(MooseDocsWatcher, self).examine()

def _init_large_media():
    """Check submodule for large_media."""
    log = logging.getLogger('MooseDocs._init_large_media')
    status = common.submodule_status()
    large_media = os.path.realpath(os.path.join(MooseDocs.MOOSE_DIR, 'large_media'))
    for submodule, status in status.iteritems():
        if ((os.path.realpath(os.path.join(MooseDocs.MOOSE_DIR, submodule)) == large_media)
                and (status == '-')):
            log.info("Initializing the 'large_media' submodule for storing images above 1MB.")
            subprocess.call(['git', 'submodule', 'update', '--init', 'large_media'],
                            cwd=MooseDocs.MOOSE_DIR)

def main(options):
    """
    Main function for the build command.

    Inputs:
        options[argparse options]: Complete options from argparse, see MooseDocs/main.py
    """

    # Make sure "large_media" exists in MOOSE
    _init_large_media()

    # Create translator
    translator, _ = common.load_config(options.config)
    if options.destination:
        translator.update(destination=mooseutils.eval_path(options.destination))
    translator.init()

    for obj in translator._Translator__content.values():
        print obj

    # Disable extensions based on command line arguments
    for ext in translator.extensions:
        if ext._name in options.disable:
            ext.setActive(False)

    # Replace "home" with local server
    if options.serve:
        home = 'http://127.0.0.1:{}'.format(options.port)
        translator.renderer.update(home=home)
    elif options.home:
        translator.renderer.update(home=options.home)

    # Dump page tree
    if options.dump:
        print translator.root
        sys.exit()

    # Clean when --files is NOT used or when --clean is used with --files.
    if ((options.files == []) or (options.files != [] and options.clean)) \
       and os.path.exists(translator['destination']):
        log = logging.getLogger('MooseDocs.build')
        log.info("Cleaning destination %s", translator['destination'])
        shutil.rmtree(translator['destination'])

    # Perform check
    if options.check:
        check(translator)

    # Perform build
    if options.files:
        nodes = []
        for filename in options.files:
            nodes += common.find_pages(translator.root, filename)
        translator.execute(options.num_threads, nodes)
    else:
        translator.execute(options.num_threads)
        #gmooseutils.run_profile(translator.execute, options.num_threads)

    if options.serve:
        watcher = MooseDocsWatcher(translator, options)
        server = livereload.Server(watcher=watcher)
        server.serve(root=translator['destination'], host=options.host, port=options.port)
