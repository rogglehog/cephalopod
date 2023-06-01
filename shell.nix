with import <nixpkgs> {};

( pkgs.python3.buildEnv.override  {
  extraLibs = with pkgs.python3Packages; [
    sqlalchemy
    requests
    feedparser
    pyyaml
];}).env
