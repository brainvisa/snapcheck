{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}
   :no-members:

{#- The private modules are not documented, except __main__ (the command line programs) -#}
{% set documented_modules = modules | default([]) + (["__main__"] if "__main__" in all_modules | default([]) else []) %}
{% if documented_modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
{% for item in documented_modules %}
   {{ item }}
{%- endfor %}
{% endif %}

{% if classes %}
.. rubric:: Classes

.. autosummary::
   :nosignatures:
{% for item in classes %}
   {{ item }}
{%- endfor %}
{% endif %}

{% if functions %}
.. rubric:: Functions

.. autosummary::
   :nosignatures:
{% for item in functions %}
   {{ item }}
{%- endfor %}
{% endif %}

{% if attributes %}
.. rubric:: Module attributes

{% for item in attributes %}
.. autodata:: {{ item }}
   :no-value:
{% endfor %}
{% endif %}

{% for item in classes %}
{% if fullname ~ "." ~ item in pydantic_models %}
.. autopydantic_model:: {{ item }}
   :no-members:
{% for method in pydantic_models[fullname ~ "." ~ item] %}
   .. automethod:: {{ method }}
{% endfor %}
{% else %}
.. autoclass:: {{ item }}
{% endif %}

.. minigallery:: {{ fullname }}.{{ item }}
   :add-heading: Examples using ``{{ item }}``
   :heading-level: ^

{% endfor %}

{% for item in functions %}
.. autofunction:: {{ item }}

{% endfor %}
