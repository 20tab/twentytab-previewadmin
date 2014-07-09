from fabric.api import local, run, cd
from fabric.state import output
import previewadmin


def publish(message):
    v = previewadmin.__version__

    output['everything'] = True
    local("git pull")
    local("git add -A")
    local("git commit -m '%s'" % message)
    local("git push")
    local("git tag {}".format(v))
    local("git push --tags")
    local("python setup.py sdist register")
    local("python setup.py sdist upload")

