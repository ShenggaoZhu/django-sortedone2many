# -*- coding: utf-8 -*-
from itertools import chain
from django import forms
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from sortedm2m.forms import SortedCheckboxSelectMultiple, SortedMultipleChoiceField


class SortedCheckboxSelectMultipleWithDisabled(SortedCheckboxSelectMultiple):
    '''
    Render a list of ``choices`` as checkboxes that can be sorted using drag & drop.
    Some checkboxes are rendered as "disabled" according to the ``disabled_value``.
    '''
    # override render()
    def render(self, name, value, attrs=None, choices=()):
        disabled_value = getattr(self, 'disabled_value', [])
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)

        # Normalize to strings
        str_values = [force_text(v) for v in value]

        selected = []
        unselected = []

        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = ' for="%s"' % conditional_escape(final_attrs['id'])
            else:
                label_for = ''

            # if an item has a category other than the current showing category
            if option_value in disabled_value and option_value not in value:
                extra_attrs = {'disabled': 'disabled'}
            else:
                extra_attrs = {}
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value, attrs=extra_attrs)
            option_label = conditional_escape(force_text(option_label))
            item = {'label_for': label_for, 'rendered_cb': rendered_cb, 'option_label': option_label, 'option_value': option_value}
            if option_value in str_values:
                selected.append(item)
            else:
                unselected.append(item)

        # re-order `selected` array according str_values which is a set of `option_value`s in the order they should be shown on screen
        ordered = []
        for value in str_values:
            for select in selected:
                if value == select['option_value']:
                    ordered.append(select)
        selected = ordered

        html = render_to_string(
            'sortedm2m/sorted_checkbox_select_multiple_widget.html',
            {'selected': selected, 'unselected': unselected})
        return mark_safe(html)


class SortedMultipleChoiceWithDisabledField(SortedMultipleChoiceField):
    '''
    Form field to render a ``SortedOneToManyField`` of a model as a list of 
    ``choices`` or checkboxes that can be sorted using drag & drop.
    
    This form field also adds a special function to the widget:
    disables those checkboxes that should not be directly selected 
    on the current admin view (to ensure the unique ``OneToMany`` relationship).
    
    E.g., on the admin view for ``category 1``, 
    ``item1.category`` is ``category 2``, so the checkbox for ``item1`` is disabled
    because ``category 2`` has to remove ``item1`` from its ``items`` list before
    ``category 1`` can select ``item1`` in the admin view.

    Pass a list of ``disabled_value`` to the widget so that the widget can decide
    whether to render a checkbox as "disabled".
    '''

    widget = SortedCheckboxSelectMultipleWithDisabled

    def __init__(self, related_query_name, *args, **kwargs):
        super(SortedMultipleChoiceWithDisabledField, self).__init__(*args, **kwargs)
        # find all items that have an non-null category
        disabled_value = self.queryset.filter(**{related_query_name + '__isnull':False}
                                                ).values_list('pk', flat=True)
        self.widget.disabled_value = disabled_value

