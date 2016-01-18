# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.abspath('..'))
import taskman


extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'taskman'
copyright = u'2011, Billy Shambrook'
version = taskman.__version__
release = taskman.__version__

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

htmlhelp_basename = 'taskmanpydoc'


latex_documents = [
  ('index', 'taskman.tex', u'Taskman Documentation',
   u'Billy Shambrook', 'manual'),
]


man_pages = [
    ('index', 'taskman', u'Taskman Documentation',
     [u'Billy Shambrook'], 1)
]
