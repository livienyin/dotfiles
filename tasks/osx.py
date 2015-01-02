import os

from invoke import ctask

from . import util


@ctask(default=True)
def setup(ctx):
    cl_tools(ctx)
    brew(ctx)
    cider(ctx)
    access_for_assistive_devices(ctx)
    hyper(ctx)
    locate(ctx)
    set_path_for_launchd(ctx)
    rvm(ctx)
    fonts(ctx)
    fix_pip(ctx)
    fix_htop(ctx)
    setup_dbus(ctx)


@ctask
def macvim(ctx):
    macvim_install = (
        "macvim --override-system-vim --custom-system-icons "
        "--with-features=huge --enable-rubyinterp --enable-pythoninterp "
        "--enable-perlinterp --enable-cscope"
    )
    ctx.run("brew install {0}".format(macvim_install))
    ctx.run("vim +BundleInstall! +q +q")

@ctask
def setup_dbus(ctx):
    ctx.run("ln -sfv /usr/local/opt/d-bus/*.plist ~/Library/LaunchAgents")

@ctask
def osx_config(ctx):
    ctx.run('sudo {0}'.format(
        os.path.join(util.RESOURCES_DIRECTORY, 'osx.sh')
    ), pty=True)


@ctask
def cider(ctx):
    ctx.run('brew install caskroom/cask/brew-cask')
    if not util.command_exists('cider'):
        ctx.run('sudo pip install cider')
    ctx.run('cider restore -i')


@ctask
def brew(ctx):
    path = 'https://raw.githubusercontent.com/Homebrew/install/master/install)'
    if not util.command_exists('brew'):
        ctx.run('ruby -e "$(curl -fsSL {0}'.format(path))


@ctask
def packages(ctx):
    ctx.run('brew update')
    for package_name in ESSENTIAL + BASICS + SHOULD_INSTALL + MISC:
        ctx.run('brew install {0}'.format(package_name))


@ctask
def set_path_for_launchd(ctx):
    launch_agent_dir = os.path.expanduser('~/Library/LaunchAgents/')
    filename = 'set-path.plist'
    source = os.path.join(util.RESOURCES_DIRECTORY, filename)
    destination = os.path.join(launch_agent_dir, filename)

    if os.path.exists(source) and not os.path.exists(destination):
        util.ensure_path_exists(launch_agent_dir)
        ctx.run('ln -s {0} {1}'.format(source, destination))


APPS_NEEDING_ASSISTIVE_DEVICE_ACCESS = ('Slate', 'Synergy', 'iTerm')
@ctask
def access_for_assistive_devices(ctx):
    for app in APPS_NEEDING_ASSISTIVE_DEVICE_ACCESS:
        app_string = '/Applications/{0}.app'.format(app)
        user_application = os.path.expanduser('~' + app_string)
        access_if_exists(ctx, user_application)
        access_if_exists(ctx, app_string)
        access_if_exists(
            ctx,
            "/Applications/Karabiner.app/Contents/Applications/"
            "Karabiner_AXNotifier.app"
        )


def access_if_exists(ctx, app_string):
    if os.path.exists(app_string):
        ctx.run(
            'zsh -c "source ~/.zshrc && '
            'enable_access_for_assistive_devices \"{0}\""'.format(
                app_string
            )
        )

@ctask(aliases=['karabiner', 'fast_repeat'])
def hyper(ctx):
    source = '{0}/karabiner-hyper.xml'.format(util.RESOURCES_DIRECTORY)
    destination_folder = os.path.join(
        os.path.expanduser("~/Library"), "Application\\ Support", "Karabiner"
    )
    destination = os.path.join(destination_folder, "private.xml")
    try:
        ctx.run("rm {0}".format(destination))
    except:
        pass
    util.ensure_path_exists(destination_folder)
    ctx.run("ln -s {0} {1}".format(source, destination))
    ctx.run("{0}/karabiner_config.sh".format(util.RESOURCES_DIRECTORY))


@ctask
def locate(ctx):
    ctx.run('sudo launchctl load -w '
            '/System/Library/LaunchDaemons/com.apple.locate.plist')


@ctask
def rvm(ctx):
    ctx.run('\\curl -sSL https://get.rvm.io | bash -s stable')


@ctask
def fonts(ctx):
    ctx.run('open {0}'.format(
        os.path.join(util.RESOURCES_DIRECTORY, "Monaco-Powerline.otf"))
    )


@ctask
def cl_tools(ctx):
    if not util.command_exists('gcc'):
        ctx.run('xcode-select --install')


@ctask
def fix_htop(ctx):
    real_htop_location = ctx.run("readlink -f $(brew --prefix htop)").stdout.strip() + "/bin/htop"
    ctx.run("sudo chmod 6555 {0}".format(real_htop_location))
    ctx.run("sudo chown root {0}".format(real_htop_location))


@ctask
def iTerm(ctx):
    library_plist = os.path.join(os.path.expanduser("~"), "Library",
                                 "Preferences", "com.googlecode.iterm2.plist")
    ctx.run("defaults write {0} LoadPrefsFromCustomFolder -bool true".format(
        library_plist
    ))
    ctx.run("defaults write {0} PrefsCustomFolder -string {1}".format(
        library_plist, util.RESOURCES_DIRECTORY
    ))


@ctask
def fix_pip(ctx):
    ctx.run("sudo easy_install -U pip")


@ctask
def launch_agents(ctx, flags=''):
    ctx.run('dotfiles -sn{1} -R {0}/resources/LaunchAgents/ '
            '-H ~/Library/LaunchAgents'.format(util.REPO_DIRECTORY, flags))
