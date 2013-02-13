# coding: utf-8
import sublime
from sublime_plugin import WindowCommand

from ..util import noop, create_panel, show_panel, append_view, StatusSpinner
from ..cmd import Cmd


class LegitCmd(Cmd):
    __executable__ = 'legit'
    __bin__ = ['legit']


class LegitWindowCmd(LegitCmd):

    def get_branch_choices(self, filter=('published', 'unpublished')):
        lines = self.legit_lines(['branches'])
        branches, choices = [], []
        for l in lines:
            if not l:
                continue
            current = l[0:2]
            name, pub = l[2:].split(None, 1)
            pub = pub.strip(' \t()')
            if not pub in filter:
                continue
            choices.append(['%s%s' % (current, name.strip()), '  %s' % pub])
            branches.append(name)
        return branches, choices

    def show_branches_panel(self, on_selection, *args, **kwargs):
        branches, choices = self.get_branch_choices(*args, **kwargs)

        def on_done(idx):
            if idx != -1:
                branch = branches[idx]
                on_selection(branch)

        self.window.show_quick_panel(choices, on_done, sublime.MONOSPACE_FONT)

    def run_async_legit_with_panel(self, cmd, progress, panel_name):
        self.panel = create_panel(self.window, panel_name, show=False)
        self.panel_name = panel_name
        self.panel_shown = False

        thread = self.legit_async(cmd, on_data=self.on_data)
        runner = StatusSpinner(thread, progress)
        runner.start()

    def on_data(self, d):
        if not self.panel_shown:
            show_panel(self.window, self.panel_name)
        append_view(self.panel, d)
        self.panel.show(self.panel.size())


class LegitSwitchCommand(WindowCommand, LegitWindowCmd):

    def run(self):
        self.show_branches_panel(self.switch)

    def switch(self, branch):
        out = self.legit_string(['switch', branch])
        create_panel(self.window, 'legit-switch', out)


class LegitSyncCommand(WindowCommand, LegitWindowCmd):

    def run(self, select_branch=False):
        if select_branch:
            self.show_branches_panel(self.sync, filter=('published',))
        else:
            self.sync()

    def sync(self, branch=None):
        if branch:
            progress = "Syncing %s" % branch
        else:
            progress = "Syncing"
        self.run_async_legit_with_panel(['sync', branch], progress, 'legit-sync')


class LegitPublishCommand(WindowCommand, LegitWindowCmd):

    def run(self):
        self.show_branches_panel(self.publish, filter=('unpublished',))

    def publish(self, branch):
        self.run_async_legit_with_panel(['publish', branch], "Publishing %s" % branch, 'legit-publish')


class LegitUnpublishCommand(WindowCommand, LegitWindowCmd):

    def run(self):
        self.show_branches_panel(self.unpublish, filter=('published',))

    def unpublish(self, branch):
        self.run_async_legit_with_panel(['unpublish', branch], "Unpublishing %s" % branch, 'legit-unpublish')


class LegitHarvestCommand(WindowCommand, LegitWindowCmd):

    def run(self, select_branch=False):
        if select_branch:
            self.show_branches_panel(self.harvest)
        else:
            self.harvest()

    def harvest(self, branch=None):
        def on_done(into_branch):
            into_branch = into_branch.strip()
            if into_branch:
                out = self.legit_string(['harvest', branch, into_branch])
                create_panel(self.window, 'legit-harvest', out)

        self.show_branches_panel(on_done)


class LegitSproutCommand(WindowCommand, LegitWindowCmd):

    def run(self, select_branch=False):
        if select_branch:
            self.show_branches_panel(self.sprout)
        else:
            self.sprout()

    def sprout(self, branch=None):
        def on_done(new_branch):
            new_branch = new_branch.strip()
            if new_branch:
                out = self.legit_string(['sprout', branch, new_branch])
                create_panel(self.window, 'legit-sprout', out)

        self.window.show_input_panel('New branch:', '', on_done, noop, noop)


class LegitGraftCommand(WindowCommand, LegitWindowCmd):

    def run(self):
        self.show_branches_panel(self.graft, filter=('unpublished',))

    def graft(self, branch):
        out = self.legit_string(['graft', branch])
        create_panel(self.window, 'legit-graft', out)


class LegitBranchesCommand(WindowCommand, LegitWindowCmd):

    def run(self):
        self.show_branches_panel(noop)