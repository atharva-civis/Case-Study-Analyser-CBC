{pkgs}: {
  deps = [
    pkgs.libiconv
    pkgs.tk
    pkgs.tcl
    pkgs.qhull
    pkgs.pkg-config
    pkgs.freetype
    pkgs.glibcLocales
  ];
}
