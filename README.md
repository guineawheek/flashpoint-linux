# Flashpoint wrapper for Linux

uhhhh yeah i made an apache compilation script, rewrote the redirector, and made a launchbox substitute (or i'm planning to atm)

## Prerequisites:

Python 3.5+ (most distros ship this by now) - used for the proxy script

Wine 3+ - "but but there's a native Linux standalone flashplayer" you may ask. Turns out that running the Windows standalone flashplayer in wine is more reliable than the actual native Linux build. Which kinda sucks. 

## installation

1. Download Flashpoint from the official archive.org source or torrent (TODO: add link), and extract it somewhere.

2. Download and extract this repo with `$ git clone [TODO]`

3. Inside the flashpoint-linux folder, edit `config` with your favorite text editor, and follow the comments in there to specify the path to the Flashpoint downloaded in step 1.

4. Download the required packages to compile Apache and PHP.

On Ubuntu or Debian, it's pretty simple, just run `sudo apt build-dep apache2 php`. Other distros have similar commands.

On Arch, the way I found was to run `sudo pacman -S apache php` then uninstalling them with `sudo pacman -R apache php` if you don't need them systemwide. Hopefully, someone will have the wits to make this a PKGBUILD for the AUR anyway and this won't matter because `makepkg` will do this for you. 


5. in the flashpoint-linux folder, run `$ ./compile.sh` to compile Apache and PHP. 

6. uh i haven't finished the rest yet

