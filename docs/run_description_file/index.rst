.. Copyright 2013-2018 The Salish Sea MEOPAR contributors
.. and The University of British Columbia
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..    http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


.. _RunDescriptionFileStructure:

******************************
Run Description File Structure
******************************

:program:`nemo` run description files are written in YAML_.
They contain key-value pairs that define the names and locations of files and directories that the :program:`nemo` command processor uses to manage NEMO runs and their results.

.. _YAML: http://pyyaml.org/wiki/PyYAMLDocumentation

Run description files are typically stored in a sub-directory of a version controlled directory tree in which you also store your model configuration elements such as coordinates,
bathymetry,
initial conditions fields,
namelists,
etc.

.. toctree::
   :maxdepth: 3

   3.6_yaml_file
   3.6_agrif_yaml_file
