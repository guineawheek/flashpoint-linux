# Flashpoint wrapper for Linux

uhhhh yeah i made an apache compilation script, rewrote the redirector, and made a launchbox substitute (or i'm planning to atm)

## Prerequisites:

Python 3.5+ (most distros ship this by now) - used for the proxy script and web ui backend

Also required is Flask for Python, which is the `python3-flask` package on Debian/Ubuntu but may be `python-flask` on other platforms

Wine 3+ - "but but there's a native Linux standalone flashplayer" you may ask. Turns out that running the Windows standalone flashplayer in wine is more reliable than the actual native Linux build. Which kinda sucks. 

`$ sudo apt install python3-flask wine`

## installation

1. Download Flashpoint from the official archive.org source or torrent (TODO: add link), and extract it somewhere.

2. Download and extract this repo with `$ git clone [TODO]`

3. Inside the flashpoint-linux folder, Run `$ ./compile.sh` once to generate `config`. Edit `config` with your favorite text editor, and follow the comments in there to specify the path to the Flashpoint downloaded in step 1.

4. Download the required packages to compile Apache and PHP.

On Ubuntu or Debian, it's pretty simple, just run `sudo apt build-dep apache2 php`. Other distros have similar commands.

On Arch, the way I found was to run `sudo pacman -S apache php` then uninstalling them with `sudo pacman -R apache php` if you don't need them systemwide. Hopefully, someone will have the wits to make this a PKGBUILD for the AUR anyway and this won't matter because `makepkg` will do this for you. 


5. In the flashpoint-linux folder, run `$ ./compile.sh` to compile Apache and PHP. 

## running

1. To start the system, simply run `$ ./run.sh`. All processes will exit when the script is killed with Ctrl-C.

2. To access the interface, go to `http://localhost:5000`. note that there can be a 5-10 second delay (or more) between pressing `Launch Game` and the game actually launching so be patient.

## bugs/things not supported yet

* some games that do funky things might not be supported, but by and large most games will launch, including those relying on PHP
* shockwave is a TODO
* there's no sort by or search beyond ctrl-F ing titles
* all the game boxarts load on the index page all at once which is horribly inefficient and just bad
* no good game process monitoring
* no option to hide "hidden" (nsfw) games

but it will launch most flash games
