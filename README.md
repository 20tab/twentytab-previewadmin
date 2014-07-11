twentytab-previewadmin
======================

A django app that initializes admin changelist view with a useful tool to have a preview of instances

## Installation

Use the following command: <b><i>pip install twentytab-previewadmin</i></b>

## Configuration

- settings.py

```py
INSTALLED_APPS = {
    ...,
    'previewadmin',
    ...
}
```

- Static files

Run collectstatic command or map static directory.


## Usage

```py
from previewadmin.admin import PreviewAdmin


class CommessaAdmin(PreviewAdmin):
    pass
```

or

```py
from previewadmin.admin import PreviewAdmin


class CommessaAdmin(PreviewAdmin):
    show_help_text = True
    button_label = u'<img src="/static/img/info.png" class="info-img" />'
```

