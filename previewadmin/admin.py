from django.contrib import admin
from django.contrib.admin.util import flatten_fieldsets, unquote
from django.contrib.admin import helpers
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text


class PreviewAdmin(admin.ModelAdmin):

    preview_info_template = "previewadmin_change_form.html"
    show_help_text = False
    button_label = _(u'View')

    def previewadmin_button(self, obj):
        return u'''
        <div class="preview-container">
            <a href="preview-item/{}" class="preview-item">{}</a>
            <div class="preview-content"></div>
        </div>
        '''.format(obj.pk, self.button_label)

    previewadmin_button.short_description = ''
    previewadmin_button.allow_tags = True

    def __init__(self, model, admin_site):
        super(PreviewAdmin, self).__init__(model, admin_site)
        list_display = self.list_display
        self.list_display = (u'previewadmin_button',) + list_display
        if list_display:
            first_elem = list_display[0]
            if not self.list_display_links:
                self.list_display_links = (first_elem,) + self.list_display_links

    def get_readonly_fields_info(self, request, obj=None):
        if self.declared_fieldsets:
            return flatten_fieldsets(self.declared_fieldsets)
        else:
            return list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
            ))

    def get_urls(self):
        from django.conf.urls import url
        urls = super(PreviewAdmin, self).get_urls()
        my_urls = [
            url(r'^preview-item/(?P<object_id>\d+)$', self.info_view, name='previewadmin_info_view'),
        ]
        return my_urls + urls

    def render_preview(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, form_url)
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,  # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'form_url': form_url,
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
        })

        return TemplateResponse(request, self.preview_info_template or [
            "admin/%s/%s/previewadmin_change_form.html" % (app_label, opts.model_name),
            "admin/%s/previewadmin_change_form.html" % app_label,
            "admin/previewadmin_change_form.html"
        ], context, current_app=self.admin_site.name)

    def info_view(self, request, object_id, form_url='', extra_context=None):
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(opts.verbose_name), 'key': escape(object_id)
            })

        ModelForm = self.get_form(request, obj)
        formsets = []
        inline_instances = self.get_inline_instances(request, obj)

        form = ModelForm(instance=obj)
        prefixes = {}
        for FormSet, inline in zip(self.get_formsets(request, obj), inline_instances):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet(instance=obj, prefix=prefix,
                              queryset=inline.get_queryset(request))
            formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields_info(request, obj),
            model_admin=self)

        media = super(PreviewAdmin, self).media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(set(
                [field.name for field in inline.opts.local_fields] +
                [field.name for field in inline.opts.local_many_to_many]
            ))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_text(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': True,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            'preserved_filters': self.get_preserved_filters(request),
            'show_help_text': self.show_help_text
        }
        context.update(extra_context or {})
        return self.render_preview(request, context, change=True, obj=obj, form_url=form_url)

    class Media:
        js = (u'{}previewadmin/js/previewadmin.js'.format(settings.STATIC_URL),)
        css = {u"all": (u"{}previewadmin/css/previewadmin.css".format(settings.STATIC_URL),)}