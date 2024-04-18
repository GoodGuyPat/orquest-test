with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell rec {
  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib.outPath}/lib:${pkgs.lib.makeLibraryPath buildInputs}:${stdenv.cc.cc.lib}/lib";

  
  name = "impurePythonEnv";
  venvDir = "./orquest_env";
  buildInputs = [
    # A Python interpreter including the 'venv' module is required to bootstrap
    # the environment.
    pythonPackages.python

    # This executes some shell code to initialize a venv in $venvDir before
    # dropping into the shell
    pythonPackages.venvShellHook

    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    # pythonPackages.numpy
    # pythonPackages.requests

    # In this particular example, in order to compile any binary extensions they may
    # require, the Python modules listed in the hypothetical requirements.txt need
    # the following packages to be installed locally:
    libstdcxx5
    bash
    taglib
    openssl
    git
    libxml2
    gnupg
    libxslt
    libzip
    zlib
  ];
  pythonImportsCheckHook = ''
  requests
  '';

  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    pip install -r requirements.txt
  '';

  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
    # allow pip to install wheels
    export DBT_PROFILES_DIR=$(pwd)
  '';

}
